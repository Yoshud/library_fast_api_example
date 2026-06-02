from app.repositories.user_repository import UserRepository
from app.models import User
from app.schemas import UserCreateScheme
from app.utils.db_utils import optional_transaction
from app.utils.types import serial_number

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class UserManager:
    def __init__(
        self,
        user_repository: UserRepository = Depends(),
    ):
        self.user_repository = user_repository

    async def get_user(self, db: AsyncSession, user_id: serial_number) -> User | None:
        return await self.user_repository.get_user(db, user_id)

    async def get_users(self, db: AsyncSession, skip: int = 0, limit: int = 1000) -> list[User]:
        return await self.user_repository.get_users(db, skip, limit)

    async def create_user(self, db: AsyncSession, user_data: UserCreateScheme) -> User:
        async with optional_transaction(db):
            return await self.user_repository.create_user(db, user_data)
