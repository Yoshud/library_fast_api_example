from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Create async engine
engine = create_async_engine(
    settings.database_url,
    # TODO: add this as some env value
    echo=True,  # Set to False in production
)

# Expire on commit = False gives as possibility to get id of data after saving object without race condition
# In Postgres and others engine with RETURNING it will work with one query. In MySQL it will actually run 2 queries
# underneath but without race condition possible. Tradeoff is potentially stale data in longer session which is
# unlikely for short liven - one query typical fastAPI sessions
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)
