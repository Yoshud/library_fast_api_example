import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command
from sqlalchemy import NullPool

from app.main import app
from app.api.deps import get_db


@pytest.fixture(scope="session")
def postgres_container():
    """Spin up a PostgreSQL container once per test session."""
    with PostgresContainer("postgres:16-alpine") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def db_engine(postgres_container):
    """Run migrations synchronously, then yield an async engine for the session."""
    sync_url = postgres_container.get_connection_url()

    # Apply Alembic migrations using a temporary synchronous connection
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

    sync_engine = create_engine(sync_url)
    with sync_engine.begin() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
    sync_engine.dispose()

    # Strip the default sync driver and enforce the asyncpg driver
    url_body = sync_url.split("://")[1]
    async_url = f"postgresql+asyncpg://{url_body}"

    async_engine = create_async_engine(async_url, pool_pre_ping=True, poolclass=NullPool)
    yield async_engine

    # Ensure the async engine is gracefully disposed of during session teardown
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    loop.run_until_complete(async_engine.dispose())


@pytest.fixture(scope="function")
async def db_session(db_engine):
    """Provide an isolated AsyncSession wrapped in a rolled-back transaction."""
    connection = await db_engine.connect()
    transaction = await connection.begin()

    session = AsyncSession(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint"
    )
    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest.fixture(scope="function")
async def client(db_session):
    """Provide an AsyncClient with overridden database dependencies for API testing."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
