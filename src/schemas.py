from datetime import datetime
from typing import Optional, List

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

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    """
    Schema for the response after user creation.
    """
    user: UserDb
    detail: str = "User successfully created"


class UserUpdateName(BaseModel):
    username: str = Field(min_length=5, max_length=16)


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


class PictureBase(BaseModel):
    rating: Optional[int] | None
    description: Optional[str] | None


class PictureModel(PictureBase):
    tags: Optional[List[int]]


class PictureDB(BaseModel):

    id: int
    picture_url: str | None
    rating: Optional[int] | None
    description: Optional[str] | None
    created_at: datetime

    class Config:
        from_attributes = True


class PictureUpdate(BaseModel):
    description: Optional[str] | None


class PictureResponse(PictureBase):
    id: int
    picture_url: str | None
    created_at: datetime
    tags: Optional[List[int]]

    class Config:
        orm_mode = True


class PictureSearch(BaseModel):
    keywords: Optional[str] = None
    tags: Optional[List[str]] = None


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


class MessageSend(BaseModel):
    receiver_id: int
    content: str


class CommentModel(BaseModel):
    content: str = Field(min_length=1, max_length=300)


class CommentResponse(CommentModel):
    id: int
    user_id: int
    picture_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

        
class TagModel(BaseModel):
    """
    Schema for tag input during tag creation.
    """
    name: str


class ChangePasswordModel(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


class ResetPasswordModel(BaseModel):
    new_password: str
    confirm_password: str
