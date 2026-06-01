from pydantic import BaseModel, ConfigDict


class BookTitleCreateScheme(BaseModel):
    title: str
    author: str


class BookTitleUpdateScheme(BaseModel):
    title: str|None = None
    author: str|None = None


class BookTitleResponseScheme(BaseModel):
    id: int
    title: str
    author: str

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
