from pydantic import BaseModel, ConfigDict, model_validator
from book_info import BookInfoCreateScheme
from source.backend.app.schemas.book_info import BookInfoResponseScheme
from source.backend.app.schemas.user import UserResponseScheme


class BookCreateScheme(BaseModel):
    book_info: BookInfoCreateScheme|None = None
    book_info_id: int|None = None

    @model_validator(mode="after")
    def check_book_info_presence(self) -> "BookCreateScheme":
        # TODO: Test that!
        if self.book_info is not None and self.book_info_id is not None:
            raise ValueError(
                "You need add add only book info or only existed book info id"
            )
        if self.book_info is None and self.book_info_id is None:
            raise ValueError(
                "You need to provide at least book_info or book_info_id"
            )
        return self


class BookUpdateScheme(BaseModel):
    remove_user: bool = False
    user_id: int|None = None
    # Setting remove_user = False and user_id to None will just change nothing

    @model_validator(mode="after")
    def check_user_action(self) -> "BookUpdateScheme":
        # TODO: test that
        if self.remove_user and self.user_id is not None:
            raise ValueError(
                "If you want to remove user - don't provide user_id"
            )
        return self


class BookResponseScheme(BaseModel):
    id: str
    book_info: BookInfoResponseScheme
    user: UserResponseScheme|None

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
