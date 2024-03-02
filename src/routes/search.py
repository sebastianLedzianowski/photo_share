from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import List, Optional
from datetime import datetime

from src.database.models import Picture, Tag
from src.database.db import get_db
from src.schemas import PictureResponse, PictureSearch


router = APIRouter()


@router.post("/search", response_model=List[PictureResponse])
async def search_pictures(
    search_params: PictureSearch,
    rating: Optional[int] = None,
    added_after: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """
    Search for pictures based on the given keywords or tags, with optional filters for rating and added date.

    Args:
        search_params (PictureSearch): The search parameters, which include keywords and/or tags.
        rating (Optional[int], optional): The minimum rating for the pictures. Defaults to None.
        added_after (Optional[datetime], optional): The earliest added date for the pictures. Defaults to None.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        List[PictureResponse]: A list of pictures matching the search criteria.
    """
    query = db.query(Picture)

    if search_params.keywords:
        # Search by keywords in the picture description
        query = query.filter(Picture.description.ilike(f"%{search_params.keywords}%"))

    if search_params.tags:
        # Search by tags
        tag_query = db.query(Tag)
        tag_ids = [tag.id for tag in tag_query.filter(Tag.name.in_(search_params.tags)).all()]
        query = query.join(Picture.tags).filter(Tag.id.in_(tag_ids))

    if rating is not None:
        # Filter by rating
        query = query.filter(Picture.rating >= rating)

    if added_after is not None:
        # Filter by added date
        query = query.filter(Picture.created_at >= added_after)

    pictures = query.all()

    # Convert the SQLAlchemy models to Pydantic models
    pydantic_pictures = [picture.to_pydantic() for picture in pictures]

    return pydantic_pictures