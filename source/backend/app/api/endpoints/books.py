from app.api.deps import get_db

from app.managers.basic_managers.book_copy_manager import BookCopyManager
from app.managers.composite_managers.book_manager import BookManager

from app.schemas import BookCreateScheme, BookResponseBasicScheme

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.post("/", response_model=BookResponseBasicScheme, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreateScheme,
    db: AsyncSession = Depends(get_db),
    book_manager: BookManager = Depends(),
    book_copy_manager: BookCopyManager = Depends()
):
    # "bad" cases are supported by pydantic
    if book_data.book_title_id is not None:
        return await book_copy_manager.create_book_copy(db, book_data.id, book_data.book_title_id)
    return await book_manager.create_book_copy_with_book_title(db, book_data.id, book_data.book_title)
