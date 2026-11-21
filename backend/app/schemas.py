"""Request and response bodies for the API, validated by Pydantic.
Bad input (missing or empty fields) gets an automatic 422 before any route code runs."""
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class UserOut(BaseModel):
    id: int
    username: str


class UserResponse(BaseModel):
    user: UserOut


class MessageIn(BaseModel):
    """Text to send to the other person; surrounding whitespace is trimmed before the check."""
    body: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=4000)]


class MessageOut(BaseModel):
    id: int
    sender_id: int
    recipient_id: int
    body: str
    created_at: datetime


class MessageList(BaseModel):
    messages: list[MessageOut]
