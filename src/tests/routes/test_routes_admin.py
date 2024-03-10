import pytest

from src.tests.conftest import create_user_db_admin


def test_admin_update_user_success(client, session):
    # Setup: Create a user
    new_user = create_user_db_admin(session)
    user_id = new_user.id

    # Perform the test with the dynamically obtained user_id
    update_payload = {"username": "new_example", "email": "new_example@example.com"}
    response = client.patch(f"/api/admin/users/{user_id}", json=update_payload)

    assert response.status_code == 200



# def test_admin_update_user_unauthorized(client, user, session):
#     # Setup: Create a user without admin privileges
#     create_user_db(user, session)
#
#     # Test: Attempt to update the user's data without admin authorization
#     response = client.patch("/api/admin/users/1", json={"username": "unauth_example"})
#
#     # Verify: The update is rejected due to lack of authorization
#     assert response.status_code == status.HTTP_401_UNAUTHORIZED
#
#
# @pytest.mark.parametrize("field,value", [
#     ("username", "sh"),  # Too short
#     ("email", "invalid_email"),  # Invalid format
# ])
# def test_admin_update_user_validation(client, user, session, field, value):
#     # Setup: Create a user and mark the test client as admin
#     create_user_db(user, session)
#     admin_token = login_user_token_created(user, session)['access_token']
#     headers = {"Authorization": f"Bearer {admin_token}"}
#
#     # Test: Attempt to update the user with invalid data
#     response = client.patch("/api/admin/users/1", json={field: value}, headers=headers)
#
#     # Verify: The request fails due to validation error
#     assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
