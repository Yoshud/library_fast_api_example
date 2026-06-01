from datetime import datetime
from typing import Annotated, Literal

from sqlalchemy.orm import DeclarativeBase, declared_attr

class Base(DeclarativeBase):
    id: any

    # Generate __tablename__ automatically from class name
    @declared_attr.classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


serial_number = Annotated[str, Literal["length=6", "digits-only"]]
datetime_tz = Annotated[datetime, Literal["timezone-aware"]]
