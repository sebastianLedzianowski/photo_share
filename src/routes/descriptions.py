from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User
from src.schemas import PictureDescription
from src.repository import descriptions as repository_descriptions
from src.services.auth import auth_service


router = APIRouter(prefix='/descriptions', tags=["descriptions"])


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=PictureDescription)
async def upload_description(
        picture_id: int,
        description: str,
        db: Session = Depends(get_db)
):
    descriptions = await repository_descriptions.upload_description(picture_id=picture_id, description=description, db=db)
    return descriptions


@router.get("/", response_model=List[PictureDescription])
async def get_all_descriptions(
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
):

    descriptions = await repository_descriptions.get_all_descriptions(skip=skip, limit=limit, db=db)
    return descriptions


@router.get("/{picture_id}", response_model=PictureDescription)
async def get_one_description(
        picture_id: int,
        db: Session = Depends(get_db)
):

    description = await repository_descriptions.get_one_description(picture_id=picture_id, db=db)
    if description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return description


@router.put("/{picture_id}", response_model=PictureDescription)
async def update_description(
        picture_id: int,
        new_description: str,
        db: Session = Depends(get_db)
):

    description = await repository_descriptions.update_description(picture_id=picture_id, new_description=new_description, db=db)
    if description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return description


@router.delete("/{picture_id}", response_model=PictureDescription)
async def delete_description(
        picture_id: int,
        db: Session = Depends(get_db)
):

    description = await repository_descriptions.delete_description(picture_id=picture_id, db=db)

    if description is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Picture not found")
    return description
