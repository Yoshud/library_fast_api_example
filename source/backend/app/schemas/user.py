from pydantic import BaseModel, ConfigDict


class UserCreateScheme(BaseModel):
    name: str


class UserUpdateScheme(BaseModel):
    name: str


class UserResponseScheme(BaseModel):
    id: str
    name: str

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
