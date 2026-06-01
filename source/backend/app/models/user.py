from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, serial_number


class User(Base):
    id: Mapped[serial_number] = mapped_column(String(6), primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), unique=False, index=True)

    books: Mapped[list["BookCopy"]] = relationship(back_populates="user")
