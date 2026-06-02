from app.controllers.basic_controllers.book_copy_service import BookCopyService, BookCopyServiceException
from app.controllers.basic_controllers.book_title_service import BookTitleService
from app.models import BookCopy
from app.schemas import BookTitleCreateScheme, BookUpdateBorrowersScheme
from app.utils.db_utils import optional_transaction
from app.utils.pg_errors import get_pg_error_code, FOREIGN_KEY_VIOLATION_PG_ERROR_CODE
from app.utils.types import serial_number

from datetime import datetime, timezone
from logging import getLogger

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError


logger = getLogger()


class BookCompositeServiceException(Exception):
    pass

class BookCompositeBookCopyNotFoundException(BookCompositeServiceException):
    def __init__(self, book_copy_id: serial_number):
        super().__init__(f"Book copy '{book_copy_id}' not exist")
        self.book_copy_id = book_copy_id

class BookCompositeUserNotFoundException(BookCompositeServiceException): pass

class BookCompositeAlreadyBorrowedException(BookCompositeServiceException):
    def __init__(self, book_copy_id: serial_number, already_borrowing_user_id: serial_number):
        super().__init__(f"Book '{book_copy_id}' is already borrowed by '{already_borrowing_user_id}'")
        self.book_copy_id = book_copy_id
        self.already_borrowing_user_id = already_borrowing_user_id

class BookCompositeServiceUnknownIntegrityException(BookCompositeServiceException): pass


class BookCompositeService:
    @staticmethod
    async def create_book_copy_with_book_title(db: AsyncSession,
            book_copy_id: serial_number,
            book_title_data: BookTitleCreateScheme) -> BookCopy:
        async with optional_transaction(db):
            book_title = await BookTitleService.create_book_title(db, book_title_data)

            try:
                book_copy = await BookCopyService.create_book_copy(
                    db=db,
                    book_copy_id=book_copy_id,
                    book_title_id=book_title.id
                )

                return book_copy

            except BookCopyServiceException as e:
                raise e

    @staticmethod
    async def update_books_borrowers(
            db: AsyncSession,
            data: BookUpdateBorrowersScheme
    ) -> list[BookCopy]:
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
            now = datetime.now(timezone.utc)

            for copy_id in requested_ids:
                if copy_id not in existing_copies:
                    raise BookCompositeBookCopyNotFoundException(copy_id)

                copy = existing_copies[copy_id]
                new_user_id = data.update_borrowers_map[copy_id]

                # Option 1: Try borrowing book
                if new_user_id is not None:
                    if copy.user_id is not None:
                        raise BookCompositeAlreadyBorrowedException(copy_id, copy.user_id)

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
                    raise BookCompositeUserNotFoundException from e
                raise BookCompositeServiceUnknownIntegrityException from e

        # possible thanks to 'expire_on_commit=False' in async_sessionmaker
        return [existing_copies[cid] for cid in requested_ids]
