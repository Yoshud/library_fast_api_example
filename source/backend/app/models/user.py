from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class User(Base):
    id: Mapped[str] = mapped_column(String(6), primary_key=True, index=True) # 6 cyfr

    name: Mapped[str] = mapped_column(String(255), unique=False, index=True)

    books: Mapped[list["Book"]] = relationship(back_populates="user")
