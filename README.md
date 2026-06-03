# Library API Backend

A modern FastAPI backend structured with SQLAlchemy and Alembic.

## Configuration & Environment Setup

To run the application (both locally and via Docker), a `.env` file is required in the root directory.

### Quick Start: Setup `.env`
1. Copy the example file to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in the values for your environment.

### Available Variables

- **Database Credentials**:
  - `POSTGRES_USER`: Database user (default: `test`).
  - `POSTGRES_PASSWORD`: Database password (default: `test`).
  - `POSTGRES_DB`: Database name (default: `test`).
  - `PG_HOST`: Database host address (e.g. `db` in Docker, `localhost` locally).
  - `PG_PORT`: Database port (default: `5432`).
- **Application Server Settings**:
  - `APP_PORT`: FastAPI listening port (default: `5000`).
- **Application Logic Settings**:
  - `ENVIRONMENT`: Defines database query logging and runtime parameters. Allowed values: `development`, `production`.
  - `TIMEZONE`: Defines the application-wide timezone used for datetimes (e.g., `UTC`, `Europe/Warsaw`).

### Error Handling

The application will fail to start and throw a `RuntimeError` if the `.env` file is not present in either the project root or the current working directory.

When running inside Docker containers, the entrypoint script `entrypoint.sh` will automatically fall back to copying `.env.example` as `.env` if no `.env` file is present (e.g., in CI pipelines), ensuring the service can start using template defaults.

### Maintenance

Run formatter:
```
cd source/backend
uv run ruff format .
```

Run linter:
```
cd source/backend
uv run ruff check . --fix
```

Run migration (in separate container with separated empty volume):
```
cd source/backend
./makemigration.sh {migration name}
```

Run tests:
```
cd source/backend
uv run pytest
```
