from pydantic import BaseModel, Field
from datetime import date


class MessageCreate(BaseModel):
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$", description="Date in YYYY-MM-DD format")
    message: str = Field(..., min_length=1, max_length=1000)


class MessageUpdate(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)


class MessageResponse(BaseModel):
    date: str
    message: str


class MessageListResponse(BaseModel):
    messages: list[MessageResponse]


class UserResponse(BaseModel):
    email: str
    authenticated: bool = True


class ErrorResponse(BaseModel):
    detail: str
