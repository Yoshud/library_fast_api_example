from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models import BookTitle
from app.repositories.book_title_repository import BookTitleRepository
from app.schemas import BookTitleCreateScheme


@pytest.fixture
def mock_db():
    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    return db


@pytest.fixture
def book_title_repository():
    return BookTitleRepository()


@pytest.fixture
def sample_book_title():
    bt = BookTitle()
    bt.id = 1
    bt.title = "Wiedźmin"
    bt.author = "Andrzej Sapkowski"
    return bt


class TestGetBookTitle:
    async def test_get_book_title_found(self, book_title_repository, mock_db, sample_book_title):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_book_title
        mock_db.execute.return_value = mock_result

        result = await book_title_repository.get_book_title(mock_db, "000001")

        assert result == sample_book_title
        mock_db.execute.assert_awaited_once()

    async def test_get_book_title_not_found(self, book_title_repository, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await book_title_repository.get_book_title(mock_db, "999999")

        assert result is None


class TestGetBookTitleByTitle:
    async def test_found(self, book_title_repository, mock_db, sample_book_title):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_book_title
        mock_db.execute.return_value = mock_result

        result = await book_title_repository.get_book_title_by_title(mock_db, "Wiedźmin", "Andrzej Sapkowski")

        assert result == sample_book_title

    async def test_not_found(self, book_title_repository, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await book_title_repository.get_book_title_by_title(mock_db, "Nieistniejąca", "Nikt")

        assert result is None


class TestGetBookTitles:
    async def test_get_book_titles(self, book_title_repository, mock_db, sample_book_title):
        mock_scalars = MagicMock()
        mock_scalars.__iter__ = MagicMock(return_value=iter([sample_book_title]))
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        result = await book_title_repository.get_book_titles(mock_db, skip=0, limit=10)

        assert result == [sample_book_title]

    async def test_get_book_titles_empty(self, book_title_repository, mock_db):
        mock_scalars = MagicMock()
        mock_scalars.__iter__ = MagicMock(return_value=iter([]))
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        result = await book_title_repository.get_book_titles(mock_db)

        assert result == []


class TestCreateBookTitle:
    async def test_create_book_title_success(self, book_title_repository, mock_db, sample_book_title):
        book_title_data = BookTitleCreateScheme(title="Wiedźmin", author="Andrzej Sapkowski")

        result = await book_title_repository.create_book_title(mock_db, book_title_data)

        # Verify db.add was called with a BookTitle instance
        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert isinstance(added_obj, BookTitle)
        assert added_obj.title == "Wiedźmin"
        assert added_obj.author == "Andrzej Sapkowski"

        # Verify flush was awaited
        mock_db.flush.assert_awaited_once()

        # Result is the same object that was added
        assert result is added_obj
