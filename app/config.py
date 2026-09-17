from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "production"
    app_name: str = "traffic-violation-system"
    log_level: str = "INFO"
    api_key: str = "change-me"
    dashboard_user: str = "admin"
    dashboard_password: str = "change-me"

    database_url: str = "sqlite:///./data/traffic.db"
    redis_url: str = "redis://localhost:6379/0"
    queue_backend: str = "inline"
    storage_backend: str = "local"
    data_dir: str = "data"
    public_base_url: str = "http://localhost:8000"

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "traffic-evidence"
    s3_region: str = "us-east-1"

    detector_backend: str = "mock"
    ocr_backend: str = "mock"
    model_dir: str = "models"
    confidence_threshold: float = 0.35
    video_frame_stride: int = 15
    dedup_window_seconds: int = 300
    job_timeout_seconds: int = 180
    max_upload_mb: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()
