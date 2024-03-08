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
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, query
from sqlalchemy.pool import StaticPool
from typing import List
import httpx
import faker

from src.routes.search import search_pictures, search_users, search_users_by_picture
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.tests.conftest import client, session
from src.database.models import Picture, Tag, User
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse
from src.services.auth import Auth


app = FastAPI()


engine = create_engine('sqlite:///test_routes_search.db')


Base = declarative_base()


TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
        

@pytest.fixture(scope="function", autouse=True)
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        

@pytest.fixture
def picture():
    class PictureTest:
        def __init__(self, id, user_id, rating, user, tags, picture_name, description, created_at):
            self.id = id
            self.user_id = user_id
            self.rating = rating
            self.user = user
            self.tags = tags
            self.picture_name = picture_name
            self.description = description
            self.created_at = created_at


        def dict(self):
            return {
                "id": self.id,
                "user_id": self.user_id,
                "rating": self.rating,
                "user": self.user.dict(),
                "tags": self.tags,
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
                    picture_name="picture1_name",
                    description="picture1_description",
                    created_at=datetime(2022, 1, 1)
                    )


@pytest.fixture
def user():
    class UserTest:
        def __init__(self, id, username, email):
            self.id = id
            self.username = username
            self.email = email

        def dict(self):
            return {
                "id": self.id,
                "username": self.username,
                "email": self.email
            }
    return UserTest(
                    id=1,
                    username="example",
                    email="example@example.com"
                    )


Base.metadata.create_all(engine)


fake = faker.Faker()

def create_mock_picture(id):
    return {
        "id": id,
        "user_id": fake.random_int(1, 10),
        "rating": fake.random_int(1, 5),
        "user": {
            "id": fake.random_int(1, 10),
            "username": fake.user_name(),
            "email": fake.email()
        },
        "tags": [fake.word(), fake.word()],
        "picture_name": fake.word(),
        "created_at": fake.date_time_between(start_date="-1y", end_date="now")
    }

def create_mock_user(id):
    return {
        "id": id,
        "username": fake.user_name(),
        "email": fake.email()
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

# Mock authenticated user
def mock_get_current_user():
    return User(id=1, username="test_user", is_moderator=True)  # Mock a moderator user

app.dependency_overrides[Auth.get_current_user] = mock_get_current_user

session.commit()


session.close()


def search_pictures(db, keyword: str) -> List[PictureResponse]:
    pictures = db.query(Picture).filter(Picture.picture_name.ilike(f"%{keyword}%")).all()
    return [PictureResponse.from_orm(picture) for picture in pictures]


def search_users(db, keyword: str) -> List[UserResponse]:
    users = db.query(User).filter(User.username.ilike(f"%{keyword}%")).all()
    return [UserResponse.from_orm(user) for user in users]


class TestPictureSearch(unittest.TestCase):
    @pytest.mark.usefixtures("picture")
    def test_search_pictures_by_tags(self, picture, client):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(tags=["family"])
                result = service.search_pictures(search_params)
                self.assertIsInstance(result, list)
                response = client.post("/pictures/search", json={"search_params": {...}})
                assert response.status_code == 200
                assert len(response.json()) > 0

    def test_search_pictures_with_rating_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(tags=["family"])
                result = service.search_pictures(search_params, rating=4)
                self.assertIsInstance(result, list)
                response = client.post("/pictures/search", json={"search_params": {...}})
                assert response.status_code == 200
                assert len(response.json()) > 0
                    
    def test_search_pictures_with_added_after_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/pictures/search", json={"search_params": {...}})
                assert response.status_code == 200
                assert len(response.json()) > 0                
    
    def test_search_pictures_sorting(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/pictures/search", json={"search_params": {...}})
                assert response.status_code == 200
                assert len(response.json()) > 0    
    
class TestUserSearch(unittest.TestCase):
    
    def test_search_users_by_keyword(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search", json={"search_params": {...}})
                assert response.status_code == 200
                assert len(response.json()) > 0
        
    def test_search_users_by_username(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search", json={"search_params": {...}})
                assert response.status_code == 200
                assert len(response.json()) > 0
                        
    def test_search_users_by_email(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search", json={"search_params": {...}})
                assert response.status_code == 200
                assert len(response.json()) > 0


class TestUserPictureSearch(unittest.TestCase):
    def test_search_users_by_pictures_by_keywords(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search_by_picture", json={"picture_id": ..., "rating": ...})
                assert response.status_code == 200
                assert len(response.json()) > 0

    def test_search_users_by_pictures_with_user_id_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search_by_picture", json={"picture_id": ..., "rating": ...})
                assert response.status_code == 200
                assert len(response.json()) > 0
                
    def test_search_users_by_pictures_with_picture_id_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search_by_picture", json={"picture_id": ..., "rating": ...})
                assert response.status_code == 200
                assert len(response.json()) > 0
                                
    def test_search_users_by_pictures_with_rating_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search_by_picture", json={"picture_id": ..., "rating": ...})
                assert response.status_code == 200
                assert len(response.json()) > 0
                    
    def test_search_users_by_pictures_with_added_after_filter(self):
        with TestClient(app) as client:
            with get_db() as db:
                service = PictureSearchService(db)
                search_params = PictureSearch(keywords="nature", tags=["landscape"])
                result = service.search_pictures(search_params, rating=4, added_after=datetime(2022, 1, 1), sort_by="created_at", sort_order="desc")
                self.assertIsInstance(result, list)
                response = client.post("/users/search_by_picture", json={"picture_id": ..., "rating": ...})
                assert response.status_code == 200
                assert len(response.json()) > 0            
            
                
                
