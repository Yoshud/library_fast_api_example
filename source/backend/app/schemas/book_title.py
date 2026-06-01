from pydantic import BaseModel, ConfigDict

from app.utils.types import name_literal


class BookTitleCreateScheme(BaseModel):
    title: name_literal
    author: name_literal


class BookTitleUpdateScheme(BaseModel):
    title: name_literal|None = None
    author: name_literal|None = None


class BookTitleResponseScheme(BaseModel):
    id: int
    title: name_literal
    author: name_literal

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
