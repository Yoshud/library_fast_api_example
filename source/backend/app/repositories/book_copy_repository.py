from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.book_copy import BookCopy
from app.utils.pg_errors import FOREIGN_KEY_VIOLATION_PG_ERROR_CODE, get_pg_error_code
from app.utils.types import serial_number


class BookCopyRepositoryError(Exception):
    pass


class BookCopyRepositoryDuplicateIdError(BookCopyRepositoryError):
    pass


class BookCopyRepositoryNoBookInfoError(BookCopyRepositoryError):
    pass


class BookCopyRepositoryUnknownIntegrityError(BookCopyRepositoryError):
    pass


class BookCopyRepository:
    @staticmethod
    async def create_book_copy(db: AsyncSession, book_copy_id: serial_number, book_title_id: int) -> BookCopy:
        # only postgresql option -> atomic operation - safe in async
        stmt = (
            insert(BookCopy)
            .values(id=book_copy_id, book_title_id=book_title_id)
            .on_conflict_do_nothing(index_elements=["id"])
            .returning(BookCopy)
        )

        try:
            result = await db.execute(stmt)
            book_copy = result.scalar_one_or_none()
        except IntegrityError as e:
            pg_error_code = get_pg_error_code(e)
            if pg_error_code == FOREIGN_KEY_VIOLATION_PG_ERROR_CODE:
                raise BookCopyRepositoryNoBookInfoError from e

            raise BookCopyRepositoryUnknownIntegrityError from e

        # returning will return None if object exist
        if book_copy is None:
            raise BookCopyRepositoryDuplicateIdError
        return book_copy

    @staticmethod
    async def get_book_copy_with_details(db: AsyncSession, book_copy_id: serial_number) -> BookCopy | None:
        """Fetch a single BookCopy with all its related entities eagerly loaded."""
        stmt = (
            select(BookCopy)
            .where(BookCopy.id == book_copy_id)
            .options(joinedload(BookCopy.book_title), joinedload(BookCopy.user))
        )
        result = await db.execute(stmt)
        book_copy = result.scalar_one_or_none()

        return book_copy

    @staticmethod
    async def get_all_book_copies_with_details(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[BookCopy]:
        """Fetch all BookCopies with all their related entities eagerly loaded."""
        stmt = (
            select(BookCopy)
            .options(joinedload(BookCopy.book_title), joinedload(BookCopy.user))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        # .unique() is required when using joinedload to handle row deduplication correctly
        return list(result.scalars().unique())
