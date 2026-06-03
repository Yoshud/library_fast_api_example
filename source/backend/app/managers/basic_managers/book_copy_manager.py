from logging import getLogger
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BookCopy
from app.repositories.book_copy_repository import BookCopyRepository
from app.utils.db_utils import optional_transaction
from app.utils.types import serial_number

logger = getLogger()


class BookCopyManagerBookCopyNotFoundError(Exception):
    def __init__(self, book_copy_id: serial_number):
        super().__init__(f"Book copy '{book_copy_id}' not exist")
        self.book_copy_id = book_copy_id


class BookCopyManager:
    def __init__(
        self,
        book_copy_repository: Annotated[BookCopyRepository, Depends()],
    ):
        self.book_copy_repository = book_copy_repository

    async def create_book_copy(self, db: AsyncSession, book_copy_id: serial_number, book_title_id: int) -> BookCopy:
        async with optional_transaction(db):
            return await self.book_copy_repository.create_book_copy(db, book_copy_id, book_title_id)

    async def get_book_copy_with_details(self, db: AsyncSession, book_copy_id: serial_number) -> BookCopy | None:
        return await self.book_copy_repository.get_book_copy_with_details(db, book_copy_id)

    async def get_book_copies_with_details(self, db: AsyncSession, skip: int = 0, limit: int = 100,) -> list[BookCopy]:
        return await self.book_copy_repository.get_all_book_copies_with_details(db, skip, limit)
