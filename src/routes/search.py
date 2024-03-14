from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from typing import List, Optional

from src.database.db import get_db
from src.schemas import PictureResponse
from src.repository import search as repository_search


router = APIRouter(prefix="/search", tags=["search"])


@router.post("/pictures", response_model=List[PictureResponse])
async def search_pictures(
        keyword: Optional[str] = None,
        sort_by: Optional[str] = "created_at",
        sort_order: Optional[str] = "desc",
        db: Session = Depends(get_db)
):
    """
    Searches for images matching the provided keyword and returns a list of image responses.
    The search considers both image descriptions and tags assigned to images.
    Results can be sorted by rating or creation date, in ascending or descending order.

    Args:
        keyword (Optional[str]): The keyword used to filter images. Defaults to `None`.
        sort_by (Optional[str]): The field by which results should be sorted. Possible values are "rating" or "created_at". Defaults to "created_at".
        sort_order (Optional[str]): Specifies whether results should be sorted in ascending ("asc") or descending ("desc") order. Defaults to "desc".
        db (Session): Database session, a dependency injected by FastAPI.

    Returns:
        List[PictureResponse]: A list of PictureResponse objects representing images that meet the search criteria.
    """
    pictures = await repository_search.search_pictures(keyword=keyword, sort_by=sort_by, sort_order=sort_order, db=db)

    return pictures
