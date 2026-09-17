import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    status: Mapped[str] = mapped_column(String(32), default="queued", index=True)
    source_type: Mapped[str] = mapped_column(String(16))
    camera_id: Mapped[str] = mapped_column(String(128), default="default")
    original_filename: Mapped[str] = mapped_column(String(512))
    content_sha256: Mapped[str] = mapped_column(String(64), index=True)
    object_key: Mapped[str] = mapped_column(String(512))
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Violation(Base):
    __tablename__ = "violations"
    __table_args__ = (
        UniqueConstraint(
            "dedup_key",
            name="uq_violations_dedup_key",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    job_id: Mapped[str] = mapped_column(String(36), index=True)
    camera_id: Mapped[str] = mapped_column(String(128), default="default", index=True)
    source_filename: Mapped[str] = mapped_column(String(512))
    vehicle_type: Mapped[str] = mapped_column(String(32), index=True)
    plate_number: Mapped[str] = mapped_column(String(32), index=True)
    plate_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    helmet_violation: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    triple_violation: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    violation_type: Mapped[str] = mapped_column(String(64), index=True)
    evidence_key: Mapped[str] = mapped_column(String(512))
    bbox_x1: Mapped[int] = mapped_column(Integer)
    bbox_y1: Mapped[int] = mapped_column(Integer)
    bbox_x2: Mapped[int] = mapped_column(Integer)
    bbox_y2: Mapped[int] = mapped_column(Integer)
    frame_index: Mapped[int] = mapped_column(Integer, default=0)
    dedup_key: Mapped[str] = mapped_column(String(128), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
