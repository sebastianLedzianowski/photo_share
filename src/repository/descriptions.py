from sqlalchemy.orm import Session
from src.database.models import Picture
from fastapi import HTTPException


async def upload_description(picture_id: int, description: str, db: Session) -> Picture:
    """
    Upload the description of a picture in the database.

    This function upload the description of a picture with the given ID in the database.

    Parameters:
    - picture_id (int): The ID of the picture whose description is to be updated.
    - description (str): The new description to be assigned to the picture.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Picture: The updated Picture object with the new description.
    """

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if not picture:
        raise HTTPException(status_code=404, detail="Picture not found")

    picture.description = description
    db.commit()
    return picture


async def get_all_descriptions(skip: int, limit: int, db: Session) -> list[str]:
    """
    Retrieves descriptions of pictures from the database.

    This function retrieves descriptions of pictures from the database, skipping the
    specified number of records and limiting the number of records returned.

    Parameters:
    - skip (int): The number of records to skip.
    - limit (int): The maximum number of records to return.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - List[str]: A list of descriptions of pictures.
    """

    return db.query(Picture.description).offset(skip).limit(limit).all()


async def get_one_description(picture_id: int, db: Session) -> str:
    """
    Retrieves the description of a specific picture from the database.

    This function retrieves the description of a picture with the given ID from the database.

    Parameters:
    - picture_id (int): The ID of the picture whose description is to be retrieved.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Optional[Picture]: The Picture object containing the description, or None if not found.
    """

    return db.query(Picture.description).filter(Picture.id == picture_id).first()


async def update_description(picture_id: int, new_description: str, db: Session) -> Picture | None:
    """
    Updates the description of a picture in the database.

    This function updates the description of a picture with the given ID in the database.

    Parameters:
    - picture_id (int): The ID of the picture whose description is to be updated.
    - new_description (str): The new description to be assigned to the picture.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Optional[Picture]: The updated Picture object with the new description, or None if picture not found.
    """

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.description = new_description
        db.commit()
    return picture


async def delete_description(picture_id: int, db: Session) -> Picture | None:
    """
    Deletes the description of a picture in the database.

    This function deletes the description of a picture with the given ID in the database.

    Parameters:
    - picture_id (int): The ID of the picture whose description is to be deleted.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Optional[Picture]: The Picture object after deleting the description, or None if picture not found.
    """

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.description = None
        db.commit()
    return picture
