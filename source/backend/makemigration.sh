#!/bin/bash
set -e

# 1. Validate input argument
if [ -z "$1" ]; then
    echo "Error: Please provide a migration message."
    echo "Usage: ./makemigration.sh 'migration_message'"
    exit 1
fi

MIGRATION_MSG=$1
CONTAINER_NAME="alembic_ephemeral_db_$(date +%s)"

# 2. Define the cleanup function
cleanup() {
    echo "Cleaning up: tearing down temporary database container..."
    docker rm -f "$CONTAINER_NAME" > /dev/null 2>&1
}
trap cleanup EXIT

echo "Starting an isolated, ephemeral database instance..."
# Launched without volumes (-v), ensuring 100% isolation from dev data
docker run --name "$CONTAINER_NAME" -d -p 127.0.0.1:0:5432 \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test \
  -e POSTGRES_DB=test \
  postgres:16-alpine > /dev/null

# Extract the dynamically assigned random port
DB_PORT=$(docker port "$CONTAINER_NAME" 5432 | sed 's/.*://')
echo "Isolated database is up on localhost:$DB_PORT"

# 3. Wait for PostgreSQL to become fully ready
echo "Waiting for database readiness check..."
until docker exec "$CONTAINER_NAME" pg_isready -U test -d test > /dev/null 2>&1; do
    sleep 0.2
done

# 4. Bring the ephemeral database state up to match existing migrations
echo "Applying existing migrations to the ephemeral database..."
PG_HOST=localhost PG_PORT="$DB_PORT" uv run alembic upgrade head

# 5. Generate the new migration based on changes made since the last upgrade
echo "Generating new Alembic migration script..."
PG_HOST=localhost PG_PORT="$DB_PORT" uv run alembic revision --autogenerate -m "$MIGRATION_MSG"

echo "Success! Migration file generated dynamically without conflicting with local stack."