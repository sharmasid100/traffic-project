#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$ROOT/models"
mkdir -p "$DEST"
BASE="https://raw.githubusercontent.com/sharmasid100/traffic-project/main/models"
for name in vehicle_weights.pt helmet_weights.pt triple_weights.pt license_weights.pt; do
  echo "Downloading $name"
  curl -L "$BASE/$name" -o "$DEST/$name"
done
echo "Models saved to $DEST"
echo "Set DETECTOR_BACKEND=yolo and OCR_BACKEND=easyocr, then reinstall with: pip install '.[ml]'"
