from sqlalchemy import String, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class BookInfo(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(255), unique=False, nullable=False)
    # TODO: there is possibility for book to not have author or have multiple authors and so on - but for now KISS
    author: Mapped[str] = mapped_column(String(255), index=True, unique=False, nullable=False)

    books_copies: Mapped[list["Book"]] = relationship(back_populates="book_info")

    __table_args__ = (
        Index('title', 'author'),
    )
    # We can add things like version, year and so on - but that wasn't part of task
