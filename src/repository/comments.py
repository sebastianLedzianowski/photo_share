from datetime import datetime
from typing import Type

from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.models import Comment, User, Picture, Reaction
from src.schemas import CommentModel, PictureDB, CommentResponse, CommentUpdate


async def create_comment(body: CommentModel, picture: PictureDB, user: User, db: Session) -> Comment:
    comment = Comment(user_id=user.id,
                      picture_id=picture.id,
                      content=body.content,
                      created_at=datetime.now()
                      )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def get_comment(comment_id: int, user: User, db: Session) -> Comment:
    return db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()


async def get_comments(picture_id: int, skip: int, limit: int, db: Session) -> list[Type[Comment]]:
    return db.query(Comment).filter(Comment.picture_id == picture_id).offset(skip).limit(limit).all()


async def update_comment(comment_id: int, body: CommentUpdate, user: User, db: Session) -> Comment | None:
    comment = db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()
    if comment:
        comment.content = body.content
        comment.updated_at = datetime.now()
        db.commit()
    return comment


async def remove_comment(comment_id: int, db: Session) -> Type[Comment]:
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if comment:
        db.delete(comment)
        db.commit()
        return comment


async def add_reaction_to_comment(comment_id: int, reaction: str, user: User, db: Session):
    async def add_reaction_to_comment(comment_id: int, reaction: str, user: User, db: Session):
        reaction_record = db.query(Reaction).filter(Reaction.comment_id == comment_id).first()
        if not reaction_record:
            new_reaction = Reaction(comment_id=comment_id, data={reaction: [user.id]})
            db.add(new_reaction)
        else:
            reaction_data = reaction_record.data
            users_id = [user_id for users in reaction_data.values() for user_id in users]
            if user.id in users_id:
                return {"message": "User already reacted to the comment"}
            if reaction not in reaction_data:
                reaction_data[reaction] = [user.id]
            else:
                reaction_data[reaction].append(user.id)
            db.query(Reaction).filter(Reaction.comment_id == comment_id).update({"data": reaction_data})
        db.commit()
        return {"message": "The reaction was created"}

