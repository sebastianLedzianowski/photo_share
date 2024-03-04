from sqlalchemy import or_, func
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List, Optional, Dict
from datetime import datetime

from src.database.models import Picture, Tag, User
from src.database.db import get_db
from src.schemas import PictureResponse, PictureSearch, UserResponse
from src.services.auth import Auth


get_current_user = Auth.get_current_user


router = APIRouter()
    
    
@router.post("/pictures/search", tags=["pictures"], response_model=List[PictureResponse])
async def search_pictures(
    search_params: PictureSearch,
    rating: Optional[int] = None,
    added_after: Optional[datetime] = None,
    sort_by: Optional[str] = "created_at",
    sort_order: Optional[str] = "desc",
    db: Session = Depends(get_db),
):
    """
    Search for pictures based on the given keywords or tags, with optional filters for rating and added date.
    Args:
        search_params (PictureSearch): The search parameters, which include keywords and/or tags.
        rating (Optional[int], optional): The minimum rating for the pictures. Defaults to None.
        added_after (Optional[datetime], optional): The earliest added date for the pictures. Defaults to None.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        sort_by (Optional[str]): The field to sort by. Defaults to "created_at".
        sort_order (Optional[str]): The sort order. Defaults to "desc".
    Returns:
        List[PictureResponse]: A list of pictures matching the search criteria, sorted by the specified field.
    """
    query = db.query(Picture)

    if search_params.keywords:
        query = query.filter(Picture.description.ilike(f"%{search_params.keywords}%"))

    if search_params.tags:
        tag_query = db.query(Tag)
        tag_ids = [tag.id for tag in tag_query.filter(Tag.name.in_(search_params.tags)).all()]
        query = query.join(Picture.tags).filter(Tag.id.in_(tag_ids))

    if rating is not None:
        query = query.filter(Picture.rating >= rating)

    if added_after is not None:
        query = query.filter(Picture.created_at >= added_after)

    if sort_by not in ["rating", "created_at"]:
        sort_by = "created_at"

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"

    pictures = query.order_by(getattr(Picture, sort_by).desc() if sort_order == "desc" else getattr(Picture, sort_by)).all()

    pydantic_pictures = [picture.to_pydantic() for picture in pictures]

    return pydantic_pictures


@router.post("/users/search", tags=["users"], response_model=List[UserResponse])
async def search_users(
    search_params: PictureSearch,
    username: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Search for users based on the given search parameters.

    Args:
        search_params (PictureSearch): The search parameters for pictures, which include keywords and/or tags.
        username (Optional[str], optional): The username of the user to search for. Defaults to None.
        email (Optional[str], optional): The email of the user to search for. Defaults to None.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(get_current_active_user).

    Returns:
        List[UserResponse]: A list of users matching the search criteria.

    Raises:
        HTTPException: If the user is not a moderator or an administrator.
    """
    query = db.query(User)

    if search_params.keywords:
        query = query.filter(
            or_(User.username.ilike(f"%{search_params.keywords}%"),
            User.email.ilike(f"%{search_params.keywords}%")
        )
    )

    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))

    if email:
        query = query.filter(User.email.ilike(f"%{email}%"))

    users = query.all()

    pydantic_users = [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            avatar=user.avatar,
            picture_count=len(user.pictures),
        ) for user in users
    ]

    return pydantic_users


@router.post("/users_by_picture/search", tags=["users"], response_model=List[UserResponse])
async def search_users_by_picture(
    user_id: Optional[int] = None,
    picture_id: Optional[int] = None,
    rating: Optional[int] = None,
    added_after: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):
    """
    Search for users based on the pictures they have added, with optional filters for rating and added date.
    Args:
        user_id (int): The ID of the user who uploaded the pictures.
        rating (Optional[int], optional): The minimum rating for the pictures. Defaults to None.
        added_after (Optional[datetime], optional): The earliest added date for the pictures. Defaults to None.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        current_user (User, optional): The currently authenticated user. Defaults to Depends(get_current_user).
    Returns:
        List[UserResponse]: A list of users matching the search criteria.
    Raises:
        HTTPException: If the user is not a moderator or an administrator.
    """
    if not (current_user.is_moderator or current_user.is_admin):
        raise HTTPException(status_code=403, detail="User filtering is only available to moderators and administrators.")

    query = db.query(Picture.user_id, func.count(Picture.id).label("picture_count"))

    if user_id is not None:
        query = query.filter(Picture.user_id == user_id)

    if picture_id is not None:
        query = query.filter(Picture.rating >= picture_id)

    if rating is not None:
        query = query.filter(Picture.rating >= rating)

    if added_after is not None:
        query = query.filter(Picture.created_at >= added_after)

    query = query.group_by(Picture.user_id)

    users = query.all()

    pydantic_users = [
        UserResponse(
            id=user.user_id,
            username=user.user.username,
            email=user.user.email,
            avatar=user.user.avatar,
            picture_count=user.picture_count,
        ) for user in users
    ]

    return pydantic_users