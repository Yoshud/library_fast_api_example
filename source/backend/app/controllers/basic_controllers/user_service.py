from app.models import User
from app.utils.types import serial_number
from app.schemas import UserCreateScheme

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError


class UserServiceError(Exception):
    pass

class UserServiceDuplicateIdError(UserServiceError):
    pass

class UserServiceUnknownIntegrityError(UserServiceError):
    pass


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
        # only postgresql option -> atomic operation - safe in async
        stmt = (
            insert(User)
            .values(id=user_data.id, name=user_data.name)
            .on_conflict_do_nothing(index_elements=['id'])
            .returning(User)
        )

        try:
            result = await db.execute(stmt)
            book_copy = result.scalar_one_or_none()
        except IntegrityError as e:
            raise UserServiceUnknownIntegrityError from e

        # returning will return None if object exist
        if book_copy is None:
            raise UserServiceDuplicateIdError
        return book_copy

    @staticmethod
    async def update_user(db: AsyncSession):
        raise NotImplementedError("Not specified as required")

    @staticmethod
    async def delete_user(db: AsyncSession):
        raise NotImplementedError("Not specified as required")
