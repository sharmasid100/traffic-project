Place YOLOv8 weights here when running with DETECTOR_BACKEND=yolo:

- vehicle_weights.pt
- helmet_weights.pt
- triple_weights.pt
- license_weights.pt

Download with `bash scripts/download_models.sh`.
The default Docker compose stack uses DETECTOR_BACKEND=mock so it boots without GPU weights.
