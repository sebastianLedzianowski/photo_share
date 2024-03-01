from typing import List

from fastapi import APIRouter, Depends, HTTPException, status,  UploadFile, File
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.conf.config import settings
from src.database.db import get_db
from src.database.models import User
from src.schemas import PictureModel, PictureResponse
from src.repository import pictures_oktawian as repository_pictures_oktawian
from src.services.auth import auth_service
from src.services.secrets_manager import get_secret

CLOUDINARY_NAME = get_secret("CLOUDINARY_NAME")
CLOUDINARY_API_KEY = get_secret("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = get_secret("CLOUDINARY_API_SECRET")


router = APIRouter(prefix='/pictures', tags=["pictures"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PictureModel)
async def upload_picture(
        body: PictureModel,
        file: UploadFile = File(),
        user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):

    cloudinary.config(
        cloud_name=CLOUDINARY_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )

    r = cloudinary.uploader.upload(file.file, public_id=f'contact_book/{user.email}', overwrite=True)
    src_url = cloudinary.CloudinaryImage(f'contact_book/{user.email}') \
        .build_url(width=250, height=250, crop='fill', version=r.get('version'))

    return await repository_pictures_oktawian.upload_picture(body, user, db)


@router.get("/", response_model=List[PictureResponse])
async def get_all_pictures(
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
):

    pictures = await repository_pictures_oktawian.get_all_pictures(skip, limit, db)
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


@router.put("/{id}", response_model=PictureResponse)
async def update_picture(
        body: PictureModel,
        picture_id: int,
        db: Session = Depends(get_db)
):

    picture = await repository_pictures_oktawian.update_picture(body, picture_id, db)
    if picture is None:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.delete("/{id}", response_model=PictureResponse)
async def delete_picture(
        picture_id: int,
        db: Session = Depends(get_db)
):

    picture = await repository_pictures_oktawian.delete_picture(picture_id, db)
    if picture is None:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture
