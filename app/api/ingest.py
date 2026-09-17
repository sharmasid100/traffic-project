from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import Job
from app.schemas import JobAccepted, JobStatus
from app.services.auth import require_api_key
from app.services.jobs import enqueue_job, sha256
from app.services.queue import enqueue_processing
from app.services.storage import get_storage

router = APIRouter(prefix="/v1", tags=["ingest"], dependencies=[Depends(require_api_key)])


def _accept(db: Session, upload: UploadFile, camera_id: str, source_type: str) -> JobAccepted:
    settings = get_settings()
    payload = upload.file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(payload) > max_bytes:
        raise HTTPException(status_code=413, detail="File too large")
    digest = sha256(payload)
    filename = upload.filename or "upload.bin"
    object_key = f"uploads/{camera_id}/{digest}/{filename}"
    get_storage().put_bytes(object_key, payload, upload.content_type or "application/octet-stream")
    job, duplicated = enqueue_job(
        db,
        source_type=source_type,
        camera_id=camera_id,
        filename=filename,
        content_sha256=digest,
        object_key=object_key,
    )
    if not duplicated:
        enqueue_processing(job.id)
        db.refresh(job)
    return JobAccepted(job_id=job.id, status=job.status, duplicated=duplicated)


@router.post("/jobs/images", response_model=JobAccepted)
def ingest_image(
    file: UploadFile = File(...),
    camera_id: str = Form("default"),
    db: Session = Depends(get_db),
) -> JobAccepted:
    return _accept(db, file, camera_id, "image")


@router.post("/jobs/videos", response_model=JobAccepted)
def ingest_video(
    file: UploadFile = File(...),
    camera_id: str = Form("default"),
    db: Session = Depends(get_db),
) -> JobAccepted:
    return _accept(db, file, camera_id, "video")


@router.get("/jobs/{job_id}", response_model=JobStatus)
def job_status(job_id: str, db: Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
