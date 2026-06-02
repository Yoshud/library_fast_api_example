from app.api.deps import get_db
from app.controllers.basic_controllers.user_service import UserService
from app.schemas import UserResponseScheme, UserCreateScheme
from app.utils.types import serial_number

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.get("/", response_model=list[UserResponseScheme])
async def read_users(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    async with db.begin():
        users = await UserService.get_users(db, skip, limit)
    return users


@router.get("/{user_id}", response_model=UserResponseScheme)
async def read_user(
    user_id: serial_number,
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        user = await UserService.get_user(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("/", response_model=UserResponseScheme, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateScheme,
    db: AsyncSession = Depends(get_db),
):
    async with db.begin():
        user = await UserService.create_user(db, user_data)

    return user
