from datetime import datetime
from typing import Annotated
from sqlalchemy.orm import mapped_column
from sqlalchemy import String, DateTime
from pydantic import AwareDatetime, Field


exactly_n_digits_regex = lambda number: "^\d{" + number + r"}$"
exactly_n_digits_field = lambda number: Field(
    min_length=number, max_length=number, pattern=exactly_n_digits_regex(number)
)

# ****************** SCHEMES TYPES ****************************
"""
Change here probably should have similar change in DB TYPES. 
"""
serial_number = Annotated[str, exactly_n_digits_field(6)]
name_literal = Annotated[str, Field(max_length=255)]

datetime_tz = AwareDatetime
# *************************************************************

# ********************* DB TYPES ******************************
"""
Change here probably should have similar change in SCHEMES TYPES. 
Change here will induce migration - it's expected behaviour!
"""

serial_number_db = Annotated[str, mapped_column(String(6))]
name_literal_db = Annotated[str, mapped_column(String(255))]

datetime_tz_db = Annotated[datetime, DateTime(timezone=True)]
# *************************************************************