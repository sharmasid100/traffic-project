from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from app.services.detectors import Detection, DetectorBackend
from app.services.evidence import annotate_evidence, encode_jpeg
from app.services.ocr import OcrBackend


MOTORCYCLE_LABELS = {"motorcycle", "motorbike", "bike"}


@dataclass
class ViolationCandidate:
    vehicle_type: str
    plate_number: str
    plate_confidence: float
    helmet_violation: bool
    triple_violation: bool
    violation_type: str
    bbox: tuple[int, int, int, int]
    evidence_bytes: bytes
    frame_index: int
    evidence_key: str = ""


def crop(image: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    x1, y1, x2, y2 = bbox
    h, w = image.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    return image[y1:y2, x1:x2]


def violation_label(helmet: bool, triple: bool) -> str:
    if helmet and triple:
        return "Helmet + Triple Riding"
    if helmet:
        return "Helmet"
    if triple:
        return "Triple Riding"
    return "Unknown"


def check_helmet_violation(detector: DetectorBackend, motorcycle_crop: np.ndarray) -> bool:
    for item in detector.detect_helmet(motorcycle_crop):
        if item.label.lower().replace("_", " ") in {"without helmet", "no helmet"}:
            return True
    return False


def check_triple_riding(detector: DetectorBackend, motorcycle_crop: np.ndarray) -> bool:
    detections = detector.detect_riders(motorcycle_crop)
    if not detections:
        return False
    best = max(detections, key=lambda item: item.confidence)
    return best.label.lower().replace(" ", "_") in {"triple_rider", "triple"}


def detect_best_plate(detector: DetectorBackend, motorcycle_crop: np.ndarray) -> Detection | None:
    plates = detector.detect_plates(motorcycle_crop)
    if not plates:
        return None
    return max(
        plates,
        key=lambda item: (item.bbox[2] - item.bbox[0]) * (item.bbox[3] - item.bbox[1]),
    )


def process_frame(
    image: np.ndarray,
    detector: DetectorBackend,
    ocr: OcrBackend,
    frame_index: int = 0,
) -> list[ViolationCandidate]:
    candidates: list[ViolationCandidate] = []
    vehicles = detector.detect_vehicles(image)
    for vehicle in vehicles:
        if vehicle.label.lower() not in MOTORCYCLE_LABELS:
            continue
        motorcycle_crop = crop(image, vehicle.bbox)
        if motorcycle_crop.size == 0:
            continue
        helmet = check_helmet_violation(detector, motorcycle_crop)
        triple = check_triple_riding(detector, motorcycle_crop)
        if not (helmet or triple):
            continue
        plate_number = "UNKNOWN"
        plate_confidence = 0.0
        plate = detect_best_plate(detector, motorcycle_crop)
        if plate is not None:
            plate_crop = crop(motorcycle_crop, plate.bbox)
            if plate_crop.size:
                plate_number, plate_confidence = ocr.read_plate(plate_crop)
                if not plate_number:
                    plate_number = "UNKNOWN"
        evidence = annotate_evidence(image, vehicle.bbox, plate_number, helmet, triple)
        candidates.append(
            ViolationCandidate(
                vehicle_type="motorcycle",
                plate_number=plate_number,
                plate_confidence=plate_confidence,
                helmet_violation=helmet,
                triple_violation=triple,
                violation_type=violation_label(helmet, triple),
                bbox=vehicle.bbox,
                evidence_bytes=encode_jpeg(evidence),
                frame_index=frame_index,
            )
        )
    return candidates


def iter_video_frames(video_bytes: bytes, stride: int):
    path = "/tmp/traffic_input.mp4"
    with open(path, "wb") as handle:
        handle.write(video_bytes)
    capture = cv2.VideoCapture(path)
    index = 0
    while True:
        ok, frame = capture.read()
        if not ok:
            break
        if index % stride == 0:
            yield index, frame
        index += 1
    capture.release()
