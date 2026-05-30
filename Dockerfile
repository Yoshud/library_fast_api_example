FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /source

RUN uv sync --frozen --no-install-project --no-dev
COPY source/* .


#EXPOSE 5000
CMD ["uv", "run", "fastapi", "dev"]