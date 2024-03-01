from typing import Type

from sqlalchemy.orm import Session

from src.schemas import PictureModel
from src.database.models import Picture, User, Tag


async def get_all_pictures(skip: int, limit: int, db: Session) -> list[Type[Picture]]:
    return db.query(Picture).offset(skip).limit(limit).all()


async def get_one_picture(picture_id: int, db: Session) -> Picture:
    return db.query(Picture).filter(Picture.id == picture_id).first()


async def upload_picture(body: PictureModel, url: str, user: User, db: Session) -> Picture:
    tags = db.query(Tag).filter(Tag.id.in_(body.tags)).all()
    picture = Picture(**body.dict(), picture_url=url, user_id=user.id, tags=tags)
    db.add(picture)
    db.commit()
    db.refresh(picture)
    return picture


async def update_picture(body: PictureModel, picture_id: int, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        picture.picture_url = body.picture_url
        picture.description = body.description
        db.commit()
    return picture


async def delete_picture(picture_id: int, db: Session) -> Picture | None:
    picture = db.query(Picture).filter(Picture.id == picture_id).first()
    if picture:
        db.delete(picture)
        db.commit()
    return picture
