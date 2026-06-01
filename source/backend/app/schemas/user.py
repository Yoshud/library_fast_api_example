from pydantic import BaseModel, ConfigDict

from app.utils.types import serial_number, name_literal


class UserCreateScheme(BaseModel):
    name: name_literal


class UserUpdateScheme(BaseModel):
    name: name_literal


class UserResponseScheme(BaseModel):
    id: serial_number
    name: name_literal

    # load data from database using "."
    model_config = ConfigDict(from_attributes=True)
