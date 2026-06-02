from logging import getLogger
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BookTitle
from app.repositories.book_title_repository import BookTitleRepository
from app.schemas import BookTitleCreateScheme
from app.utils.db_utils import optional_transaction
from app.utils.types import name_literal, serial_number

logger = getLogger()


class BookTitleManager:
    def __init__(
        self,
        book_title_repository: Annotated[BookTitleRepository, Depends()],
    ):
        self.book_title_repository = book_title_repository

    async def get_book_title(self, db: AsyncSession, book_title_id: serial_number) -> BookTitle | None:
        return await self.book_title_repository.get_book_title(db, book_title_id)

    async def get_book_title_by_title(
        self, db: AsyncSession, title: name_literal, author: name_literal
    ) -> BookTitle | None:
        return await self.book_title_repository.get_book_title_by_title(db, title, author)

    async def get_book_titles(self, db: AsyncSession, skip: int = 0, limit: int = 1000) -> list[BookTitle]:
        return await self.book_title_repository.get_book_titles(db, skip, limit)

    async def create_book_title(self, db: AsyncSession, book_title_data: BookTitleCreateScheme) -> BookTitle:
        async with optional_transaction(db):
            return await self.book_title_repository.create_book_title(db, book_title_data)
