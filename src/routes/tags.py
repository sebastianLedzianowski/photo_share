from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.schemas import TagModel
from src.database.db import get_db
from src.repository import tags as repository_tags


router = APIRouter(prefix='/tags', tags=["tags"])

@router.post('/', response_model=List[TagModel])
async def create_tags(
        tags: List[str],
        db: Session = Depends(get_db),
):
    """
    Create new tags in the database.

    This endpoint accepts a list of tag names and creates new tag records in the database.
    If a tag with the same name already exists, it will be ignored.

    Parameters:
    - tags (List[str]): A list of tag names to be created.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - List[TagModel]: A list of created tags as TagModel instances, including their database-assigned IDs.
    """
    created_tags = await repository_tags.add_new_tags_to_db(db=db, tags=tags)
    if not created_tags:
        raise HTTPException(status_code=400, detail="Tags could not be created.")
    return created_tags
