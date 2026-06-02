from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User

from sqlalchemy import select

from app.utils.types import serial_number
from app.schemas import UserCreateScheme


class UserService:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: serial_number) -> User|None:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        return user

    @staticmethod
    async def get_users(db: AsyncSession, skip: int = 0, limit: int = 1000) -> list[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars())

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreateScheme) -> User:
        # TODO: get user serial number and check
        user = User(title=user_data.name)
        db.add(user)
        await db.commit()
        # value and id will be set thanks to 'expire_on_commit=False' in async_sessionmaker
        return user

    @staticmethod
    async def update_user(db: AsyncSession):
        raise NotImplementedError("Not specified as required")

    @staticmethod
    async def delete_user(db: AsyncSession):
        raise NotImplementedError("Not specified as required")
