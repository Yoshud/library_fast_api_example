from unittest.mock import AsyncMock, patch

import pytest

from app.managers.basic_managers.book_copy_manager import BookCopyManager
from app.models import BookCopy
from app.repositories.book_copy_repository import BookCopyRepositoryDuplicateIdError
from app.tests.unit.conftest import noop_transaction


@pytest.fixture
def mock_book_copy_repo():
    return AsyncMock()


@pytest.fixture
def book_copy_manager(mock_book_copy_repo):
    return BookCopyManager(book_copy_repository=mock_book_copy_repo)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def sample_book_copy():
    bc = BookCopy()
    bc.id = "000001"
    bc.book_title_id = 1
    bc.user_id = None
    bc.borrowing_time = None
    return bc


class TestCreateBookCopy:
    @patch("app.managers.basic_managers.book_copy_manager.optional_transaction", noop_transaction)
    async def test_create_book_copy_success(self, book_copy_manager, mock_book_copy_repo, mock_db, sample_book_copy):
        mock_book_copy_repo.create_book_copy.return_value = sample_book_copy

        result = await book_copy_manager.create_book_copy(mock_db, "000001", 1)

        assert result == sample_book_copy
        mock_book_copy_repo.create_book_copy.assert_awaited_once_with(mock_db, "000001", 1)

    @patch("app.managers.basic_managers.book_copy_manager.optional_transaction", noop_transaction)
    async def test_create_book_copy_duplicate_propagates_error(self, book_copy_manager, mock_book_copy_repo, mock_db):
        mock_book_copy_repo.create_book_copy.side_effect = BookCopyRepositoryDuplicateIdError

        with pytest.raises(BookCopyRepositoryDuplicateIdError):
            await book_copy_manager.create_book_copy(mock_db, "000001", 1)


class TestGetBookCopyWithDetails:
    async def test_get_book_copy_with_details_found(
        self, book_copy_manager, mock_book_copy_repo, mock_db, sample_book_copy
    ):
        mock_book_copy_repo.get_book_copy_with_details.return_value = sample_book_copy

        result = await book_copy_manager.get_book_copy_with_details(mock_db, "000001")

        assert result == sample_book_copy
        mock_book_copy_repo.get_book_copy_with_details.assert_awaited_once_with(mock_db, "000001")

    async def test_get_book_copy_with_details_not_found(self, book_copy_manager, mock_book_copy_repo, mock_db):
        mock_book_copy_repo.get_book_copy_with_details.return_value = None

        result = await book_copy_manager.get_book_copy_with_details(mock_db, "999999")

        assert result is None


class TestGetBookCopiesWithDetails:
    async def test_get_book_copies_with_details(
        self, book_copy_manager, mock_book_copy_repo, mock_db, sample_book_copy
    ):
        mock_book_copy_repo.get_all_book_copies_with_details.return_value = [sample_book_copy]

        result = await book_copy_manager.get_book_copies_with_details(mock_db, skip=0, limit=50)

        assert result == [sample_book_copy]
        mock_book_copy_repo.get_all_book_copies_with_details.assert_awaited_once_with(mock_db, 0, 50)

    async def test_get_book_copies_with_details_default_params(self, book_copy_manager, mock_book_copy_repo, mock_db):
        mock_book_copy_repo.get_all_book_copies_with_details.return_value = []

        result = await book_copy_manager.get_book_copies_with_details(mock_db)

        assert result == []
        mock_book_copy_repo.get_all_book_copies_with_details.assert_awaited_once_with(mock_db, 0, 100)
