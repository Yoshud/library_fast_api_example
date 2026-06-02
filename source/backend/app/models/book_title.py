from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.utils.types import name_literal_db


class BookTitle(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[name_literal_db] = mapped_column(unique=False, nullable=False)
    # TODO: there is possibility for book to not have author or have multiple authors and so on - but for now KISS
    author: Mapped[name_literal_db] = mapped_column(index=True, unique=False, nullable=False)

    book_copies: Mapped[list["BookCopy"]] = relationship(back_populates="book_title")  # noqa F821

    __table_args__ = (Index("title", "author"),)
    # We can add things like version, year and so on - but that wasn't part of task
