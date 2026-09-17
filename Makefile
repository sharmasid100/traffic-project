.PHONY: up down test smoke

up:
	docker compose up --build

down:
	docker compose down -v

test:
	python -m pytest -q

smoke:
	curl -fsS http://localhost:8000/health
	curl -fsS -X POST http://localhost:8000/v1/jobs/images \
	  -H "X-API-Key: $${API_KEY:-change-me}" \
	  -F camera_id=cam-1 \
	  -F file=@samples/traffic_frame.bmp
