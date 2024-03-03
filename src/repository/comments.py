from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Comment, User
from src.schemas import CommentModel, PictureDB


async def create_comment(body: CommentModel, picture: PictureDB, user: User, db: Session) -> Comment:
    comment = Comment(user_id=user.id,
                      picture_id=picture.id,
                      content=body.content,
                      created_at=datetime.now(),
                      update_at=datetime.now()
                      )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comment(comment_id: int, user: User, db: Session) -> Comment:
    return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()


async def update_comment(comment_id: int, body: CommentModel, user: User, db: Session) -> Comment | None:
    comment = db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()
    if comment:
        comment.content = body.content
        comment.updated_at = datetime.now()
        db.commit()
    return comment


async def remove_comment(comment_id: int, user: User, db: Session) -> None | dict:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if user.admin or user.moderator:
        if comment:
            db.delete(comment)
            db.commit()
        return comment
    else:
        return {"message": "You can't delete the comment."}

