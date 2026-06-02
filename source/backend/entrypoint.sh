#!/bin/sh
set -e


echo "Running database migrations..."
uv run --no-sync alembic upgrade head

# With exec uv will receive
echo "Starting FastAPI..."
exec uv run fastapi run app/main.py --host 0.0.0.0 --port 5000
