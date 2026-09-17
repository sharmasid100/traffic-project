# Deploy

## GitHub

1. Create an empty GitHub repository.
2. Push this project:

```bash
git remote add origin git@github.com:<you>/traffic-violation-system.git
git branch -M main
git push -u origin main
```

3. GitHub Actions will run tests and build the Docker image on every push.
4. The publish workflow pushes `ghcr.io/<you>/traffic-violation-system` on `main`.
   Enable package write access for Actions if the first publish is denied.

## VPS / any Docker host

```bash
export API_KEY=... DASHBOARD_PASSWORD=...
docker compose up --build -d
curl -f http://localhost:8000/health
```

Put a reverse proxy (Caddy/Nginx) in front of port 8000 and set `PUBLIC_BASE_URL` to the public HTTPS origin.

## GitHub Container Registry

```bash
docker pull ghcr.io/<you>/traffic-violation-system:latest
# then point docker-compose.yml image: to that tag and drop build:
```

## Real YOLO models

```bash
bash scripts/download_models.sh
export DETECTOR_BACKEND=yolo OCR_BACKEND=easyocr
docker compose up --build -d
```

Install ML extras in the image if you switch off mock (rebuild after adding `pip install '.[ml]'` in the Dockerfile).
