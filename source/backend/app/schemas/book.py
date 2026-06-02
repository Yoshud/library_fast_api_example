from pydantic import BaseModel, ConfigDict, model_validator

from app.utils.types import serial_number
from app.schemas import BookTitleResponseScheme, BookTitleCreateScheme
from app.schemas import UserResponseScheme


class BookCreateScheme(BaseModel):
    id: serial_number
    book_title: BookTitleCreateScheme|None = None
    book_title_id: int|None = None

    @model_validator(mode="after")
    def check_book_title_presence(self) -> "BookCreateScheme":
        # TODO: Test that!
        if self.book_title is not None and self.book_title_id is not None:
            raise ValueError(
                "You need add add only book info or only existed book info id"
            )
        if self.book_title is None and self.book_title_id is None:
            raise ValueError(
                "You need to provide at least book_title or book_title_id"
            )
        return self


class BookUpdateBorrowersScheme(BaseModel):
    update_borrowers_map: dict[serial_number, serial_number | None] # book_copy_id -> user_id or None (returning)


class BookResponseScheme(BaseModel):
    # TODO: check that
    id: serial_number
    book_title: BookTitleResponseScheme
    user: UserResponseScheme|None

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)

class BookResponseBasicScheme(BaseModel):
    id: serial_number
    book_title_id: BookTitleResponseScheme
    user_id: UserResponseScheme|None

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
