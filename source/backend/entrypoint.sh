#!/bin/sh
set -e


# Ensure .env exists in the application directory before starting
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    echo "No .env file found. Copying .env.example to .env..."
    cp .env.example .env
  else
    echo "CRITICAL: Neither .env nor .env.example found in the working directory!"
    exit 1
  fi
fi

echo "Running database migrations..."
uv run --no-sync alembic upgrade head

# With exec uv will receive
echo "Starting FastAPI..."
exec uv run fastapi run app/main.py --host 0.0.0.0 --port 5000
