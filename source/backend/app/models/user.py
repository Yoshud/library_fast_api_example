from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.utils.types import serial_number_db, name_literal_db


class User(Base):
    id: Mapped[serial_number_db] = mapped_column(primary_key=True, index=True)

    name: Mapped[name_literal_db] = mapped_column(unique=False, index=True)

    book_copies: Mapped[list["BookCopy"]] = relationship(back_populates="user")
