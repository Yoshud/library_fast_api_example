from app.api.deps import get_db
from app.controllers.basic_controllers.book_copy_service import BookCopyService
from app.controllers.composite_controllers.book_composite_service import BookCompositeService

from app.schemas import BookCreateScheme, BookResponseScheme, BookUpdateBorrowersScheme, BookResponseBasicScheme

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter()


@router.post("/", response_model=BookResponseBasicScheme, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreateScheme,
    db: AsyncSession = Depends(get_db),
):
    if book_data.book_title_id is not None:
        if book_data.book_title is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only one value of fields 'book_title_id' and 'book_title' can be set",
            )

        async with db.begin():
            book = await BookCopyService.create_book_copy(db, book_data.id, book_data.book_title_id)
    else:
        async with db.begin():
            book = await BookCompositeService.create_book_copy_with_book_title(db, book_data.id, book_data.book_title)

    return book
