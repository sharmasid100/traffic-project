from pathlib import Path

from fastapi.testclient import TestClient

from app import models  # noqa: F401
from app.config import get_settings
from app.db import Base, get_engine, get_session_factory
from app.main import app
from app.services.storage import get_storage


def _client() -> TestClient:
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    get_storage.cache_clear()
    Base.metadata.create_all(get_engine())
    return TestClient(app)


def test_health():
    with _client() as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_ingest_image_creates_violation():
    sample = Path(__file__).resolve().parents[1] / "samples" / "traffic_frame.bmp"
    with _client() as client:
        with sample.open("rb") as handle:
            response = client.post(
                "/v1/jobs/images",
                headers={"X-API-Key": "test-key"},
                files={"file": ("traffic_frame.bmp", handle, "image/bmp")},
                data={"camera_id": "cam-1"},
            )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["duplicated"] is False
        assert body["status"] == "completed"

        stats = client.get("/v1/stats", headers={"X-API-Key": "test-key"})
        assert stats.status_code == 200
        assert stats.json()["total_records"] == 1
        assert stats.json()["helmet_count"] == 1

        violations = client.get("/v1/violations", headers={"X-API-Key": "test-key"})
        assert violations.status_code == 200
        row = violations.json()[0]
        assert row["plate_number"] == "MH12AB1234"
        assert row["violation_type"] == "Helmet + Triple Riding"
        evidence = client.get(row["evidence_url"].replace("http://testserver", ""))
        assert evidence.status_code == 200
        assert evidence.content[:2] == b"\xff\xd8"
