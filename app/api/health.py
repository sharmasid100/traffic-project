from fastapi import APIRouter
from sqlalchemy import text

from app.db import get_engine
from app.schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    return HealthOut()


@router.get("/ready")
def ready() -> dict:
    with get_engine().connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ready"}
