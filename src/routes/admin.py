from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.database.models import User
from src.repository.admin import update_user_admin, admin_required

from src.database.db import get_db
from src.schemas import UserDb, AdminUserUpdateModel
from src.services.auth import auth_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.patch("/users/{user_id}", response_model=UserDb)
@auth_service.admin_required
async def admin_update_user(user_id: int,
                            body: AdminUserUpdateModel,
                            db: Session = Depends(get_db),
                            # current_user: User = Depends(admin_required)  # test function, will be deleted if not needed
                            ):

    updated_user = await update_user_admin(user_id=user_id, body=body, db=db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDb.from_orm(updated_user)


