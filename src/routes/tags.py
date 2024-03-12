from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.schemas import TagModel, TagsResponseModel
from src.repository import tags as repository_tags
from src.database.db import get_db

router = APIRouter(prefix='/tags', tags=["tags"])

@router.post('/', response_model=TagsResponseModel)
async def add_tags(
        picture_id: int, 
        tags: List[str],
        db: Session = Depends(get_db),
):
    """
    Create new tags in the database.

    This endpoint accepts a list of tag names and creates new tag records in the database.
    If a tag with the same name already exists, it will be ignored.

    Parameters:
    - picture_id (int): The ID of the picture to which the tags will be associated.
    - tags (List[str]): A list of tag names to be created.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - TagsResponseModel: A response model containing two lists of TagModel instances,
      representing newly created tags and existing tags in the database.

    Raises:
    - HTTPException: If tags could not be created.
    """
    response = await repository_tags.add_tags_to_db(picture_id=picture_id, tags=tags, db=db)
    if not response:
        raise HTTPException(status_code=400, detail="Tags could not be created.")
    return response
