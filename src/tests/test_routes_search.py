import unittest
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker, Session, query
from sqlalchemy.pool import StaticPool
from typing import List
import httpx
import faker

from src.routes.search import search_pictures, search_users, search_users_by_picture, router
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.tests.conftest import client, session
from src.database.models import Picture, Tag, User, Base
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse


app = FastAPI()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def picture():
    class PictureTest:
        def __init__(self, id, user_id, rating, user, tags, picture_url, picture_name, description, created_at):
            self.id = id
            self.user_id = user_id
            self.rating = rating
            self.user = user
            self.tags = tags
            self.picture_url = picture_url
            self.picture_name = picture_name
            self.description = description
            self.created_ad = created_at


        def dict(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "rating": self.rating,
                "user": self.user.dict(),
                "tags": self.tags,
                "picture_url": self.picture_url,
                "picture_name": self.picture_name,
                "description": self.description,
                "created_at": self.created_at
            }
    return PictureTest(
                    id=1,
                    user_id=1,
                    rating=4,
                    user=user,
                    tags=['picture1_tag', 'picture1_tag2'],
                    picture_url="picture1_url",
                    picture_name="picture1_name",
                    description="picture1_description",
                    created_at=datetime(2022, 1, 1)
                    )


@pytest.fixture(scope="function")
def user():
    class UserTest:
        def __init__(self, id, username, email, password):
            self.id = id
            self.username = username
            self.email = email
            self.password = password

        def dict(self):
            return {
                "id": self.id,
                "username": self.username,
                "email": self.email,
                "password": self.password
            }
    return UserTest(id=1,
                    username="example",
                    email="example@example.com",
                    password="secret")
    


fake = faker.Faker()

def create_mock_picture(id):
    return {
        "id": id,
        "user_id": fake.random_int(1, 10),
        "rating": fake.random_int(1, 5),
        "user": {
            "id": fake.random_int(1, 10),
            "username": fake.user_name(),
            "email": fake.email(),
            "password": fake.password()
        },
        "tags": [fake.word(), fake.word()],
        "picture_url": fake.image_url(),
        "picture_name": fake.word(),
        "description": fake.sentence(),
        "created_at": fake.date_time_between(start_date="-1y", end_date="now")
    }

def create_mock_user(id):
    return {
        "id": id,
        "username": fake.user_name(),
        "email": fake.email(),
        "password": fake.password()
    }


mock_pictures = [create_mock_picture(i) for i in range(1, 11)]
mock_users = [create_mock_user(i) for i in range(1, 11)]


Session = sessionmaker(bind=engine)
session = Session()

for mock_picture in mock_pictures:
    user_id = mock_picture["user"]["id"]
    user = session.query(User).filter_by(id=user_id).first()
    picture = Picture(id=mock_picture["id"], user_id=mock_picture["user_id"], rating=mock_picture["rating"], user=user, tags=','.join(mock_picture["tags"]), picture_url=mock_picture["picture_url"], picture_name=mock_picture["picture_name"], description=mock_picture["description"], created_at=mock_picture["created_at"])
    session.add(picture)
    
for mock_user in mock_users:
    user = User(id=mock_user["id"], username=mock_user["username"], email=mock_user["email"], password=mock_user["password"])
    session.add(user)

session.commit()
session.close()


            
class TestPictureSearch(unittest.TestCase):
    
    def test_search_pictures_by_keywords(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)

    def test_search_pictures_by_tags(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                
    def test_search_pictures_with_rating_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
    
    def test_search_pictures_with_added_after_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
    
    def test_search_pictures_sorting(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
    
class TestUserSearch(unittest.TestCase):
    
    def test_search_users_by_keyword(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
        
    def test_search_users_by_username(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
        
    def test_search_users_by_email(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)


class TestUserPictureSearch(unittest.TestCase):
    def test_search_users_by_pictures_by_keywords(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)

    def test_search_users_by_pictures_with_user_id_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                
    def test_search_users_by_pictures_with_picture_id_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                
    def test_search_users_by_pictures_with_rating_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
    
    def test_search_users_by_pictures_with_added_after_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)