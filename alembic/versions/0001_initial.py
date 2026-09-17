"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-09-16
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "jobs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("source_type", sa.String(length=16), nullable=False),
        sa.Column("camera_id", sa.String(length=128), nullable=False),
        sa.Column("original_filename", sa.String(length=512), nullable=False),
        sa.Column("content_sha256", sa.String(length=64), nullable=False),
        sa.Column("object_key", sa.String(length=512), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"])
    op.create_index("ix_jobs_content_sha256", "jobs", ["content_sha256"])
    op.create_table(
        "violations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("camera_id", sa.String(length=128), nullable=False),
        sa.Column("source_filename", sa.String(length=512), nullable=False),
        sa.Column("vehicle_type", sa.String(length=32), nullable=False),
        sa.Column("plate_number", sa.String(length=32), nullable=False),
        sa.Column("plate_confidence", sa.Float(), nullable=False),
        sa.Column("helmet_violation", sa.Boolean(), nullable=False),
        sa.Column("triple_violation", sa.Boolean(), nullable=False),
        sa.Column("violation_type", sa.String(length=64), nullable=False),
        sa.Column("evidence_key", sa.String(length=512), nullable=False),
        sa.Column("bbox_x1", sa.Integer(), nullable=False),
        sa.Column("bbox_y1", sa.Integer(), nullable=False),
        sa.Column("bbox_x2", sa.Integer(), nullable=False),
        sa.Column("bbox_y2", sa.Integer(), nullable=False),
        sa.Column("frame_index", sa.Integer(), nullable=False),
        sa.Column("dedup_key", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("dedup_key", name="uq_violations_dedup_key"),
    )
    op.create_index("ix_violations_job_id", "violations", ["job_id"])
    op.create_index("ix_violations_plate_number", "violations", ["plate_number"])
    op.create_index("ix_violations_created_at", "violations", ["created_at"])


def downgrade() -> None:
    op.drop_table("violations")
    op.drop_table("jobs")
