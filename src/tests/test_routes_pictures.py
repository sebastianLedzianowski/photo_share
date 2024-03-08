import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime

from main import app
from src.services.auth import auth_service
from src.tests.conftest import login_user_token_created, fake_db_for_pictures_test

client = TestClient(app)


def create_x_pictures(fake_db_for_pictures_test, no_of_pictures):
    pictures = []
    for i in range(no_of_pictures):
        picture = fake_db_for_pictures_test["create_picture"](f"test_url{i}", f"test_description{i}", datetime.now())
        pictures.append(picture)
    return pictures


def test_upload_picture(user, session, client, mock_picture):
    new_user = login_user_token_created(user, session)

    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.post(
            "/api/pictures/upload",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {new_user["access_token"]}"
            },
            files=mock_picture1
        )
        data = response.json()

        assert response.status_code == 201, response.text
        assert "id" in data
        assert "picture_url" in data
        assert "rating" in data
        assert "created_at" in data


def test_get_all_pictures(user, session, client, fake_db_for_pictures_test):

    no_of_pictures = 4

    pictures = create_x_pictures(fake_db_for_pictures_test, no_of_pictures)
    for picture in pictures:
        session.add(picture)
    session.commit()

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get("/api/pictures/")
        data = response.json()

        assert response.status_code == 200, response.text
        assert isinstance(data, list)
        assert len(data) == no_of_pictures
        for i in range(no_of_pictures):
            assert data[i]["id"] == pictures[i].id
            assert data[i]["picture_url"] == pictures[i].picture_url
            assert data[i]["description"] == pictures[i].description
            assert "created_at" in data[i]
            assert "rating" in data[i]


def test_get_one_picture_found(user, session, client, fake_db_for_pictures_test):
    no_of_pictures = 4
    no_to_get = no_of_pictures - 1
    pictures = create_x_pictures(fake_db_for_pictures_test, no_of_pictures)
    for picture in pictures:
        print(f"Test_get_one: {picture}")
        session.add(picture)
    session.commit()

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(f"/api/pictures/{no_to_get}")
        data = response.json()

        assert response.status_code == 200, response.text
        assert data["id"] == pictures[no_to_get-1].id
        assert data["picture_url"] == pictures[no_to_get - 1].picture_url
        assert data["description"] == pictures[no_to_get - 1].description
        assert "created_at" in data
        assert "rating" in data


def test_get_one_picture_not_found(user, session, client, fake_db_for_pictures_test):
    no_of_pictures = 4
    no_to_get = no_of_pictures + 100
    pictures = create_x_pictures(fake_db_for_pictures_test, no_of_pictures)
    for picture in pictures:
        session.add(picture)
    session.commit()

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.get(f"api/pictures/{no_to_get}")

        assert response.status_code == 404, response.text


def test_update_picture_found(user, session, client, mock_picture, fake_db_for_pictures_test):
    new_user = login_user_token_created(user, session)
    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}
    no_of_pictures = 4
    no_to_update = no_of_pictures - 1
    pictures = create_x_pictures(fake_db_for_pictures_test, no_of_pictures)
    for picture in pictures:
        session.add(picture)
    session.commit()

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/pictures/{no_to_update}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {new_user["access_token"]}"
            },
            files=mock_picture1
        )
        data = response.json()

        assert response.status_code == 200, response.text
        assert "id" in data
        assert "picture_url" in data
        assert "rating" in data
        assert "created_at" in data


def test_update_picture_not_found(user, session, client, mock_picture, fake_db_for_pictures_test):
    new_user = login_user_token_created(user, session)
    mock_picture1 = {"picture": ("test_image.png", mock_picture, "image/png")}
    no_of_pictures = 4
    no_to_update = no_of_pictures + 100
    pictures = create_x_pictures(fake_db_for_pictures_test, no_of_pictures)
    for picture in pictures:
        session.add(picture)
    session.commit()

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.put(
            f"/api/pictures/{no_to_update}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {new_user["access_token"]}"
            },
            files=mock_picture1
        )

        assert response.status_code == 404, response.text


def test_delete_picture_found(user, session, client, fake_db_for_pictures_test):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures - 1
    pictures = create_x_pictures(fake_db_for_pictures_test, no_of_pictures)
    for picture in pictures:
        session.add(picture)
        print("Picture: ", picture)
    session.commit()

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/pictures/{no_to_delete}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {new_user["access_token"]}"
            }
        )
        data = response.json()

        assert response.status_code == 200, response.text
        assert "id" in data
        assert "picture_url" in data
        assert "rating" in data
        assert "created_at" in data


def test_delete_picture_not_found(user, session, client, fake_db_for_pictures_test):
    new_user = login_user_token_created(user, session)
    no_of_pictures = 4
    no_to_delete = no_of_pictures + 100
    pictures = create_x_pictures(fake_db_for_pictures_test, no_of_pictures)
    for picture in pictures:
        session.add(picture)
    session.commit()

    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        response = client.delete(
            f"/api/pictures/{no_to_delete}",
            headers={
                "accept": "application/json",
                "Authorization": f"Bearer {new_user["access_token"]}"
            }
        )

        assert response.status_code == 404, response.text


if __name__ == "__main__":
    pytest.main()
