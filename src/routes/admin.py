from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository.admin import update_user_admin
from src.schemas import UserDb, AdminUserUpdateModel
from src.services.auth import auth_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.patch("/users/{user_id}",
              response_model=UserDb,
              dependencies=[Depends(auth_service.require_role(required_role="admin"))])
async def admin_update_user(user_id: int,
                            body: AdminUserUpdateModel,
                            db: Session = Depends(get_db),
                            ):
    """
    Updates the user identified by the given user id. Only administrators can perform
    this action.

    Args:
        user_id (int): The unique identifier of the user to be updated.
        body (AdminUserUpdateModel): The request body containing the updated user
            data. Only the provided fields will be updated.
        db (Session): The database session dependency injected by FastAPI.

    Returns:
        UserDb: The updated user data as a Pydantic model.

    Raises:
        HTTPException: With a status code of 404 if the user could not be found.
    """
    updated_user = await update_user_admin(user_id=user_id, body=body, db=db)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserDb.from_orm(updated_user)


