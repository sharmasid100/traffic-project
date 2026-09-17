from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Violation
from app.services.auth import require_dashboard
from app.services.jobs import stats as load_stats
from app.services.storage import get_storage

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


@router.get("/", response_class=HTMLResponse)
def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    username: str = Depends(require_dashboard),
):
    storage = get_storage()
    rows = db.scalars(select(Violation).order_by(Violation.created_at.desc()).limit(200)).all()
    records = []
    for row in rows:
        records.append(
            {
                "timestamp": row.created_at,
                "vehicle_type": row.vehicle_type,
                "plate_number": row.plate_number,
                "violation_type": row.violation_type,
                "helmet_violation": row.helmet_violation,
                "triple_violation": row.triple_violation,
                "evidence_url": storage.public_url(row.evidence_key) if row.evidence_key else "",
                "camera_id": row.camera_id,
            }
        )
    summary = load_stats(db)
    return templates.TemplateResponse(
        request,
        "index.html",
        {"records": records, **summary, "user": username},
    )
