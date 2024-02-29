from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class UserModel(BaseModel):
    """
    Schema for user input during registration.
    """
    username: str = Field(min_length=5, max_length=16)
    email: EmailStr
    password: str = Field(min_length=6, max_length=20)


class UserDb(BaseModel):
    """
    Schema for user data retrieved from the database.
    """
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    avatar: str | None

    class ConfigDict:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Schema for the response after user creation.
    """
    user: UserDb
    detail: str = "User successfully created"


class TokenModel(BaseModel):
    """
    Schema for the response containing access and refresh tokens.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    """
    Schema for the request containing an email address.
    """
    email: EmailStr


class MessageBase(BaseModel):
    sender_id: int
    receiver_id: int
    content: str


class MessageModel(MessageBase):
    id: int

    class Config:
        from_attributes = True


class MessageResponse(MessageBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

