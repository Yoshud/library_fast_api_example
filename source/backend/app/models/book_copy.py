from sqlalchemy import ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.book_title import BookTitle
from app.models.user import User
from app.utils.types import datetime_tz_db, serial_number_db


class BookCopy(Base):
    id: Mapped[serial_number_db] = mapped_column(primary_key=True, index=True, autoincrement=False)

    borrowing_time: Mapped[datetime_tz_db | None]

    book_title_id: Mapped[int] = mapped_column(ForeignKey("BookTitle.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("User.id", ondelete="RESTRICT"), default=None)

    book_title: Mapped["BookTitle"] = relationship(back_populates="book_copies")
    user: Mapped["User"] = relationship(back_populates="book_copies")

    @hybrid_property
    def is_borrowed(self) -> bool:
        return self.user_id is not None
