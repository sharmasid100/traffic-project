from datetime import datetime

from pydantic import BaseModel, Field


class JobAccepted(BaseModel):
    job_id: str
    status: str
    duplicated: bool = False


class JobStatus(BaseModel):
    id: str
    status: str
    source_type: str
    camera_id: str
    original_filename: str
    error_message: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ViolationOut(BaseModel):
    id: str
    job_id: str
    camera_id: str
    source_filename: str
    vehicle_type: str
    plate_number: str
    plate_confidence: float
    helmet_violation: bool
    triple_violation: bool
    violation_type: str
    evidence_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class StatsOut(BaseModel):
    total_records: int
    helmet_count: int
    triple_count: int
    unique_vehicles: int
    queued_jobs: int = 0


class HealthOut(BaseModel):
    status: str = "ok"
    service: str = Field(default="traffic-violation-system")
