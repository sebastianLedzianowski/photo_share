from src.tests.conftest import login_user_confirmed_true_and_hash_password
from src.tests.test_routes_auth import login_user_token_created
from PIL import Image
from io import BytesIO


def test_read_users_me(user, session, client):
    token_user = login_user_token_created(user, session)

    response = client.get('/api/users/me/',
                          headers={'Authorization': f'Bearer {token_user.get("access_token")}'},
                          )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email


def test_update_avatar_user(user, session, client, monkeypatch):
    new_user = login_user_token_created(user, session)

    width, height = 250, 250
    image = Image.new("RGB", (width, height), (255, 0, 0))

    image_bytes_io = BytesIO()
    image.save(image_bytes_io, format="PNG")
    image_bytes_io.seek(0)

    mock_uploaded_file = {"file": ("test_image.png", image_bytes_io, "image/png")}

    response = client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {new_user.get('access_token')}"},
        files=mock_uploaded_file
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == user.username
    assert data["email"] == user.email
    assert "created_at" in data
    assert "avatar" in data


def test_list_all_users(client, user, session):
    # Create a user in the database for testing
    login_user_confirmed_true_and_hash_password(user, session)

    # Perform the GET request to list all users
    response = client.get("/api/users/all")

    # Validate the response
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # Ensure at least one user is returned
    assert data[0]["email"] == user.email  # Validate the email of the user returned


def test_update_user_name(client, user, session):
    # Create and log in a user
    login_user_confirmed_true_and_hash_password(user, session)

    # Define new username
    new_username = "new_example"
    user_id = 1  # Assuming this is the ID of the user created above

    # Perform the PATCH request to update the user's name
    response = client.patch(f"/api/users/update/{user_id}", json={"username": new_username})

    # Validate the response
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == new_username


def test_delete_user(client, user, session):
    # Create and log in a user
    login_user_confirmed_true_and_hash_password(user, session)

    user_id = 1  # Assuming this is the ID of the user created above

    # Perform the DELETE request
    response = client.delete(f"/api/users/delete/{user_id}")

    # Validate the response
    assert response.status_code == 204
