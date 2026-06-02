FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /source

# Copy python project configuration files first for optimal docker layer caching - needed for uv sync
COPY source/backend/pyproject.toml source/backend/uv.lock source/backend/.python-version source/backend/alembic.ini  ./

# Install dependencies (without installing the project package itself)
RUN uv sync --frozen --no-install-project --no-dev

# Copy the application code
COPY source/backend/app ./app
COPY source/backend/migrations ./migrations

COPY source/backend/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port 5000 to match docker-compose configuration
EXPOSE 5000

ENTRYPOINT ["/entrypoint.sh"]
