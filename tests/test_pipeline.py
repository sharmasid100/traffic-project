import numpy as np

from app.services.detectors import MockDetector
from app.services.ocr import MockOcr
from app.services.pipeline import process_frame, violation_label


def test_violation_label():
    assert violation_label(True, True) == "Helmet + Triple Riding"
    assert violation_label(True, False) == "Helmet"
    assert violation_label(False, True) == "Triple Riding"


def test_mock_pipeline_emits_motorcycle_violation():
    image = np.zeros((480, 640, 3), dtype=np.uint8)
    image[:] = (40, 40, 40)
    results = process_frame(image, MockDetector(), MockOcr())
    assert len(results) == 1
    item = results[0]
    assert item.vehicle_type == "motorcycle"
    assert item.helmet_violation is True
    assert item.triple_violation is True
    assert item.plate_number == "MH12AB1234"
    assert item.evidence_bytes.startswith(b"\xff\xd8")
