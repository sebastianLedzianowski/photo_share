from fastapi import Depends
from src.services.auth import auth_service


@auth_service.admin_required
async def get_user_and_validate(current_user: dict = Depends(auth_service.get_current_user)):

    """
    Validates the current user and obtains their user ID.

    Parameters:
        current_user (dict, optional): Dictionary representing information about the current user. 
                                       Defaults to using the `get_current_user` function from the `auth_service`.

    Returns:
        dict: A dictionary containing the user ID.
    """
    return {"user_id": current_user.email}