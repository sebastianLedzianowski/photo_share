from fastapi import HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status
from src.database.models import User
from src.services.auth import auth_service
from src.schemas import AdminUserUpdateModel


async def admin_required(current_user: User = Depends(auth_service.get_current_user)):
    '''
    test function that checks if the user is admin, will de deleted if not needed
    '''

    if not current_user.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Requires admin privileges."
        )
    return current_user


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
