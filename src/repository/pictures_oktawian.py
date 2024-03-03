from typing import Type

from sqlalchemy.orm import Session

from src.schemas import PictureUpdate
from src.database.models import Picture, User, Tag


async def upload_picture(url: str, user: User, db: Session) -> Picture:

    picture = Picture(picture_url=url, user_id=user.id)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


async def get_all_pictures(skip: int, limit: int, db: Session) -> list[Type[Picture]]:
    return db.query(Picture).offset(skip).limit(limit).all()


async def get_one_picture(picture_id: int, db: Session) -> Picture:
    return db.query(Picture).filter(Picture.id == picture_id).first()


async def update_picture(picture_id: int, url: str, user: User, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.user_id = user.id
        picture.picture_url = url
        db.commit()
    return picture


async def delete_picture(picture_id: int, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        db.delete(picture)
        db.commit()
    return picture
