from app.api.deps import get_db

from app.managers.basic_managers.book_copy_manager import BookCopyManager
from app.managers.composite_managers.book_manager import BookManager
from app.repositories.book_copy_repository import BookCopyRepositoryDuplicateIdException, \
    BookCopyServiceNoBookInfoException

from app.schemas import BookCreateScheme, BookResponseBasicScheme

from fastapi import APIRouter, Depends, status, HTTPException
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
    try:
        if book_data.book_title_id is not None:
            return await book_copy_manager.create_book_copy(db, book_data.id, book_data.book_title_id)

        return await book_manager.create_book_copy_with_book_title(db, book_data.id, book_data.book_title)
    except BookCopyRepositoryDuplicateIdException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"There is already book copy with serial number {book_data.id} in DB"
        )
    except BookCopyServiceNoBookInfoException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND_CONFLICT,
            detail=f"Book title id {book_data.book_title_id} not found"
        )
