from datetime import UTC, datetime
from logging import getLogger
from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BookCopy
from app.repositories.book_copy_repository import BookCopyRepository, BookCopyRepositoryError
from app.repositories.book_title_repository import BookTitleRepository
from app.schemas import BookTitleCreateScheme, BookUpdateBorrowersScheme
from app.utils.db_utils import optional_transaction
from app.utils.pg_errors import FOREIGN_KEY_VIOLATION_PG_ERROR_CODE, get_pg_error_code
from app.utils.types import serial_number

logger = getLogger()


class BookManagerServiceError(Exception):
    pass


class BookManagerBookCopyNotFoundError(BookManagerServiceError):
    def __init__(self, book_copy_id: serial_number):
        super().__init__(f"Book copy '{book_copy_id}' not exist")
        self.book_copy_id = book_copy_id


class BookManagerUserNotFoundError(BookManagerServiceError):
    pass


class BookManagerAlreadyBorrowedError(BookManagerServiceError):
    def __init__(self, book_copy_id: serial_number, already_borrowing_user_id: serial_number):
        super().__init__(f"Book '{book_copy_id}' is already borrowed by '{already_borrowing_user_id}'")
        self.book_copy_id = book_copy_id
        self.already_borrowing_user_id = already_borrowing_user_id


class BookManagerServiceUnknownIntegrityError(BookManagerServiceError):
    pass


class BookManager:
    def __init__(
        self,
        book_title_repository: Annotated[BookTitleRepository, Depends()],
        book_copy_repository: Annotated[BookCopyRepository, Depends()],
    ):
        self.book_title_repository = book_title_repository
        self.book_copy_repository = book_copy_repository

    async def create_book_copy_with_book_title(
        self, db: AsyncSession, book_copy_id: serial_number, book_title_data: BookTitleCreateScheme
    ) -> BookCopy:
        async with optional_transaction(db):
            book_title = await self.book_title_repository.create_book_title(db, book_title_data)

            try:
                book_copy = await self.book_copy_repository.create_book_copy(
                    db=db, book_copy_id=book_copy_id, book_title_id=book_title.id
                )

                return book_copy

            except BookCopyRepositoryError as e:
                raise e

    async def update_books_borrowers(self, db: AsyncSession, data: BookUpdateBorrowersScheme) -> list[BookCopy]:
        # Not the cleanest approach, but best one in this specific case
        if not data.update_borrowers_map:
            return []

        # CRITICAL - ids are sorted so deadlock shouldn't be possible when multiple updates will start in same time
        # ( further ones will stop immanently or immanently after encounter first different update )
        # what relly mean sorted is not important - they just need to be in specific always same order
        # also ignore redundant ones
        requested_ids = sorted(data.update_borrowers_map.keys())

        async with optional_transaction(db):
            # We lock rows in table it's only safe option
            stmt = select(BookCopy).where(BookCopy.id.in_(requested_ids)).with_for_update()
            result = await db.execute(stmt)
            existing_copies = {copy.id: copy for copy in result.scalars()}

            # TODO: Przenieść strefę czasową do konfiguracji aplikacji
            now = datetime.now(UTC)

            for copy_id in requested_ids:
                if copy_id not in existing_copies:
                    raise BookManagerBookCopyNotFoundError(copy_id)

                copy = existing_copies[copy_id]
                new_user_id = data.update_borrowers_map[copy_id]

                # Option 1: Try borrowing book
                if new_user_id is not None:
                    if copy.user_id is not None:
                        raise BookManagerAlreadyBorrowedError(copy_id, copy.user_id)

                    # new values
                    copy.user_id = new_user_id
                    copy.borrowing_time = now

                # Option 2: Try to return book
                else:
                    if copy.user_id is None:
                        logger.warning("Try to return already returned book - operation is idempotent")

                    copy.user_id = None
                    copy.borrowing_time = None

            # Try to save byt user_ids can not exist (assuming they exist are faster)
            try:
                # sqlalchemy will do bulk update underneath
                await db.flush()
            except IntegrityError as e:
                pg_error_code = get_pg_error_code(e)
                if pg_error_code == FOREIGN_KEY_VIOLATION_PG_ERROR_CODE:
                    raise BookManagerUserNotFoundError from e
                raise BookManagerServiceUnknownIntegrityError from e

        # possible thanks to 'expire_on_commit=False' in async_sessionmaker
        return [existing_copies[cid] for cid in requested_ids]
