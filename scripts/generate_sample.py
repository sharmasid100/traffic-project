from pathlib import Path

import cv2
import numpy as np

root = Path(__file__).resolve().parents[1]
out = root / "samples"
out.mkdir(exist_ok=True)
image = np.zeros((480, 640, 3), dtype=np.uint8)
image[:] = (30, 30, 30)
cv2.rectangle(image, (120, 80), (520, 430), (80, 80, 80), -1)
cv2.rectangle(image, (240, 360), (400, 420), (220, 220, 220), -1)
cv2.putText(image, "MH12AB1234", (250, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
cv2.imwrite(str(out / "traffic_frame.jpg"), image)
print(out / "traffic_frame.jpg")
