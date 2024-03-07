import pytest
from PIL import Image
from io import BytesIO
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from src.services.auth import auth_service
from src.tests.test_routes_auth import login_user_token_created

client = TestClient(app)


def create_mock_picture(width=250, height=250, color=(255, 0, 0)):
    """
    Create a mock picture.

    Args:
    - width (int): Width of the picture.
    - height (int): Height of the picture.
    - color (tuple): RGB color tuple for the picture background.

    Returns:
    - BytesIO: BytesIO object containing the mock picture.
    """

    image = Image.new("RGB", (width, height), color)
    image_bytes_io = BytesIO()
    image.save(image_bytes_io, format="PNG")
    image_bytes_io.seek(0)

    return image_bytes_io


def test_upload_picture(user, session, client):
    new_user = login_user_token_created(user, session)

    mock_picture = create_mock_picture()
    mock_uploaded_file = {"picture": ("test_image.png", mock_picture, "image/png")}

    response = client.post(
        "api/pictures/upload",
        headers={
            'accept': 'application/json',
            "Authorization": f"Bearer {new_user.get('access_token')}"
        },
        files=mock_uploaded_file
    )
    assert response.status_code == 200
    data = response.json()
    print("DATA: ", data)
    assert "id" in data
    assert "picture_url" in data
    assert "rating" in data
    assert "created_at" in data


def test_get_all_pictures(user, session):

    response = client.get("api/pictures/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 1
    assert "id" in data[0]
    assert "picture_url" in data[0]
    assert "rating" in data[0]
    assert "created_at" in data[0]


def test_get_one_picture_found(user, session):

    response = client.get("api/pictures/1")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "picture_url" in data
    assert "rating" in data
    assert "created_at" in data
    assert "user_id" in data


def test_get_one_picture_not_found(user, session, client):

    response = client.get("api/pictures/9999")
    assert response.status_code == 404


def test_update_picture_found(user, session, client):

    new_user = login_user_token_created(user, session)

    mock_picture = create_mock_picture()
    mock_uploaded_file = {"picture": ("test_image.png", mock_picture, "image/png")}

    response = client.put(
        "api/pictures/1",
        headers={
            'accept': 'application/json',
            "Authorization": f"Bearer {new_user.get('access_token')}"
        },
        files=mock_uploaded_file
    )
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "picture_url" in data
    assert "rating" in data
    assert "created_at" in data


def test_update_picture_not_found(user, session):

    new_user = login_user_token_created(user, session)

    mock_picture = create_mock_picture()
    mock_uploaded_file = {"picture": ("test_image.png", mock_picture, "image/png")}

    response = client.put(
        "api/pictures/9999",
        headers={
            'accept': 'application/json',
            "Authorization": f"Bearer {new_user.get('access_token')}"
        },
        files=mock_uploaded_file
    )
    assert response.status_code == 404


def test_delete_picture_found(client, session, user):
    new_user = login_user_token_created(user, session)

    # with patch.object(auth_service, 'r') as r_mock:
    #     r_mock.get.return_value = None

    response = client.delete(
        "api/pictures/1",
        headers={
            'accept': 'application/json',
            "Authorization": f"Bearer {new_user.get('access_token')}"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "picture_url" in data
    assert "rating" in data
    assert "created_at" in data


def test_delete_picture_not_found(user, session, client):
    new_user = login_user_token_created(user, session)

    response = client.delete(
        "api/pictures/9999",
         headers={
             'accept': 'application/json',
             "Authorization": f"Bearer {new_user.get('access_token')}"
            }
         )
    assert response.status_code == 404


if __name__ == "__main__":
    pytest.main()
