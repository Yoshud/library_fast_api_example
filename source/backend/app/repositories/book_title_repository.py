from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BookTitle
from app.schemas import BookTitleCreateScheme
from app.utils.types import name_literal, serial_number


class BookTitleRepository:
    @staticmethod
    async def get_book_title(db: AsyncSession, book_title_id: serial_number) -> BookTitle | None:
        result = await db.execute(select(BookTitle).where(BookTitle.id == book_title_id))
        book_title = result.scalar_one_or_none()
        return book_title

    @staticmethod
    async def get_book_title_by_title(db: AsyncSession, title: name_literal, author: name_literal) -> BookTitle | None:
        result = await db.execute(select(BookTitle).where(BookTitle.title == title, BookTitle.author == author))
        # Composite index on model level ensure 0 or 1 book title as response
        book_title = result.scalar_one_or_none()
        return book_title

    @staticmethod
    async def get_book_titles(db: AsyncSession, skip: int = 0, limit: int = 1000) -> list[BookTitle]:
        result = await db.execute(select(BookTitle).offset(skip).limit(limit))
        return list(result.scalars())

    @staticmethod
    async def create_book_title(db: AsyncSession, book_title_data: BookTitleCreateScheme) -> BookTitle:
        book_title = BookTitle(title=book_title_data.title, author=book_title_data.author)
        db.add(book_title)
        await db.flush()
        # value and id will be set thanks to 'expire_on_commit=False' in async_sessionmaker
        return book_title

    @staticmethod
    async def update_book_title(db: AsyncSession):
        raise NotImplementedError("Not specified as required")

    @staticmethod
    async def delete_book_title(db: AsyncSession):
        raise NotImplementedError("Not specified as required")
