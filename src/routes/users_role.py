from fastapi import APIRouter, Depends
from src.services.auth_admin import get_user_and_validate
from src.services.auth_moderator import get_user_and_validate as get_moderator_and_validate

router = APIRouter(prefix='/access', tags=["sdbh"])

@router.get("/admin")
async def some_endpoint(current_user_and_admin=Depends(get_user_and_validate)):
    """
    Handles GET request to the /access/admin endpoint.

    Parameters:
        current_user_and_admin: User and their permissions obtained through the get_user_and_validate function.

    Returns:
        dict: A dictionary containing a success message and the user ID.
    """
    
    return {"message": "Endpoint reached successfully", "user_id": current_user_and_admin["user_id"]}


@router.get("/moderator")
async def some_endpoint(current_user_and_moderator=Depends(get_moderator_and_validate)):
    """
    Handles GET request to the /access/moderator endpoint.

    Parameters:
        current_user_and_moderator: User and their permissions obtained through the get_moderator_and_validate function.

    Returns:
        dict: A dictionary containing a success message and the user ID.
    """
    return {"message": "Endpoint reached successfully", "user_id": current_user_and_moderator["user_id"]}
