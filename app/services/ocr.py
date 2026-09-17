from __future__ import annotations

import re
from abc import ABC, abstractmethod

import cv2
import numpy as np

from app.config import get_settings


REPLACEMENTS = {"O": "0", "I": "1", "S": "5", "B": "8"}


def preprocess_plate(plate_img: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    gray = cv2.resize(gray, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    return cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )


def clean_plate_number(text: str) -> str:
    text = text.upper().replace(" ", "").replace("-", "")
    text = re.sub(r"[^A-Z0-9]", "", text)
    return "".join(REPLACEMENTS.get(ch, ch) for ch in text)


class OcrBackend(ABC):
    @abstractmethod
    def read_plate(self, plate_crop: np.ndarray) -> tuple[str, float]:
        raise NotImplementedError


class MockOcr(OcrBackend):
    def read_plate(self, plate_crop: np.ndarray) -> tuple[str, float]:
        if plate_crop is None or plate_crop.size == 0:
            return "UNKNOWN", 0.0
        mean = float(np.mean(plate_crop))
        if mean < 40:
            return "UNKNOWN", 0.1
        return "MH12AB1234", 0.91


class EasyOcrBackend(OcrBackend):
    def __init__(self) -> None:
        import easyocr

        self.reader = easyocr.Reader(["en"], gpu=False)

    def read_plate(self, plate_crop: np.ndarray) -> tuple[str, float]:
        processed = preprocess_plate(plate_crop)
        results = self.reader.readtext(processed)
        best_text = "UNKNOWN"
        best_conf = 0.0
        for _, text, conf in results:
            if conf > best_conf:
                best_conf = float(conf)
                best_text = text
        cleaned = clean_plate_number(best_text)
        if not cleaned:
            return "UNKNOWN", best_conf
        return cleaned, best_conf


def build_ocr() -> OcrBackend:
    backend = get_settings().ocr_backend.lower()
    if backend == "easyocr":
        return EasyOcrBackend()
    return MockOcr()
