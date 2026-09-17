from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from app.config import get_settings


@dataclass
class Detection:
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]


class DetectorBackend(ABC):
    @abstractmethod
    def detect_vehicles(self, image: np.ndarray) -> list[Detection]:
        raise NotImplementedError

    @abstractmethod
    def detect_helmet(self, crop: np.ndarray) -> list[Detection]:
        raise NotImplementedError

    @abstractmethod
    def detect_riders(self, crop: np.ndarray) -> list[Detection]:
        raise NotImplementedError

    @abstractmethod
    def detect_plates(self, crop: np.ndarray) -> list[Detection]:
        raise NotImplementedError


class MockDetector(DetectorBackend):
    """Deterministic demo detector so the stack runs without GPU weights."""

    def detect_vehicles(self, image: np.ndarray) -> list[Detection]:
        h, w = image.shape[:2]
        return [
            Detection("motorcycle", 0.92, (int(w * 0.2), int(h * 0.2), int(w * 0.8), int(h * 0.9)))
        ]

    def detect_helmet(self, crop: np.ndarray) -> list[Detection]:
        h, w = crop.shape[:2]
        return [Detection("Without Helmet", 0.88, (int(w * 0.3), 0, int(w * 0.7), int(h * 0.3)))]

    def detect_riders(self, crop: np.ndarray) -> list[Detection]:
        h, w = crop.shape[:2]
        return [Detection("triple_rider", 0.81, (0, 0, w, h))]

    def detect_plates(self, crop: np.ndarray) -> list[Detection]:
        h, w = crop.shape[:2]
        y1, y2 = int(h * 0.7), int(h * 0.95)
        x1, x2 = int(w * 0.25), int(w * 0.75)
        return [Detection("license_plate", 0.9, (x1, y1, x2, y2))]


class YoloDetector(DetectorBackend):
    def __init__(self) -> None:
        from ultralytics import YOLO

        settings = get_settings()
        model_dir = Path(settings.model_dir)
        self.threshold = settings.confidence_threshold
        self.vehicle = YOLO(str(model_dir / "vehicle_weights.pt"))
        self.helmet = YOLO(str(model_dir / "helmet_weights.pt"))
        self.triple = YOLO(str(model_dir / "triple_weights.pt"))
        self.plate = YOLO(str(model_dir / "license_weights.pt"))

    def _run(self, model, image: np.ndarray) -> list[Detection]:
        results = model(image, verbose=False, conf=self.threshold)
        detections: list[Detection] = []
        for box in results[0].boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append(
                Detection(
                    label=model.names[cls],
                    confidence=float(box.conf[0]),
                    bbox=(x1, y1, x2, y2),
                )
            )
        return detections

    def detect_vehicles(self, image: np.ndarray) -> list[Detection]:
        return self._run(self.vehicle, image)

    def detect_helmet(self, crop: np.ndarray) -> list[Detection]:
        return self._run(self.helmet, crop)

    def detect_riders(self, crop: np.ndarray) -> list[Detection]:
        return self._run(self.triple, crop)

    def detect_plates(self, crop: np.ndarray) -> list[Detection]:
        return self._run(self.plate, crop)


def build_detector() -> DetectorBackend:
    backend = get_settings().detector_backend.lower()
    if backend == "yolo":
        return YoloDetector()
    return MockDetector()
