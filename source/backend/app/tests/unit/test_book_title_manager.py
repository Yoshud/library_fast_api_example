from unittest.mock import AsyncMock, patch

import pytest

from app.managers.basic_managers.book_title_manager import BookTitleManager
from app.models import BookTitle
from app.schemas import BookTitleCreateScheme
from app.tests.unit.conftest import noop_transaction


@pytest.fixture
def mock_book_title_repo():
    return AsyncMock()


@pytest.fixture
def book_title_manager(mock_book_title_repo):
    return BookTitleManager(book_title_repository=mock_book_title_repo)


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


class TestGetBookTitle:
    async def test_get_book_title_found(self, book_title_manager, mock_book_title_repo, mock_db, sample_book_title):
        mock_book_title_repo.get_book_title.return_value = sample_book_title

        result = await book_title_manager.get_book_title(mock_db, "000001")

        assert result == sample_book_title
        mock_book_title_repo.get_book_title.assert_awaited_once_with(mock_db, "000001")

    async def test_get_book_title_not_found(self, book_title_manager, mock_book_title_repo, mock_db):
        mock_book_title_repo.get_book_title.return_value = None

        result = await book_title_manager.get_book_title(mock_db, "999999")

        assert result is None


class TestGetBookTitleByTitle:
    async def test_get_book_title_by_title_found(
        self, book_title_manager, mock_book_title_repo, mock_db, sample_book_title
    ):
        mock_book_title_repo.get_book_title_by_title.return_value = sample_book_title

        result = await book_title_manager.get_book_title_by_title(mock_db, "Wiedźmin", "Andrzej Sapkowski")

        assert result == sample_book_title
        mock_book_title_repo.get_book_title_by_title.assert_awaited_once_with(mock_db, "Wiedźmin", "Andrzej Sapkowski")

    async def test_get_book_title_by_title_not_found(self, book_title_manager, mock_book_title_repo, mock_db):
        mock_book_title_repo.get_book_title_by_title.return_value = None

        result = await book_title_manager.get_book_title_by_title(mock_db, "Nieistniejąca", "Nikt")

        assert result is None


class TestGetBookTitles:
    async def test_get_book_titles(self, book_title_manager, mock_book_title_repo, mock_db, sample_book_title):
        mock_book_title_repo.get_book_titles.return_value = [sample_book_title]

        result = await book_title_manager.get_book_titles(mock_db, skip=0, limit=50)

        assert result == [sample_book_title]
        mock_book_title_repo.get_book_titles.assert_awaited_once_with(mock_db, 0, 50)

    async def test_get_book_titles_default_params(self, book_title_manager, mock_book_title_repo, mock_db):
        mock_book_title_repo.get_book_titles.return_value = []

        result = await book_title_manager.get_book_titles(mock_db)

        assert result == []
        mock_book_title_repo.get_book_titles.assert_awaited_once_with(mock_db, 0, 1000)


class TestCreateBookTitle:
    @patch("app.managers.basic_managers.book_title_manager.optional_transaction", noop_transaction)
    async def test_create_book_title_success(
        self, book_title_manager, mock_book_title_repo, mock_db, sample_book_title
    ):
        book_title_data = BookTitleCreateScheme(title="Wiedźmin", author="Andrzej Sapkowski")
        mock_book_title_repo.create_book_title.return_value = sample_book_title

        result = await book_title_manager.create_book_title(mock_db, book_title_data)

        assert result == sample_book_title
        mock_book_title_repo.create_book_title.assert_awaited_once_with(mock_db, book_title_data)
