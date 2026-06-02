from app.api.deps import get_db
from app.managers.basic_managers.user_manager import UserManager
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
    user_manager: UserManager = Depends(),
):
    users = await user_manager.get_users(db, skip, limit)
    return users


@router.get("/{user_id}", response_model=UserResponseScheme)
async def read_user(
    user_id: serial_number,
    db: AsyncSession = Depends(get_db),
    user_manager: UserManager = Depends(),
):
    user = await user_manager.get_user(db, user_id)
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
    user_manager: UserManager = Depends(),
):
    user = await user_manager.create_user(db, user_data)
    return user