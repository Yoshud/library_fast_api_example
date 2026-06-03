from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError

from app.managers.composite_managers.book_manager import (
    BookManager,
    BookManagerAlreadyBorrowedError,
    BookManagerBookCopyNotFoundError,
    BookManagerServiceUnknownIntegrityError,
    BookManagerUserNotFoundError,
)
from app.models import BookCopy, BookTitle
from app.repositories.book_copy_repository import BookCopyRepositoryDuplicateIdError
from app.schemas import BookTitleCreateScheme, BookUpdateBorrowersScheme
from app.tests.unit.conftest import noop_transaction
from app.utils.pg_errors import FOREIGN_KEY_VIOLATION_PG_ERROR_CODE


@pytest.fixture
def mock_book_title_repo():
    return AsyncMock()


@pytest.fixture
def mock_book_copy_repo():
    return AsyncMock()


@pytest.fixture
def book_manager(mock_book_title_repo, mock_book_copy_repo):
    return BookManager(
        book_title_repository=mock_book_title_repo,
        book_copy_repository=mock_book_copy_repo,
    )


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def sample_book_title():
    bt = BookTitle()
    bt.id = 1
    bt.title = "Wiedźmin"
    bt.author = "Andrzej Sapkowski"
    return bt


@pytest.fixture
def sample_book_copy():
    bc = BookCopy()
    bc.id = "000001"
    bc.book_title_id = 1
    bc.user_id = None
    bc.borrowing_time = None
    return bc


def _make_fk_integrity_error():
    """Create an IntegrityError that mimics a PostgreSQL foreign key violation."""
    orig = MagicMock()
    orig.pgcode = FOREIGN_KEY_VIOLATION_PG_ERROR_CODE
    orig.sqlstate = FOREIGN_KEY_VIOLATION_PG_ERROR_CODE
    error = IntegrityError("fk violation", params=None, orig=orig)
    return error


def _make_generic_integrity_error():
    """Create an IntegrityError that is NOT a foreign key violation."""
    orig = MagicMock()
    orig.pgcode = "99999"
    orig.sqlstate = "99999"
    error = IntegrityError("generic error", params=None, orig=orig)
    return error


# ─────────────────────────────────────────────────────────────
# create_book_copy_with_book_title
# ─────────────────────────────────────────────────────────────
class TestCreateBookCopyWithBookTitle:
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_success(
        self, book_manager, mock_book_title_repo, mock_book_copy_repo, mock_db,
        sample_book_title, sample_book_copy,
    ):
        mock_book_title_repo.create_book_title.return_value = sample_book_title
        mock_book_copy_repo.create_book_copy.return_value = sample_book_copy

        book_title_data = BookTitleCreateScheme(title="Wiedźmin", author="Andrzej Sapkowski")
        result = await book_manager.create_book_copy_with_book_title(mock_db, "000001", book_title_data)

        assert result == sample_book_copy
        mock_book_title_repo.create_book_title.assert_awaited_once_with(mock_db, book_title_data)
        mock_book_copy_repo.create_book_copy.assert_awaited_once_with(
            db=mock_db, book_copy_id="000001", book_title_id=sample_book_title.id,
        )

    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_duplicate_copy_propagates_error(
        self, book_manager, mock_book_title_repo, mock_book_copy_repo, mock_db, sample_book_title,
    ):
        mock_book_title_repo.create_book_title.return_value = sample_book_title
        mock_book_copy_repo.create_book_copy.side_effect = BookCopyRepositoryDuplicateIdError

        book_title_data = BookTitleCreateScheme(title="Wiedźmin", author="Andrzej Sapkowski")

        with pytest.raises(BookCopyRepositoryDuplicateIdError):
            await book_manager.create_book_copy_with_book_title(mock_db, "000001", book_title_data)


# ─────────────────────────────────────────────────────────────
# update_books_borrowers
# ─────────────────────────────────────────────────────────────
def _setup_db_for_update(mock_db, copies: list[BookCopy]):
    """Configure mock_db so that execute(...) returns scalars matching the given copies."""
    mock_result = MagicMock()
    mock_result.scalars.return_value = copies
    mock_db.execute.return_value = mock_result


class TestUpdateBooksBorrowers:
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_empty_map_returns_empty(self, book_manager, mock_db):
        data = BookUpdateBorrowersScheme(update_borrowers_map={})

        result = await book_manager.update_books_borrowers(mock_db, data)

        assert result == []
        mock_db.execute.assert_not_awaited()

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_borrow_book_success(self, book_manager, mock_db, sample_book_copy):
        """Borrowing sets user_id and borrowing_time."""
        assert sample_book_copy.user_id is None
        _setup_db_for_update(mock_db, [sample_book_copy])

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": "200001"})
        result = await book_manager.update_books_borrowers(mock_db, data)

        assert len(result) == 1
        assert result[0].user_id == "200001"
        assert result[0].borrowing_time is not None
        mock_db.flush.assert_awaited_once()

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_return_book_success(self, book_manager, mock_db, sample_book_copy):
        """Returning clears user_id and borrowing_time."""
        from datetime import datetime, timezone

        sample_book_copy.user_id = "200001"
        sample_book_copy.borrowing_time = datetime.now(timezone.utc)
        _setup_db_for_update(mock_db, [sample_book_copy])

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": None})
        result = await book_manager.update_books_borrowers(mock_db, data)

        assert len(result) == 1
        assert result[0].user_id is None
        assert result[0].borrowing_time is None

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_borrow_already_borrowed_by_other_raises(self, book_manager, mock_db, sample_book_copy):
        """Trying to borrow a book already borrowed by another user raises error."""
        sample_book_copy.user_id = "200002"
        _setup_db_for_update(mock_db, [sample_book_copy])

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": "200001"})

        with pytest.raises(BookManagerAlreadyBorrowedError) as exc_info:
            await book_manager.update_books_borrowers(mock_db, data)

        assert exc_info.value.book_copy_id == "000001"
        assert exc_info.value.already_borrowing_user_id == "200002"

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_borrow_same_user_idempotent(self, book_manager, mock_db, sample_book_copy):
        """Borrowing by the same user is idempotent — no error, value unchanged."""
        from datetime import datetime, timezone

        original_time = datetime.now(timezone.utc)
        sample_book_copy.user_id = "200001"
        sample_book_copy.borrowing_time = original_time
        _setup_db_for_update(mock_db, [sample_book_copy])

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": "200001"})
        result = await book_manager.update_books_borrowers(mock_db, data)

        assert len(result) == 1
        # borrowing_time should remain unchanged (idempotent skip via continue)
        assert result[0].borrowing_time == original_time
        assert result[0].user_id == "200001"

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_return_already_returned_idempotent(self, book_manager, mock_db, sample_book_copy):
        """Returning an already-returned book is idempotent — no error."""
        assert sample_book_copy.user_id is None
        _setup_db_for_update(mock_db, [sample_book_copy])

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": None})
        result = await book_manager.update_books_borrowers(mock_db, data)

        assert len(result) == 1
        assert result[0].user_id is None

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_book_copy_not_found_raises(self, book_manager, mock_db):
        """Requesting an ID that doesn't exist in DB raises BookManagerBookCopyNotFoundError."""
        _setup_db_for_update(mock_db, [])  # no copies found

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": "200001"})

        with pytest.raises(BookManagerBookCopyNotFoundError) as exc_info:
            await book_manager.update_books_borrowers(mock_db, data)

        assert exc_info.value.book_copy_id == "000001"

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_user_not_found_fk_violation(self, book_manager, mock_db, sample_book_copy):
        """IntegrityError with FK violation on flush raises BookManagerUserNotFoundError."""
        _setup_db_for_update(mock_db, [sample_book_copy])
        mock_db.flush.side_effect = _make_fk_integrity_error()

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": "200001"})

        with pytest.raises(BookManagerUserNotFoundError):
            await book_manager.update_books_borrowers(mock_db, data)

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_unknown_integrity_error(self, book_manager, mock_db, sample_book_copy):
        """IntegrityError that is NOT FK violation raises BookManagerServiceUnknownIntegrityError."""
        _setup_db_for_update(mock_db, [sample_book_copy])
        mock_db.flush.side_effect = _make_generic_integrity_error()

        data = BookUpdateBorrowersScheme(update_borrowers_map={"000001": "200001"})

        with pytest.raises(BookManagerServiceUnknownIntegrityError):
            await book_manager.update_books_borrowers(mock_db, data)

    @patch("app.managers.composite_managers.book_manager.settings", MagicMock(TIMEZONE="Europe/Warsaw"))
    @patch("app.managers.composite_managers.book_manager.optional_transaction", noop_transaction)
    async def test_ids_processed_in_sorted_order(self, book_manager, mock_db):
        """Keys must be processed in sorted order to prevent deadlocks."""
        copy_a = BookCopy()
        copy_a.id = "000003"
        copy_a.user_id = None
        copy_a.borrowing_time = None
        copy_a.book_title_id = 1

        copy_b = BookCopy()
        copy_b.id = "000001"
        copy_b.user_id = None
        copy_b.borrowing_time = None
        copy_b.book_title_id = 2

        _setup_db_for_update(mock_db, [copy_a, copy_b])

        data = BookUpdateBorrowersScheme(
            update_borrowers_map={"000003": "200001", "000001": "200002"}
        )
        result = await book_manager.update_books_borrowers(mock_db, data)

        # Result order follows sorted keys
        assert [r.id for r in result] == ["000001", "000003"]
