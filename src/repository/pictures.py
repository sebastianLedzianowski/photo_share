from typing import Type

from sqlalchemy.orm import Session

from src.database.models import Picture, User


async def upload_picture(url: str, user: User, db: Session) -> Picture:
    """
    Asynchronously uploads a picture to the database.

    This function takes a URL, a user object, and a database session. It creates a new
    Picture object with the provided URL and user ID, adds it to the database, commits
    the transaction, and refreshes the session to retrieve the newly created picture.

    Parameters:
    - url (str): The URL of the picture to upload.
    - user (User): The user object associated with the picture.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Picture: The newly uploaded Picture object.
    """

    picture = Picture(picture_url=url, user_id=user.id)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


async def get_all_pictures(skip: int, limit: int, db: Session) -> list[Type[Picture]]:
    """
    Asynchronously retrieves all pictures from the database.

    This function retrieves all pictures stored in the database, with optional
    support for pagination.

    Parameters:
    - skip (int): The number of pictures to skip.
    - limit (int): The maximum number of pictures to retrieve.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - List[Type[Picture]]: A list of Picture objects representing the retrieved pictures.
    """

    return db.query(Picture).offset(skip).limit(limit).all()


async def get_one_picture(picture_id: int, db: Session) -> Picture:
    """
    Asynchronously retrieves a specific picture from the database.

    This function retrieves a picture with the specified ID from the database.

    Parameters:
    - picture_id (int): The ID of the picture to retrieve.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Picture: The Picture object representing the retrieved picture.
    """

    return db.query(Picture).filter(Picture.id == picture_id).first()


async def update_picture(picture_id: int, url: str, user: User, db: Session) -> Picture | None:
    """
    Asynchronously updates a picture in the database.

    This function updates the specified picture in the database with a new URL
    and user ID.

    Parameters:
    - picture_id (int): The ID of the picture to update.
    - url (str): The new URL of the picture.
    - user (User): The user object associated with the picture.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Union[Picture, None]: The updated Picture object if successful, otherwise None.
    """

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.user_id = user.id
        picture.picture_url = url
        db.commit()
    return picture


async def delete_picture(picture_id: int, db: Session) -> Picture | None:
    """
    Asynchronously deletes a picture from the database.

    This function deletes the specified picture from the database.

    Parameters:
    - picture_id (int): The ID of the picture to delete.
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Union[Picture, None]: The deleted Picture object if successful, otherwise None.
    """

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        db.delete(picture)
        db.commit()
    return picture
