from typing import List
from fastapi import APIRouter, Depends, HTTPException,  UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.schemas import PictureDB
from src.repository import pictures_oktawian as repository_pictures_oktawian
from src.services.auth import auth_service
from src.services.secrets_manager import get_secret

CLOUDINARY_NAME = get_secret("CLOUDINARY_NAME")
CLOUDINARY_API_KEY = get_secret("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = get_secret("CLOUDINARY_API_SECRET")


router = APIRouter(prefix='/pictures', tags=["pictures"])


@router.post("/upload/", response_model=PictureDB)
async def upload_picture(
        picture: UploadFile = File(...),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
) -> PictureDB:

    try:
        cloudinary.config(
            cloud_name=CLOUDINARY_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        picture = cloudinary.uploader.upload(picture.file)
        url = cloudinary.CloudinaryImage(f'picture/{current_user.email}').build_url(crop='fill', version=picture.get('version'))

        picture_url = await repository_pictures_oktawian.upload_picture(url=url, user=current_user, db=db)
        return picture_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PictureDB])
async def get_all_pictures(
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
):

    pictures = await repository_pictures_oktawian.get_all_pictures(skip=skip, limit=limit, db=db)
    return pictures


@router.get("/{id}")
async def get_one_picture(
        picture_id: int,
        db: Session = Depends(get_db)
):

    picture = await repository_pictures_oktawian.get_one_picture(picture_id, db)
    if picture is None:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.put("/{id}", response_model=PictureDB)
async def update_picture(
        picture_id: int,
        picture: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    try:
        cloudinary.config(
            cloud_name=CLOUDINARY_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        picture = cloudinary.uploader.upload(picture.file)
        url = cloudinary.CloudinaryImage(f'picture/{current_user.email}').build_url(crop='fill',version=picture.get('version'))

        picture_url = await repository_pictures_oktawian.update_picture(picture_id=picture_id, url=url, user=current_user, db=db)
        if picture_url is None:
            raise HTTPException(status_code=404, detail="Picture not found")
        return picture_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}", response_model=PictureDB)
async def delete_picture(
        picture_id: int,
        db: Session = Depends(get_db)
):

    picture = await repository_pictures_oktawian.delete_picture(picture_id, db)
    if picture is None:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture
