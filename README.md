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

### Build docker
```bash
docker compose build
```

### Run App
```bash
docker compose up
# or detach:
docker compose up -d
```

### Stop App

### Error Handling

The application will fail to start and throw a `RuntimeError` if the `.env` file is not present in either the project root or the current working directory.

When running inside Docker containers, the entrypoint script `entrypoint.sh` will automatically fall back to copying `.env.example` as `.env` if no `.env` file is present (e.g., in CI pipelines), ensuring the service can start using template defaults.

### Maintenance

Run formatter:
```bash
cd source/backend
uv run ruff format .
```

Run linter:
```bash
cd source/backend
uv run ruff check . --fix
```

Run migration (in separate container with separated empty volume):
```bash
cd source/backend
./makemigration.sh {migration name}
```

Run tests:
```bash
cd source/backend
# Unit tests only (fast, no DB needed)
uv run pytest app/tests/unit/ -v

# Integration tests (requires Docker for testcontainers)
uv run pytest app/tests/integration/ -v

# All tests
uv run pytest
```

---

### CI/CD

This project uses **GitHub Actions** for continuous integration. The pipeline is defined in [`.github/workflows/ci.yml`](.github/workflows/ci.yml) and runs on every push/PR to `main`/`master`.

| Job | Runs | Requires |
|-----|------|----------|
| **Lint & Format** | `ruff format --check` + `ruff check` | — |
| **Unit Tests** | `pytest app/tests/unit/` | — |
| **Integration Tests** | `pytest app/tests/integration/` | Lint & Unit pass first |

The lint/format and unit test jobs run **in parallel**. Integration tests only start after both pass.

---

### Git Hooks

A `pre-commit` hook is included in the [`hooks/`](hooks/) directory. It runs the formatter check, linter, and unit tests **before each commit**, preventing broken code from entering the repository.

#### Setup (one-time)

Point Git to the `hooks/` directory:

```bash
git config core.hooksPath hooks
```

That's it — the `pre-commit` hook will now run automatically on every `git commit`.

#### What it checks

1. `ruff format --check` — code formatting
2. `ruff check` — linting rules
3. `pytest app/tests/unit/ -q` — unit tests (~1s)

If any check fails, the commit is rejected. Fix the issues and try again.

#### Skip (emergency only)

```bash
git commit --no-verify -m "message"
```

