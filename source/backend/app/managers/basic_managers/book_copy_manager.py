from app.repositories.book_copy_repository import BookCopyRepository
from app.models import BookCopy
from app.utils.db_utils import optional_transaction
from app.utils.types import serial_number

from logging import getLogger

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


logger = getLogger()


class BookCopyManager:
    def __init__(
        self,
        book_copy_repository: BookCopyRepository = Depends(),
    ):
        self.book_copy_repository = book_copy_repository

    async def create_book_copy(self, db: AsyncSession, book_copy_id: serial_number, book_title_id: int) -> BookCopy:
        async with optional_transaction(db):
            return await self.book_copy_repository.create_book_copy(db, book_copy_id, book_title_id)
