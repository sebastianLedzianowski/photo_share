from fastapi import APIRouter, HTTPException, Depends, status
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, Picture
from src.schemas import CommentModel, CommentResponse
from src.repository import comments as repository_comments
from src.services.auth import auth_service

router = APIRouter(prefix="/comment", tags=["comments"])


@router.get("/{comment_id}", response_model=CommentResponse)
async def read_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    comment = await repository_comments.get_comment(comment_id, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.post("/", response_model=CommentModel, dependencies=[Depends(RateLimiter(times=1, seconds=5))], status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentModel,
        current_picture: Picture,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    return await repository_comments.create_comment(body, current_picture, current_user, db)


@router.put("/{contact_id}", response_model=CommentResponse)
async def update_contact(
        comment_id: int,
        body: CommentModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    comment= await repository_comments.update_comment(comment_id, body, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/{contact_id}", response_model=CommentResponse)
async def remove_contact(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    comment = await repository_comments.remove_comment(comment_id, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment
