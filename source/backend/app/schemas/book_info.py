from pydantic import BaseModel, ConfigDict


class BookInfoCreateScheme(BaseModel):
    title: str
    author: str


class BookInfoUpdateScheme(BaseModel):
    title: str|None = None
    author: str|None = None


class BookInfoResponseScheme(BaseModel):
    id: int
    title: str
    author: str

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
