from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.managers.basic_managers.book_copy_manager import BookCopyManager
from app.managers.composite_managers.book_manager import (
    BookManager,
    BookManagerAlreadyBorrowedError,
    BookManagerBookCopyNotFoundError,
    BookManagerUserNotFoundError,
)
from app.repositories.book_copy_repository import (
    BookCopyRepositoryDuplicateIdError,
    BookCopyRepositoryNoBookInfoError,
)
from app.schemas import BookCreateScheme, BookResponseBasicScheme, BookResponseScheme, BookUpdateBorrowersScheme
from app.utils.types import serial_number

router = APIRouter()


# TODO: Add HATEOS


@router.post("/", response_model=BookResponseBasicScheme, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreateScheme,
    db: Annotated[AsyncSession, Depends(get_db)],
    book_manager: Annotated[BookManager, Depends()],
    book_copy_manager: Annotated[BookCopyManager, Depends()],
):
    # "bad" cases are supported by pydantic
    try:
        if book_data.book_title_id is not None:
            return await book_copy_manager.create_book_copy(db, book_data.id, book_data.book_title_id)

        return await book_manager.create_book_copy_with_book_title(db, book_data.id, book_data.book_title)
    except BookCopyRepositoryDuplicateIdError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"There is already book copy with serial number {book_data.id} in DB",
        ) from e
    except BookCopyRepositoryNoBookInfoError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND_CONFLICT, detail=f"Book title id {book_data.book_title_id} not found"
        ) from e


@router.get("/", response_model=list[BookResponseScheme])
async def get_books(
    db: Annotated[AsyncSession, Depends(get_db)],
    book_copy_manager: Annotated[BookCopyManager, Depends()],
    skip: int = 0,
    limit: int = 100,
):
    books = await book_copy_manager.get_book_copies_with_details(db, skip, limit)
    return books


@router.get(
    "/{book_id}", response_model=BookResponseScheme, responses={404: {"description": "Book is not found in database"}}
)
async def get_book(
    db: Annotated[AsyncSession, Depends(get_db)],
    book_copy_manager: Annotated[BookCopyManager, Depends()],
    book_id: serial_number,
):
    book = await book_copy_manager.get_book_copy_with_details(db, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Boook not found",
        )
    return book


@router.put(
    "/",
    response_model=list[BookResponseBasicScheme],
    responses={
        404: {"description": "Book copy or User not found"},
        409: {"description": "Some book is borrowed by somebody else"},
    },
)
async def update_borrowers(
    db: Annotated[AsyncSession, Depends(get_db)],
    book_manager: Annotated[BookManager, Depends()],
    borrower_update_data: BookUpdateBorrowersScheme,
):
    try:
        books = await book_manager.update_books_borrowers(db, borrower_update_data)
        return books
    except BookManagerAlreadyBorrowedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book {e.book_copy_id} is already borrowed by user {e.already_borrowing_user_id} - all operations cancelled",
        ) from e
    except BookManagerUserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more users is not found - all operations cancelled",
        ) from e
    except BookManagerBookCopyNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book {e.book_copy_id} is not found - all operations cancelled",
        ) from e
