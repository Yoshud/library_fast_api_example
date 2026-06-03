from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import User
from app.repositories.user_repository import (
    UserRepository,
    UserRepositoryDuplicateIdError,
    UserRepositoryUnknownIntegrityError,
)
from app.schemas import UserCreateScheme


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def user_repository():
    return UserRepository()


@pytest.fixture
def sample_user():
    user = User()
    user.id = "100001"
    user.name = "Jan Kowalski"
    return user


class TestGetUser:
    async def test_get_user_found(self, user_repository, mock_db, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        result = await user_repository.get_user(mock_db, "100001")

        assert result == sample_user
        mock_db.execute.assert_awaited_once()

    async def test_get_user_not_found(self, user_repository, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute.return_value = mock_result

        result = await user_repository.get_user(mock_db, "999999")

        assert result is None


class TestGetUsers:
    async def test_get_users(self, user_repository, mock_db, sample_user):
        mock_scalars = MagicMock()
        mock_scalars.__iter__ = MagicMock(return_value=iter([sample_user]))
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        result = await user_repository.get_users(mock_db, skip=0, limit=10)

        assert result == [sample_user]
        mock_db.execute.assert_awaited_once()

    async def test_get_users_empty(self, user_repository, mock_db):
        mock_scalars = MagicMock()
        mock_scalars.__iter__ = MagicMock(return_value=iter([]))
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        mock_db.execute.return_value = mock_result

        result = await user_repository.get_users(mock_db)

        assert result == []


class TestCreateUser:
    async def test_create_user_success(self, user_repository, mock_db, sample_user):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_user
        mock_db.execute.return_value = mock_result

        user_data = UserCreateScheme(id="100001", name="Jan Kowalski")
        result = await user_repository.create_user(mock_db, user_data)

        assert result == sample_user
        mock_db.execute.assert_awaited_once()

    async def test_create_user_duplicate_raises(self, user_repository, mock_db):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None  # on_conflict_do_nothing → None
        mock_db.execute.return_value = mock_result

        user_data = UserCreateScheme(id="100001", name="Jan Kowalski")

        with pytest.raises(UserRepositoryDuplicateIdError):
            await user_repository.create_user(mock_db, user_data)

    async def test_create_user_integrity_error_raises(self, user_repository, mock_db):
        orig = MagicMock()
        mock_db.execute.side_effect = IntegrityError("error", params=None, orig=orig)

        user_data = UserCreateScheme(id="100001", name="Jan Kowalski")

        with pytest.raises(UserRepositoryUnknownIntegrityError):
            await user_repository.create_user(mock_db, user_data)
