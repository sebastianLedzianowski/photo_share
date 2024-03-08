from typing import Type
from sqlalchemy.orm import Session
from src.database.models import Picture, User
from fastapi import HTTPException


async def upload_picture(url: str, version: str, public_id: str, user: User, qr: str, db: Session) -> Picture:
    """
    Asynchronously uploads a picture to the database.

    This function takes a URL, a user object, and a database session. It creates a new
    Picture object with the provided URL and user ID, adds it to the database, commits
    the transaction, and refreshes the session to retrieve the newly created picture.

    Parameters:
    - url (str): The URL of the picture to upload.
    - user (User): The user object associated with the picture.
    - qr (str): The URL for QR code of original picture
    - db (Session): The SQLAlchemy session used to interact with the database.

    Returns:
    - Picture: The newly uploaded Picture object.
    """
    converted_picture_name = f"v{version}/{public_id}"
    picture = Picture(picture_url=url, user_id=user.id, picture_name=converted_picture_name, qr_code_original_picture=qr)
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
        db.refresh(picture)
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


async def upload_edited_picture(picture, edited_url, picture_id, db: Session) -> Picture | None:
    """
    Upload the edited picture to the database and return the edited URL.

    Parameters:
    - picture: The picture object to be updated with the edited URL.
    - edited_url (str): The edited URL of the picture.
    - picture_id (int): The ID of the picture being edited.
    - db (Session): An SQLAlchemy database session instance provided by the FastAPI dependency injection system.

    Returns:
    - str: The edited URL of the picture.

    Raises:
    - HTTPException: If there is an issue committing the changes to the database.
    """

    picture.picture_edited_url = edited_url
    db.commit()

    return edited_url


async def validate_edit_parameters(picture_edit):
    """
    Validate the parameters provided for editing a picture.

    Parameters:
    - picture_edit (PictureEdit): An object containing the parameters for editing the picture. The parameters include:
    - improve (str): A string representing the improvement level. Must be between 0 and 100.
    - contrast (str): A string representing the contrast level. Must be between -100 and 100.
    - unsharp_mask (str): A string representing the unsharp mask value. Must be between 1 and 2000.
    - brightness (str): A string representing the brightness value. Must be between -99 and 100.
    - gamma (str): A string representing the gamma correction value. Must be between -50 and 150.
    - gen_replace (str): A string representing the replacement transformation. If specified, 'gen_remove' should not be provided.
    - gen_remove (str): A string representing the removal transformation. If specified, 'gen_replace' should not be provided.

    Raises:
    - HTTPException: If any of the parameters are invalid or conflicting.
    """

    try:
        if picture_edit.improve != "0":
            improve_value = int(picture_edit.improve)
            if not 0 <= improve_value <= 100:
                raise ValueError("Value of 'improve' must be between 0 and 100.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.contrast != "0":
            contrast_value = int(picture_edit.contrast)
            if not -100 <= contrast_value <= 100:
                raise ValueError("Value of 'contrast' must be between -100 and 100.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.unsharp_mask != "0":
            unsharp_mask_value = int(picture_edit.unsharp_mask)
            if not 1 <= unsharp_mask_value <= 2000:
                raise ValueError("Value of 'unsharp_mask' must be between 1 and 2000.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.brightness != "0":
            brightness_value = int(picture_edit.brightness)
            if not -99 <= brightness_value <= 100:
                raise ValueError("Value of 'brightness' must be between -99 and 100.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.gamma != "0":
            gamma_value = int(picture_edit.gamma)
            if not -50 <= gamma_value <= 150:
                raise ValueError("Value of 'gamma' must be between -50 and 150.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        if picture_edit.gen_replace != "from_null;to_null" and picture_edit.gen_remove != "prompt_null":
            raise HTTPException(status_code=400,
                                detail="You can only specify either gen_replace or gen_remove, not both.")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def parse_transform_effects(picture_edit):
    """
    Parse the transformation effects based on the provided parameters for editing a picture.

    Parameters:
    - picture_edit (PictureEdit): An object containing the parameters for editing the picture.

    Returns:
    - list: A list of dictionaries representing the transformation effects to be applied to the picture.
    """

    transformation = [
        {'effect': f"gen_replace:{picture_edit.gen_replace}"} if picture_edit.gen_replace != "from_null;to_null" else None,
        {'effect': f"gen_remove:{picture_edit.gen_remove}"} if picture_edit.gen_remove != "prompt_null" else None,
        {'effect': f"improve:outdoor:{picture_edit.improve}"} if picture_edit.improve != "0" else None,
        {'effect': f"contrast:{picture_edit.contrast}"} if picture_edit.contrast != "0" else None,
        {'effect': f"unsharp_mask:{picture_edit.unsharp_mask}"} if picture_edit.unsharp_mask != "0" else None,
        {'effect': f"brightness:{picture_edit.brightness}"} if picture_edit.brightness != "0" else None,
        {'effect': f"gamma:{picture_edit.gamma}"} if picture_edit.gamma != "0" else None,
        {'effect': f"grayscale"} if picture_edit.grayscale != False else None,
        {'effect': f"redeye"} if picture_edit.redeye != False else None,
    ]

    transformation = [effect for effect in transformation if effect is not None]

    return transformation
