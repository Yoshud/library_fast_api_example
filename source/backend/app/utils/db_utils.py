from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def optional_transaction(db: AsyncSession):
    # If transaction is not open - open new
    if not db.in_transaction():
        async with db.begin():
            yield
    else:
        # if transaction is open - just go
        yield
