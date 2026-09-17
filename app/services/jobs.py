from __future__ import annotations

import hashlib
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Job, Violation
from app.services.pipeline import ViolationCandidate


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def make_dedup_key(
    camera_id: str,
    plate_number: str,
    violation_type: str,
    created_at: datetime,
    window_seconds: int,
) -> str:
    bucket = int(created_at.timestamp() // window_seconds)
    return f"{camera_id}:{plate_number}:{violation_type}:{bucket}"


def enqueue_job(
    db: Session,
    *,
    source_type: str,
    camera_id: str,
    filename: str,
    content_sha256: str,
    object_key: str,
) -> tuple[Job, bool]:
    existing = db.scalar(
        select(Job).where(Job.content_sha256 == content_sha256, Job.camera_id == camera_id)
    )
    if existing and existing.status in {"queued", "running", "completed"}:
        return existing, True
    job = Job(
        source_type=source_type,
        camera_id=camera_id,
        original_filename=filename,
        content_sha256=content_sha256,
        object_key=object_key,
        status="queued",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job, False


def persist_violations(db: Session, job: Job, candidates: list[ViolationCandidate]) -> int:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    stored = 0
    for candidate in candidates:
        key = make_dedup_key(
            job.camera_id,
            candidate.plate_number,
            candidate.violation_type,
            now,
            settings.dedup_window_seconds,
        )
        already = db.scalar(select(Violation).where(Violation.dedup_key == key))
        if already:
            continue
        db.add(
            Violation(
                job_id=job.id,
                camera_id=job.camera_id,
                source_filename=job.original_filename,
                vehicle_type=candidate.vehicle_type,
                plate_number=candidate.plate_number,
                plate_confidence=candidate.plate_confidence,
                helmet_violation=candidate.helmet_violation,
                triple_violation=candidate.triple_violation,
                violation_type=candidate.violation_type,
                evidence_key=candidate.evidence_key,
                bbox_x1=candidate.bbox[0],
                bbox_y1=candidate.bbox[1],
                bbox_x2=candidate.bbox[2],
                bbox_y2=candidate.bbox[3],
                frame_index=candidate.frame_index,
                dedup_key=key,
            )
        )
        stored += 1
    db.commit()
    return stored


def stats(db: Session) -> dict:
    total = db.scalar(select(func.count(Violation.id))) or 0
    helmet = db.scalar(select(func.count(Violation.id)).where(Violation.helmet_violation.is_(True))) or 0
    triple = db.scalar(select(func.count(Violation.id)).where(Violation.triple_violation.is_(True))) or 0
    unique = db.scalar(
        select(func.count(func.distinct(Violation.plate_number))).where(Violation.plate_number != "UNKNOWN")
    ) or 0
    queued = db.scalar(select(func.count(Job.id)).where(Job.status.in_(["queued", "running"]))) or 0
    return {
        "total_records": total,
        "helmet_count": helmet,
        "triple_count": triple,
        "unique_vehicles": unique,
        "queued_jobs": queued,
    }
