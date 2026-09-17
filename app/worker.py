from __future__ import annotations

import cv2
import numpy as np
import structlog

from app.config import get_settings
from app.db import SessionLocal
from app.logging import configure_logging
from app.models import Job
from app.services.detectors import build_detector
from app.services.jobs import persist_violations
from app.services.ocr import build_ocr
from app.services.pipeline import iter_video_frames, process_frame
from app.services.storage import get_storage

logger = structlog.get_logger()
_detector = None
_ocr = None


def _backends():
    global _detector, _ocr
    if _detector is None:
        _detector = build_detector()
    if _ocr is None:
        _ocr = build_ocr()
    return _detector, _ocr


def process_job(job_id: str) -> dict:
    settings = get_settings()
    storage = get_storage()
    detector, ocr = _backends()
    db = SessionLocal()
    job = db.get(Job, job_id)
    if job is None:
        return {"error": "job_not_found", "job_id": job_id}
    job.status = "running"
    db.commit()
    try:
        payload = storage.get_bytes(job.object_key)
        if job.source_type == "image":
            array = np.frombuffer(payload, dtype=np.uint8)
            image = cv2.imdecode(array, cv2.IMREAD_COLOR)
            if image is None:
                raise ValueError("Unable to decode image")
            frames = [(0, image)]
        else:
            frames = list(iter_video_frames(payload, settings.video_frame_stride))

        candidates = []
        for frame_index, frame in frames:
            for candidate in process_frame(frame, detector, ocr, frame_index=frame_index):
                slug = candidate.violation_type.replace(" ", "_")
                key = f"evidence/{job.id}/{frame_index}_{slug}.jpg"
                storage.put_bytes(key, candidate.evidence_bytes, "image/jpeg")
                candidate.evidence_key = key
                candidates.append(candidate)
        stored = persist_violations(db, job, candidates)
        job.status = "completed"
        db.commit()
        logger.info("job_completed", job_id=job.id, stored=stored, candidates=len(candidates))
        return {"job_id": job.id, "stored": stored}
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
        db.commit()
        logger.exception("job_failed", job_id=job_id)
        raise
    finally:
        db.close()


def enqueue_redis(job_id: str) -> None:
    import redis
    from rq import Queue

    settings = get_settings()
    connection = redis.from_url(settings.redis_url)
    Queue("traffic", connection=connection, default_timeout=settings.job_timeout_seconds).enqueue(
        process_job, job_id, job_id=f"traffic-{job_id}"
    )


def main() -> None:
    import redis
    from rq import Queue, Worker

    settings = get_settings()
    configure_logging(settings.log_level)
    connection = redis.from_url(settings.redis_url)
    Worker([Queue("traffic", connection=connection)], connection=connection).work()


if __name__ == "__main__":
    main()
