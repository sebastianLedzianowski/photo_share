from typing import List
from src.services.admin import require_admin
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import CommentModel, CommentResponse, PictureDB, CommentUpdate
from src.repository import comments as repository_comments
from src.services.auth import auth_service

router = APIRouter(prefix="/comments", tags=["comments"])


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


@router.get("/", response_model=List[CommentResponse])
async def read_comments(
        picture_id: int,
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
):
    comment = await repository_comments.get_comments(picture_id, skip, limit, db)
    return comment


@router.post("/", response_model=CommentModel,
             dependencies=[Depends(RateLimiter(times=1, seconds=5))],
             status_code=status.HTTP_201_CREATED)
async def create_comment(
        body: CommentModel,
        current_picture: PictureDB,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    return await repository_comments.create_comment(body, current_picture, current_user, db)


@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
        comment_id: int,
        body: CommentUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    comment = await repository_comments.update_comment(comment_id, body, current_user, db)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return comment


@router.delete("/{comment_id}")
async def remove_comment(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
) -> JSONResponse:
    """Delete comment by id. User can delete only his own comment.

    Args:
        comment_id (int): Comment id
        db (Session): Database session
        current_user (User): Current user

    Returns:
        JSONResponse: Json response with result
    """
    if not current_user.moderator and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail= "Only moderators or administrators can delete comments.")
    comment = await repository_comments.remove_comment(comment_id, current_user, db)
    if comment is None:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"message": "You can't delete the comment."}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "The comment deleted successfully"}
    )


