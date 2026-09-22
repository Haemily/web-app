import re
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


CONTACT_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|(?<!\d)(?:\+?65[ -]?)?[689]\d{3}[ -]?\d{4}(?!\d)")


def public_text(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("Text cannot be blank")
    if CONTACT_PATTERN.search(value):
        raise ValueError("Remove phone numbers and email addresses from public text")
    return value


class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=24)
    password: str = Field(min_length=1, max_length=128)


class ContentIn(BaseModel):
    title: str = Field(min_length=5, max_length=160)
    body: str = Field(min_length=10, max_length=5000)
    format: Literal["Question", "Story", "Discussion"]
    topic: str = Field(min_length=2, max_length=60)
    stage: str = Field(min_length=2, max_length=60)

    _check_title = field_validator("title")(public_text)
    _check_body = field_validator("body")(public_text)


class CommentIn(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: int | None = None

    _check_body = field_validator("body")(public_text)


class ActivityIn(BaseModel):
    title: str = Field(min_length=5, max_length=160)
    description: str = Field(min_length=10, max_length=2000)
    kind: Literal["Meetup", "Open jio"]
    starts_at: datetime
    location: str = Field(min_length=2, max_length=100)

    _check_title = field_validator("title")(public_text)
    _check_description = field_validator("description")(public_text)
    _check_location = field_validator("location")(public_text)

    @field_validator("starts_at")
    @classmethod
    def timezone_required(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("Include a timezone in starts_at")
        return value


class HelpRequestIn(BaseModel):
    title: str = Field(min_length=5, max_length=120)
    description: str = Field(min_length=10, max_length=2000)
    area: str = Field(min_length=2, max_length=80)
    non_medical_acknowledged: Literal[True]

    _check_title = field_validator("title")(public_text)
    _check_description = field_validator("description")(public_text)
    _check_area = field_validator("area")(public_text)


class ReportIn(BaseModel):
    target_type: Literal["content", "activity", "help_request"]
    target_id: int = Field(gt=0)
    reason: Literal["unsafe", "medical", "privacy", "other"]
    details: str = Field(default="", max_length=1000)

    _check_details = field_validator("details")(public_text)


class ReportStatusIn(BaseModel):
    status: Literal["open", "reviewed", "closed"]
