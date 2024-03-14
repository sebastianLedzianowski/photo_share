import pytest
import unittest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json
from typing import Optional, List
from datetime import datetime, timedelta

from src.database.models import Picture, User, Tag
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
from src.tests.conftest import TestingSessionLocal
from src.tests.conftest import login_user_token_created


def test_search_pictures2(user, session: Session, client: TestClient):
    user1 = login_user_token_created(user, session)

    search_params = PictureSearch(
        keywords=["test"],
        tags=["test_tag"],
        rating=4,
        added_after=datetime.utcnow() - timedelta(days=30)
    )
    response = client.get(
        "/pictures",
        headers={"Authorization": f"Bearer {user1}"},
        params=search_params.dict()
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, PictureResponse) for item in data)


def test_search_pictures(search_params, sort_by, sort_order, db):
    picture_search_service = PictureSearchService(db)
    pictures = picture_search_service.search_pictures(search_params, sort_by, sort_order)
    assert isinstance(pictures, List)
    for picture in pictures:
        assert isinstance(picture, PictureResponse)


def test_search_pictures(picture_s, user, admin, session, client):
    user_1 = login_user_token_created(user, session)
    user_2 = login_user_token_created(admin, session)

    picture = picture_s

    response = client.get(
        "/api/search/pictures",
        headers={"Authorization": f"Bearer {user_1.get('access_token')}"},
        json={"picture_id": 1,
              "rating": 3}
    )

    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == [{'type': 'enum',
                               'loc': ['body', 'rating'],
                               'msg': 'Input should be 1, 2, 3, 4 or 5',
                               'input': 3,
                               'ctx': {'expected': '1, 2, 3, 4 or 5'}}]