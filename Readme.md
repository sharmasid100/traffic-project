# Automated Traffic Violation Detection System

GitHub-ready production service for the same computer-vision workflow as
[sharmasid100/traffic-project](https://github.com/sharmasid100/traffic-project):

detect vehicles → motorcycle crop → helmet + triple-riding checks → license-plate OCR → annotated evidence → dashboard.

[![CI](https://github.com/sharmasid100/traffic-violation-system/actions/workflows/ci.yml/badge.svg)](https://github.com/sharmasid100/traffic-violation-system/actions/workflows/ci.yml)

## What you get

- FastAPI ingest API (`X-API-Key`) and operator dashboard (HTTP Basic)
- Redis + RQ workers for async image/video jobs
- PostgreSQL for jobs and violations (Alembic migrations)
- Local object storage (shared Docker volume); optional S3/MinIO
- Mock detector/OCR so the stack is fully runnable without GPU weights
- GitHub Actions CI + GHCR image publish

## Quick start

```bash
docker compose up --build
```

- API / dashboard: http://localhost:8000
- Health: http://localhost:8000/health
- Dashboard login: `admin` / `change-me`

Ingest a sample frame:

```bash
curl -X POST http://localhost:8000/v1/jobs/images \
  -H "X-API-Key: change-me" \
  -F camera_id=cam-junction-1 \
  -F file=@samples/traffic_frame.bmp
```

Then refresh the dashboard. Mock models always emit a helmet + triple-riding hit so you can verify the full path.

## Local tests

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Configuration

Copy `.env.example` if you want a dotenv file. Compose already has working defaults.

| Variable | Default | Purpose |
| --- | --- | --- |
| `API_KEY` | `change-me` | Ingest/query API |
| `QUEUE_BACKEND` | `redis` in Compose, `inline` in tests | `redis` or `inline` |
| `STORAGE_BACKEND` | `local` | `local` or `s3` |
| `DETECTOR_BACKEND` | `mock` | `mock` or `yolo` |
| `OCR_BACKEND` | `mock` | `mock` or `easyocr` |

## Layout

```text
app/                  API, worker, detection pipeline
alembic/              Postgres schema
samples/              Demo traffic frame
.github/workflows/    CI and GHCR publish
docker-compose.yml    Postgres + Redis + API + worker
```

See [DEPLOY.md](DEPLOY.md) for GitHub and production hosting.
