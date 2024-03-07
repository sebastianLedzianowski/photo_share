from typing import Type
from sqlalchemy.orm import Session
from src.database.models import Picture


async def upload_description(picture_id: int, description: str, db: Session) -> Picture:

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    picture.description = description
    db.commit()
    return picture


async def get_all_descriptions(skip: int, limit: int, db: Session) -> list[str]:

    return db.query(Picture.description).offset(skip).limit(limit).all()


async def get_one_description(picture_id: int, db: Session) -> Picture:

    return db.query(Picture.description).filter(Picture.id == picture_id).first()


async def update_description(picture_id: int, new_description: str, db: Session) -> Picture | None:

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.description = new_description
        db.commit()
    return picture


async def delete_description(picture_id: int, db: Session) -> Picture | None:

    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.description = None
        db.commit()
    return picture
