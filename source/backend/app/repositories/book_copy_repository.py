from app.models.book_copy import BookCopy
from app.utils.pg_errors import get_pg_error_code, FOREIGN_KEY_VIOLATION_PG_ERROR_CODE
from app.utils.types import serial_number

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError


class BookCopyRepositoryException(Exception):
    pass

class BookCopyRepositoryDuplicateIdException(BookCopyRepositoryException):
    pass

class BookCopyServiceNoBookInfoException(BookCopyRepositoryException):
    pass

class BookCopyRepositoryUnknownIntegrityException(BookCopyRepositoryException):
    pass

class BookCopyRepository:
    @staticmethod
    async def create_book_copy(db: AsyncSession, book_copy_id: serial_number, book_title_id: int) -> BookCopy:
        # only postgresql option -> atomic operation - safe in async
        stmt = (
            insert(BookCopy)
            .values(id=book_copy_id, book_title_id=book_title_id)
            .on_conflict_do_nothing(index_elements=['id'])
            .returning(BookCopy)
        )

        try:
            result = await db.execute(stmt)
            book_copy = result.scalar_one_or_none()
        except IntegrityError as e:
            pg_error_code = get_pg_error_code(e)
            if pg_error_code == FOREIGN_KEY_VIOLATION_PG_ERROR_CODE:
                raise BookCopyServiceNoBookInfoException from e

            raise BookCopyRepositoryUnknownIntegrityException from e

        # returning will return None if object exist
        if book_copy is None:
            raise BookCopyRepositoryDuplicateIdException
        return book_copy
