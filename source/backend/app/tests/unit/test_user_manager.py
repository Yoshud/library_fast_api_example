from unittest.mock import AsyncMock, patch

import pytest

from app.managers.basic_managers.user_manager import UserManager
from app.models import User
from app.repositories.user_repository import UserRepositoryDuplicateIdError
from app.schemas import UserCreateScheme
from app.tests.unit.conftest import noop_transaction


@pytest.fixture
def mock_user_repo():
    return AsyncMock()


@pytest.fixture
def user_manager(mock_user_repo):
    return UserManager(user_repository=mock_user_repo)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def sample_user():
    user = User()
    user.id = "100001"
    user.name = "Jan Kowalski"
    return user


class TestGetUser:
    async def test_get_user_found(self, user_manager, mock_user_repo, mock_db, sample_user):
        mock_user_repo.get_user.return_value = sample_user

        result = await user_manager.get_user(mock_db, "100001")

        assert result == sample_user
        mock_user_repo.get_user.assert_awaited_once_with(mock_db, "100001")

    async def test_get_user_not_found(self, user_manager, mock_user_repo, mock_db):
        mock_user_repo.get_user.return_value = None

        result = await user_manager.get_user(mock_db, "999999")

        assert result is None
        mock_user_repo.get_user.assert_awaited_once_with(mock_db, "999999")


class TestGetUsers:
    async def test_get_users(self, user_manager, mock_user_repo, mock_db, sample_user):
        mock_user_repo.get_users.return_value = [sample_user]

        result = await user_manager.get_users(mock_db, skip=5, limit=10)

        assert result == [sample_user]
        mock_user_repo.get_users.assert_awaited_once_with(mock_db, 5, 10)

    async def test_get_users_default_params(self, user_manager, mock_user_repo, mock_db):
        mock_user_repo.get_users.return_value = []

        result = await user_manager.get_users(mock_db)

        assert result == []
        mock_user_repo.get_users.assert_awaited_once_with(mock_db, 0, 1000)


class TestCreateUser:
    @patch("app.managers.basic_managers.user_manager.optional_transaction", noop_transaction)
    async def test_create_user_success(self, user_manager, mock_user_repo, mock_db, sample_user):
        user_data = UserCreateScheme(id="100001", name="Jan Kowalski")
        mock_user_repo.create_user.return_value = sample_user

        result = await user_manager.create_user(mock_db, user_data)

        assert result == sample_user
        mock_user_repo.create_user.assert_awaited_once_with(mock_db, user_data)

    @patch("app.managers.basic_managers.user_manager.optional_transaction", noop_transaction)
    async def test_create_user_duplicate_propagates_error(self, user_manager, mock_user_repo, mock_db):
        user_data = UserCreateScheme(id="100001", name="Jan Kowalski")
        mock_user_repo.create_user.side_effect = UserRepositoryDuplicateIdError

        with pytest.raises(UserRepositoryDuplicateIdError):
            await user_manager.create_user(mock_db, user_data)
