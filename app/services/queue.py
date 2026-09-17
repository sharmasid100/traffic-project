from app.config import get_settings


def enqueue_processing(job_id: str) -> None:
    settings = get_settings()
    if settings.queue_backend.lower() == "redis":
        from app.worker import enqueue_redis

        enqueue_redis(job_id)
        return
    from app.worker import process_job

    process_job(job_id)
