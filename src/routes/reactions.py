from fastapi import APIRouter, status, Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import ReactionName
from src.services.auth import auth_service
from src.repository import reactions as repository_reactions


router = APIRouter(prefix="/reactions", tags=["reactions"])


@router.post("/{reaction}", status_code=status.HTTP_201_CREATED)
async def add_reaction_to_comment(
        comment_id: int,
        reaction: ReactionName,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    return await repository_reactions.add_reaction_to_comment(comment_id, reaction, current_user, db)


@router.delete("/{reaction}")
async def remove_reaction(
        comment_id: int,
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    return await repository_reactions.remove_reaction_from_comment(comment_id, current_user, db)


@router.get("/{comment_id}/")
async def get_reactions(
        comment_id: int,
        db: Session = Depends(get_db)
):
    comment = await repository_reactions.get_reactions(comment_id, db)
    return comment


@router.get("/number/{comment_id}")
async def get_number_of_reactions(
        comment_id: int,
        db: Session = Depends(get_db)
):
    comment = await repository_reactions.get_number_of_reactions(comment_id, db)
    return comment
