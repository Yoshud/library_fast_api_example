from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Book(Base):
    id: Mapped[str] = mapped_column(String(6), primary_key=True, index=True) # 6 cyfr

    book_info_id: Mapped[int] = mapped_column(ForeignKey("bookinfo.id", ondelete="RESTRICT"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="RESTRICT"), nullable=True, default=None)

    book_info: Mapped["BookInfo"] = relationship(back_populates="books_copies")
    user: Mapped["User"] = relationship(back_populates="books")
