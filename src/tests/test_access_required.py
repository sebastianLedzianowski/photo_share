import asyncio
from src.database.models import User
import pytest
from fastapi import HTTPException, status
from src.services.auth import auth_service


admin_user = User(admin=True)
non_admin_user = User(admin=False)
moderator_user = User(moderator=True)
non_moderator_user = User(moderator=False)


@pytest.mark.asyncio
async def test_admin_required_success():
    async def mock_func(current_user):
        return True
    result = await auth_service.admin_required(mock_func)(current_user=admin_user)
    assert result is True

@pytest.mark.asyncio
async def test_admin_required_failure():
    async def mock_func(current_user):
        return True
    with pytest.raises(HTTPException) as ex:
        await auth_service.admin_required(mock_func)(current_user=non_admin_user)
    assert ex.value.status_code == status.HTTP_403_FORBIDDEN

@pytest.mark.asyncio
async def test_moderator_required_success():
    async def mock_func(current_user):
        return True
    result = await auth_service.moderator_required(mock_func)(current_user=moderator_user)
    assert result is True

@pytest.mark.asyncio
async def test_moderator_required_failure():
    async def mock_func(current_user):
        return True
    with pytest.raises(HTTPException) as ex:
        await auth_service.moderator_required(mock_func)(current_user=non_moderator_user)
    assert ex.value.status_code == status.HTTP_403_FORBIDDEN
