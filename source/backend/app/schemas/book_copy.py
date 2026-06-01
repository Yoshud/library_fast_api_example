from pydantic import BaseModel, ConfigDict, model_validator

from app.models.base import serial_number
from app.schemas import BookTitleResponseScheme, BookTitleCreateScheme
from app.schemas import UserResponseScheme


class BookCopyCreateScheme(BaseModel):
    id: serial_number
    book_title: BookTitleCreateScheme|None = None
    book_title_id: int|None = None

    @model_validator(mode="after")
    def check_book_title_presence(self) -> "BookCopyCreateScheme":
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


class BookCopyUpdateScheme(BaseModel):
    remove_user: bool = False
    user_id: int|None = None
    # Setting remove_user = False and user_id to None will just change nothing

    @model_validator(mode="after")
    def check_user_action(self) -> "BookCopyUpdateScheme":
        # TODO: test that
        if self.remove_user and self.user_id is not None:
            raise ValueError(
                "If you want to remove user - don't provide user_id"
            )
        return self


class BookCopyResponseScheme(BaseModel):
    id: serial_number
    book_title: BookTitleResponseScheme
    user: UserResponseScheme|None

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
