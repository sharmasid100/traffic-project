import cv2
import numpy as np


def annotate_evidence(
    image: np.ndarray,
    bbox: tuple[int, int, int, int],
    plate_number: str,
    helmet_violation: bool,
    triple_violation: bool,
) -> np.ndarray:
    evidence = image.copy()
    x1, y1, x2, y2 = bbox
    cv2.rectangle(evidence, (x1, y1), (x2, y2), (0, 255, 0), 2)
    tags = []
    if helmet_violation:
        tags.append("helmet")
    if triple_violation:
        tags.append("triple")
    label = f"Plate:{plate_number} | {'_'.join(tags) or 'none'}"
    cv2.putText(
        evidence,
        label,
        (x1, max(30, y1 - 10)),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (0, 0, 255),
        2,
    )
    return evidence


def encode_jpeg(image: np.ndarray) -> bytes:
    ok, buffer = cv2.imencode(".jpg", image)
    if not ok:
        raise ValueError("Failed to encode evidence image")
    return buffer.tobytes()
