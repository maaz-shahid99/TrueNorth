#!/usr/bin/env sh
# Apply database migrations, then run the container's command (uvicorn by default).
set -e

echo "Running database migrations (alembic upgrade head)..."
alembic upgrade head

exec "$@"
