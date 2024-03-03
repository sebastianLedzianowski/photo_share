
from unittest.mock import MagicMock, patch
import pytest

from src.services.auth_admin import auth_service
from src.services.auth_admin import get_user_and_validate


class MockUser:
    def __init__(self, email: str, admin: bool):
        self.email = email
        self.admin = admin


@pytest.mark.asyncio
async def test_get_user_and_validate():

    user_attributes = MockUser(email="test@example.com", admin=True)

    async def mock_get_current_user():
        return user_attributes

    auth_service.get_current_user = MagicMock(side_effect=mock_get_current_user)

  
    with patch.object(auth_service, "admin_required") as mock_admin_required:


        async def mock_function(current_user: dict):
            pass


        decorated_function = auth_service.admin_required(mock_function)

        response = await get_user_and_validate(current_user=user_attributes)

        assert "user_id" in response
        assert response["user_id"] == user_attributes.email

 
        assert mock_admin_required.called
