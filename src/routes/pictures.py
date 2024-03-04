from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException,  UploadFile, File, status
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader

from src.database.db import get_db
from src.database.models import User
from src.schemas import PictureDB, PictureEdit
from src.repository import pictures as repository_pictures
from src.services.auth import auth_service
from src.services.secrets_manager import get_secret

CLOUDINARY_NAME = get_secret("CLOUDINARY_NAME")
CLOUDINARY_API_KEY = get_secret("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = get_secret("CLOUDINARY_API_SECRET")


router = APIRouter(prefix='/pictures', tags=["pictures"])


@router.post("/upload", response_model=PictureDB)
async def upload_picture(
        picture: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
) -> PictureDB:
    """
    Upload a picture to the database.

    This endpoint uploads a picture file to the cloud storage using Cloudinary. It then associates
    the uploaded picture with the current user and saves the picture data to the database.

    Parameters:
    - picture (UploadFile): The picture file to be uploaded.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The URL of the uploaded picture as a PictureDB instance.
    """

    try:
        cloudinary.config(
            cloud_name=CLOUDINARY_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        picture_name = f'picture/{current_user.email}'
        picture = cloudinary.uploader.upload(picture.file, public_id=picture_name, overwrite=True)

        #  WITH PICTURE MODIFICATION - UPLOADED CROPPED WITH BACKGROUND COLOR
        # url = cloudinary.CloudinaryImage(f'picture/{current_user.email}').build_url(background="white", height=250, width=250, crop='pad', version=picture.get('version'))

        #  WITHOUT PICTURE MODIFICATION - UPLOADED AS IT IS

        version = picture.get('version')
        picture_name = picture.get('public_id')

        url = cloudinary.CloudinaryImage(picture_name).build_url(version=version)

        picture_url = await repository_pictures.upload_picture(url=url, version=version, picture_name=picture_name, user=current_user, db=db)
        return picture_url
    


        picture_name = f'picture/{current_user.email}'
        upload_result = cloudinary.uploader.upload(picture.file, public_id=picture_name, overwrite=True)

        version = upload_result.get('version')
        picture_name = upload_result.get('public_id')

        # Budowanie URL za pomocą version i picture_name
        url = cloudinary.CloudinaryImage(picture_name).build_url(version=version)

        picture_url = await repository_pictures.upload_picture(url=url, user=current_user, db=db)
        return picture_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PictureDB])
async def get_all_pictures(
        skip: int = 0,
        limit: int = 20,
        db: Session = Depends(get_db)
):
    """
    Retrieve all pictures from the database.

    This endpoint retrieves all pictures stored in the database, with optional pagination support.

    Parameters:
    - skip (int): The number of pictures to skip.
    - limit (int): The maximum number of pictures to retrieve.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - A list of PictureDB instances representing the retrieved pictures.
    """

    pictures = await repository_pictures.get_all_pictures(skip=skip, limit=limit, db=db)
    return pictures


@router.get("/{picture_id}")
async def get_one_picture(
        picture_id: int,
        db: Session = Depends(get_db)
):
    """
    Retrieve a specific picture from the database.

    This endpoint retrieves a picture with the specified ID from the database.

    Parameters:
    - picture_id (int): The ID of the picture to retrieve.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The PictureDB instance representing the retrieved picture.
    """

    picture = await repository_pictures.get_one_picture(picture_id, db)
    if picture is None:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture


@router.put("/{picture_id}", response_model=PictureDB)
async def update_picture(
        picture_id: int,
        picture: UploadFile = File(),
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
):
    """
    Update a picture in the database.

    This endpoint updates the specified picture in the database with a new picture file.

    Parameters:
    - picture_id (int): The ID of the picture to update.
    - picture (UploadFile): The new picture file to upload.
    - current_user (User): The current user authenticated via the authentication service.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The URL of the updated picture as a PictureDB instance.
    """

    try:
        cloudinary.config(
            cloud_name=CLOUDINARY_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        picture = cloudinary.uploader.upload(picture.file, public_id=f'picture/{current_user.email}', overwrite=True)

        #  WITH PICTURE MODIFICATION - UPLOADED CROPPED WITH BACKGROUND COLOR
        # url = cloudinary.CloudinaryImage(f'picture/{current_user.email}').build_url(background="white", height=250, width=250, crop='pad', version=picture.get('version'))

        #  WITHOUT PICTURE MODIFICATION - UPLOADED AS IT IS
        url = cloudinary.CloudinaryImage(f'picture/{current_user.email}').build_url(version=picture.get('version'))

        picture_url = await repository_pictures.update_picture(picture_id=picture_id, url=url, user=current_user, db=db)

        if picture_url is None:
            raise HTTPException(status_code=404, detail="Picture not found")
        return picture_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{picture_id}", response_model=PictureDB)
async def delete_picture(
        picture_id: int,
        db: Session = Depends(get_db)
):
    """
    Delete a picture from the database.

    This endpoint deletes the specified picture from the database.

    Parameters:
    - picture_id (int): The ID of the picture to delete.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency
      injection system.

    Returns:
    - The PictureDB instance representing the deleted picture.
    """

    picture = await repository_pictures.delete_picture(picture_id, db)

    if picture is None:
        raise HTTPException(status_code=404, detail="Picture not found")
    return picture

@router.post("/edit/{id}", status_code=status.HTTP_201_CREATED)
async def edit_picture(picture_id: int, picture_edit: PictureEdit, db: Session = Depends(get_db)):
    """
    Edit a picture based on the specified parameters.

    Parameters:
    - picture_id (int): The ID of the picture to be edited.
    - picture_edit (PictureEdit): An object containing the parameters for editing the picture. The parameters include:
        - improve (str): A string representing the improvement level. Must be between 0 and 100.
        - contrast (str): A string representing the contrast level. Must be between -100 and 100.
        - unsharp_mask (str): A string representing the unsharp mask value. Must be between 1 and 2000.
        - brightness (str): A string representing the brightness value. Must be between -99 and 100.
        - gamma (str): A string representing the gamma correction value. Must be between -50 and 150.
        - grayscale (bool): A boolean indicating whether to apply grayscale effect. If True, the effect is applied.
        - redeye (bool): A boolean indicating whether to apply red-eye effect. If True, the effect is applied.
        - gen_replace (str): A string representing the replacement transformation. If specified, 'gen_remove' should not be provided.
        - gen_remove (str): A string representing the removal transformation. If specified, 'gen_replace' should not be provided.
    - db (Session, optional): An SQLAlchemy database session instance provided by the FastAPI dependency injection system.

    Returns:
    - The edited URL of the picture as a string.

    Raises:
    - HTTPException: If an error occurs during the editing process, such as validation failure or database access issues.
    """


    await repository_pictures.validate_edit_parameters(picture_edit)

    try:
        cloudinary.config(
            cloud_name=CLOUDINARY_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET,
            secure=True
        )

        picture = await repository_pictures.get_one_picture(picture_id, db)
        transformation = await repository_pictures.parse_transform_effects(picture_edit)

        edited_url = cloudinary.utils.cloudinary_url(
            picture.picture_name, transformation=transformation
        )[0]

        return await repository_pictures.upload_edited_picture(picture, edited_url, picture_id, db)

    except Exception as e:
      raise HTTPException(status_code=500, detail=str(e))