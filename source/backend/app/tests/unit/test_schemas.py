import pytest
from pydantic import ValidationError

from app.schemas.book import BookCreateScheme
from app.schemas.book_title import BookTitleCreateScheme


def test_book_create_scheme_both_present():
    with pytest.raises(ValidationError, match="You need add add only book info or only existed book info id"):
        BookCreateScheme(id="123456", book_title=BookTitleCreateScheme(title="Title", author="Author"), book_title_id=1)


def test_book_create_scheme_none_present():
    with pytest.raises(ValidationError, match="You need to provide at least book_title or book_title_id"):
        BookCreateScheme(id="123456")


def test_book_create_scheme_only_book_title():
    scheme = BookCreateScheme(id="123456", book_title=BookTitleCreateScheme(title="Title", author="Author"))
    assert scheme.book_title is not None
    assert scheme.book_title.title == "Title"
    assert scheme.book_title.author == "Author"
    assert scheme.book_title_id is None


def test_book_create_scheme_only_book_title_id():
    scheme = BookCreateScheme(id="123456", book_title_id=1)
    assert scheme.book_title is None
    assert scheme.book_title_id == 1
