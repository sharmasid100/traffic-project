import os
import tempfile
from pathlib import Path


def pytest_configure():
    data_dir = Path(tempfile.mkdtemp(prefix="traffic-test-"))
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["QUEUE_BACKEND"] = "inline"
    os.environ["STORAGE_BACKEND"] = "local"
    os.environ["DATA_DIR"] = str(data_dir)
    os.environ["PUBLIC_BASE_URL"] = "http://testserver"
    os.environ["API_KEY"] = "test-key"
    os.environ["DASHBOARD_USER"] = "admin"
    os.environ["DASHBOARD_PASSWORD"] = "test-pass"
    os.environ["DETECTOR_BACKEND"] = "mock"
    os.environ["OCR_BACKEND"] = "mock"
    os.environ["APP_ENV"] = "test"
