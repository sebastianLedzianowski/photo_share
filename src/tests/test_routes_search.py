import unittest
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session, query
from datetime import datetime
from sqlalchemy.pool import StaticPool
from typing import List
from fastapi.templating import Jinja2Templates

from src.routes.search import search_pictures, search_users, search_users_by_picture
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.database.models import Base, User, Picture, Tag
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
from src.services.auth import Auth
from src.tests.conftest import fake_db_for_search_test
from main import app
from src.services.auth import auth_service
from faker import Faker


fake = Faker("pl_PL")


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


templates = Jinja2Templates(directory="templates")


@pytest.fixture(scope="function", autouse=True)
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)
    
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

no_of_pictures = 20

def create_x_pictures(fake_db_for_search_test, no_of_pictures):
    pictures = []
    for i in range(no_of_pictures):
        picture = fake_db_for_search_test["create_picture"](f"test_user_id{i}",f"test_rating{i}",f"test_user{i}",f"test_tag{i}"f"test_picture_name{i}", f"test_description{i}", datetime.now())
        pictures.append(picture)
    return pictures

pictures = create_x_pictures(fake_db_for_search_test, no_of_pictures)
for picture in pictures:
     session.add(picture)
session.commit()

no_of_users = 10

def create_x_users(fake_db_for_search_test, no_of_users):
    users = []
    for i in range(no_of_users):
        user = fake_db_for_search_test["create_user"](f"test_email{i}",f"test_username{i}")
        users.append(user)
    return users

users = create_x_users(fake_db_for_search_test, no_of_users)
for user in users:
     session.add(user)
session.commit()

get_current_user = Auth.get_current_user

session.commit()
session.close()


class TestPictureSearch(unittest.TestCase):

    def test_search_pictures_with_keyword_filter(self):
        client = TestClient(app)
        response = client.get("/api/pictures/search?keyword=user1")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 1
        assert "id" in data[0]

        
    def test_search_pictures_with_picture_name_filter(self):
        pass
    
    def test_search_pictures_with_rating_filter(self):
         pass
                   
    def test_search_pictures_with_added_after_filter(self):
        pass
            
    def test_search_pictures_sorting(self):
        pass

    
class TestUserSearch(unittest.TestCase):
    
    def test_search_users_by_keyword(self):
        pass

    def test_search_users_by_username(self):
        pass

    def test_search_users_by_email(self):
        pass


class TestUserPictureSearch(unittest.TestCase):
    
    def test_search_users_by_pictures_by_keywords(self):
        pass

    def test_search_users_by_pictures_with_user_id_filter(self):
        pass
                
    def test_search_users_by_pictures_with_picture_id_filter(self):
        pass
                                
    def test_search_users_by_pictures_with_rating_filter(self):
        pass

    def test_search_users_by_pictures_with_added_after_filter(self):
        pass


if __name__ == "__main__":
    pytest.main()