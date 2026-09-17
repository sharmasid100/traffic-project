from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Violation
from app.schemas import StatsOut, ViolationOut
from app.services.auth import require_api_key
from app.services.jobs import stats as load_stats
from app.services.storage import get_storage

router = APIRouter(prefix="/v1", tags=["violations"], dependencies=[Depends(require_api_key)])


@router.get("/violations", response_model=list[ViolationOut])
def list_violations(
    limit: int = Query(50, ge=1, le=500),
    plate_number: str | None = None,
    db: Session = Depends(get_db),
) -> list[ViolationOut]:
    storage = get_storage()
    query = select(Violation).order_by(Violation.created_at.desc()).limit(limit)
    if plate_number:
        query = query.where(Violation.plate_number == plate_number)
    rows = db.scalars(query).all()
    return [
        ViolationOut(
            id=row.id,
            job_id=row.job_id,
            camera_id=row.camera_id,
            source_filename=row.source_filename,
            vehicle_type=row.vehicle_type,
            plate_number=row.plate_number,
            plate_confidence=row.plate_confidence,
            helmet_violation=row.helmet_violation,
            triple_violation=row.triple_violation,
            violation_type=row.violation_type,
            evidence_url=storage.public_url(row.evidence_key) if row.evidence_key else "",
            created_at=row.created_at,
        )
        for row in rows
    ]


@router.get("/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)) -> StatsOut:
    return StatsOut(**load_stats(db))
