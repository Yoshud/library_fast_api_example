from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import BookCopy
from app.repositories.book_copy_repository import (
    BookCopyRepository,
    BookCopyRepositoryDuplicateIdError,
    BookCopyRepositoryNoBookInfoError,
    BookCopyRepositoryUnknownIntegrityError,
)
from app.utils.pg_errors import FOREIGN_KEY_VIOLATION_PG_ERROR_CODE


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def book_copy_repository():
    return BookCopyRepository()


@pytest.fixture
def sample_book_copy():
    bc = BookCopy()
    bc.id = "000001"
    bc.book_title_id = 1
    bc.user_id = None
    bc.borrowing_time = None
    return bc


class TestCreateBookCopy:
    async def test_create_success(self, book_copy_repository, mock_db, sample_book_copy):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_book_copy
        mock_db.execute.return_value = mock_result

        result = await book_copy_repository.create_book_copy(mock_db, "000001", 1)

        assert result == sample_book_copy
        mock_db.execute.assert_awaited_once()

    async def test_create_duplicate_raises(self, book_copy_repository, mock_db):
        """on_conflict_do_nothing returns None for duplicate → raises DuplicateIdError."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        with pytest.raises(BookCopyRepositoryDuplicateIdError):
            await book_copy_repository.create_book_copy(mock_db, "000001", 1)

    async def test_create_no_book_info_fk_violation(self, book_copy_repository, mock_db):
        """FK violation (book_title_id doesn't exist) → BookCopyRepositoryNoBookInfoError."""
        orig = MagicMock()
        orig.pgcode = FOREIGN_KEY_VIOLATION_PG_ERROR_CODE
        orig.sqlstate = FOREIGN_KEY_VIOLATION_PG_ERROR_CODE
        mock_db.execute.side_effect = IntegrityError("fk", params=None, orig=orig)

        with pytest.raises(BookCopyRepositoryNoBookInfoError):
            await book_copy_repository.create_book_copy(mock_db, "000001", 9999)

    async def test_create_unknown_integrity_error(self, book_copy_repository, mock_db):
        """Non-FK IntegrityError → BookCopyRepositoryUnknownIntegrityError."""
        orig = MagicMock()
        orig.pgcode = "99999"
        orig.sqlstate = "99999"
        mock_db.execute.side_effect = IntegrityError("other", params=None, orig=orig)

        with pytest.raises(BookCopyRepositoryUnknownIntegrityError):
            await book_copy_repository.create_book_copy(mock_db, "000001", 1)


class TestGetBookCopyWithDetails:
    async def test_found(self, book_copy_repository, mock_db, sample_book_copy):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_book_copy
        mock_db.execute.return_value = mock_result

        result = await book_copy_repository.get_book_copy_with_details(mock_db, "000001")

        assert result == sample_book_copy

    async def test_not_found(self, book_copy_repository, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await book_copy_repository.get_book_copy_with_details(mock_db, "999999")

        assert result is None


class TestGetAllBookCopiesWithDetails:
    async def test_returns_list(self, book_copy_repository, mock_db, sample_book_copy):
        mock_unique = MagicMock()
        mock_unique.__iter__ = MagicMock(return_value=iter([sample_book_copy]))
        mock_scalars = MagicMock()
        mock_scalars.unique.return_value = mock_unique
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        result = await book_copy_repository.get_all_book_copies_with_details(mock_db, skip=0, limit=10)

        assert result == [sample_book_copy]

    async def test_returns_empty(self, book_copy_repository, mock_db):
        mock_unique = MagicMock()
        mock_unique.__iter__ = MagicMock(return_value=iter([]))
        mock_scalars = MagicMock()
        mock_scalars.unique.return_value = mock_unique
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        result = await book_copy_repository.get_all_book_copies_with_details(mock_db)

        assert result == []
