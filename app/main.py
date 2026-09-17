from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.dashboard import router as dashboard_router
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api.media import router as media_router
from app.api.violations import router as violations_router
from app.config import get_settings
from app.logging import configure_logging

ROOT = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings = get_settings()
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    if settings.database_url.startswith("sqlite"):
        from app import models  # noqa: F401
        from app.db import Base, get_engine

        Base.metadata.create_all(get_engine())
    yield


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title="Traffic Violation System",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(health_router)
app.include_router(media_router)
app.include_router(ingest_router)
app.include_router(violations_router)
app.include_router(dashboard_router)
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
