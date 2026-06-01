from pydantic import BaseModel, ConfigDict

from app.models.base import serial_number


class UserCreateScheme(BaseModel):
    name: str


class UserUpdateScheme(BaseModel):
    name: str


class UserResponseScheme(BaseModel):
    id: serial_number
    name: str

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
