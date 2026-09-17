#!/bin/sh
set -eu
mkdir -p "${DATA_DIR:-/data}"
if echo "${DATABASE_URL:-}" | grep -q "postgresql"; then
  alembic upgrade head
fi
exec "$@"
