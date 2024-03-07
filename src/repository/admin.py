from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import AdminUserUpdateModel


async def update_user_admin(user_id: int, body: AdminUserUpdateModel, db: Session):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data_dict = body.dict(exclude_unset=True)
    for key, value in update_data_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user
