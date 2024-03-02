import unittest
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.routes.search import search_pictures, search_users, search_users_by_picture
from src.database.models import Picture, Tag, User, Base
from src.database.db import get_db
from src.schemas import PictureResponse, PictureSearch, UserResponse


app = FastAPI()


class Test_search_pictures(unittest.TestCase):
    def setUp(self):
        engine = create_engine("sqlite:///:memory:", echo=False, connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(engine)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    def test_search_pictures(self, mock_get_db, client):
        user = User(username="testuser", email="test@example.com", avatar="test.jpg")
        mock_get_db.return_value.query.return_value.filter.return_value.first.return_value = user
        db = self.SessionLocal()
        mock_get_db.return_value = db

        response = client.post("/search/pictures", json={"keywords": "test"})
        pictures = PictureResponse(id=1, description="test picture", rating=5, created_at=datetime.now(), user_id=1)
        assert response.status_code == 200
        assert response.json() == [pictures.dict()]

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    def test_search_pictures_rating_filter(self, mock_get_db, client):
        user = User(username="testuser", email="test@example.com", avatar="test.jpg")
        picture1 = Picture(description="test picture 1", rating=3, user_id=1)
        picture2 = Picture(description="test picture 2", rating=5, user_id=1)
        db = self.SessionLocal()
        db.add(user)
        db.add(picture1)
        db.add(picture2)
        db.commit()
        mock_get_db.return_value = db

        response = client.post("/search/pictures", json={"keywords": "test", "rating": 4})
        pictures = PictureResponse(id=2, description="test picture 2", rating=5, created_at=picture2.created_at, user_id=1)
        assert response.status_code == 200
        assert response.json() == [pictures.dict()]
    
    
class Test_search_users(unittest.TestCase):

    def tearDown(self):
        self.db.close()

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    def test_search_users(self, mock_get_db, client):
        user1 = User(username="testuser1", email="test1@example.com", avatar="test1.jpg")
        user2 = User(username="testuser2", email="test2@example.com", avatar="test2.jpg")
        self.db.add(user1)
        self.db.add(user2)
        self.db.commit()
        mock_get_db.return_value = self.db

        response = client.post("/search/users", json={"keywords": "test"})
        users = [
            UserResponse(id=1, username="testuser1", email="test1@example.com", avatar="test1.jpg", picture_count=0),
            UserResponse(id=2, username="testuser2", email="test2@example.com", avatar="test2.jpg", picture_count=0)
        ]
        assert response.status_code == 200
        assert response.json() == users

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    def test_search_users_username_filter(self, mock_get_db, client):
        user = User(username="testuser", email="test@example.com", avatar="test.jpg")
        self.db.add(user)
        self.db.commit()
        mock_get_db.return_value = self.db

        response = client.post("/search/users", json={"username": "testuser"})
        users = [UserResponse(id=1, username="testuser", email="test@example.com", avatar="test.jpg", picture_count=0)]
        assert response.status_code == 200
        assert response.json() == users

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    def test_search_users_email_filter(self, mock_get_db, client):
        user = User(username="testuser", email="test@example.com", avatar="test.jpg")
        self.db.add(user)
        self.db.commit()
        mock_get_db.return_value = self.db

        response = client.post("/search/users", json={"email": "test@example.com"})
        users = [UserResponse(id=1, username="testuser", email="test@example.com", avatar="test.jpg", picture_count=0)]
        assert response.status_code == 200
        assert response.json() == users
    
    
class Test_search_users_by_picture(unittest.TestCase):
    def setUp(self):
        self.db = get_db()
        self.client = TestClient(app)
        self.user = User(username="testuser", email="test@example.com", avatar="test.jpg", is_moderator=True)
        self.db.add(self.user)
        self.db.commit()

    def tearDown(self):
        self.db.close()

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    @patch("src.routes.search.get_current_user", new_callable=MagicMock)
    def test_search_users_by_picture(self, mock_get_current_user, mock_get_db, client):
        # Add test data to the database
        user1 = User(username="user1", email="user1@example.com", avatar="user1.jpg")
        user2 = User(username="user2", email="user2@example.com", avatar="user2.jpg")
        picture1 = Picture(user_id=user1.id, rating=3)
        picture2 = Picture(user_id=user2.id, rating=5)
        self.db.add(user1)
        self.db.add(user2)
        self.db.add(picture1)
        self.db.add(picture2)
        self.db.commit()

        # Test search_users_by_picture function with no filters
        mock_get_current_user.return_value = self.user
        mock_get_db.return_value = self.db
        response = client.post("/search/users_by_picture")
        users = [
            UserResponse(id=user1.id, username="user1", email="user1@example.com", avatar="user1.jpg", picture_count=1),
            UserResponse(id=user2.id, username="user2", email="user2@example.com", avatar="user2.jpg", picture_count=1)
        ]
        assert response.status_code == 200
        assert response.json() == users

        # Test search_users_by_picture function with user_id filter
        mock_get_current_user.return_value = self.user
        mock_get_db.return_value = self.db
        response = client.post("/search/users_by_picture", json={"user_id": user1.id})
        users = [
            UserResponse(id=user1.id, username="user1", email="user1@example.com", avatar="user1.jpg", picture_count=1),
        ]
        assert response.status_code == 200

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    @patch("src.routes.search.get_current_user", new_callable=MagicMock)
    def test_search_users_by_picture_rating_filter(self, mock_get_current_user, mock_get_db, client):
        # Add test data to the database
        user1 = User(username="user1", email="user1@example.com", avatar="user1.jpg")
        user2 = User(username="user2", email="user2@example.com", avatar="user2.jpg")
        picture1 = Picture(user_id=user1.id, rating=3)
        picture2 = Picture(user_id=user2.id, rating=5)
        self.db.add(user1)
        self.db.add(user2)
        self.db.add(picture1)
        self.db.add(picture2)
        self.db.commit()

        # Test search_users_by_picture function with rating filter
        mock_get_current_user.return_value = self.user
        mock_get_db.return_value = self.db
        response = client.post("/search/users_by_picture", json={"rating": 4})
        users = [
            UserResponse(id=user2.id, username="user2", email="user2@example.com", avatar="user2.jpg", picture_count=1)
        ]
        assert response.status_code == 200
        assert response.json() == users

    @patch("src.routes.search.get_db", new_callable=MagicMock)
    @patch("src.routes.search.get_current_user", new_callable=MagicMock)
    def test_search_users_by_picture_added_after_filter(self, mock_get_current_user, mock_get_db, client):
        # Add test data to the database
        user1 = User(username="user1", email="user1@example.com", avatar="user1.jpg")
        user2 = User(username="user2", email="user2@example.com", avatar="user2.jpg")
        picture1 = Picture(user_id=user1.id, rating=3, created_at=datetime.now() - timedelta(days=10))
        picture2 = Picture(user_id=user2.id, rating=5, created_at=datetime.now())
        self.db.add(user1)
        self.db.add(user2)
        self.db.add(picture1)
        self.db.add(picture2)
        self.db.commit()

        # Test search_users_by_picture function with added_after filter
        mock_get_current_user.return_value = self.user
        mock_get_db.return_value = self.db
        response = client.post("/search/users_by_picture", json={"added_after": datetime.now() - timedelta(days=11)})
        users = [
            UserResponse(id=user2.id, username="user2", email="user2@example.com", avatar="user2.jpg", picture_count=1)
        ]
        assert response.status_code == 200
        assert response.json() == users


    @patch("src.routes.search.get_db", new_callable=MagicMock)
    @patch("src.routes.search.get_current_user", new_callable=MagicMock)
    def test_search_users_by_picture_not_moderator(self, mock_get_current_user, mock_get_db, client):
        # Add test data to the database
        user1 = User(username="user1", email="user1@example.com", avatar="user1.jpg")
        user2 = User(username="user2", email="user2@example.com", avatar="user2.jpg")
        picture1 = Picture(user_id=user1.id, rating=3)
        picture2 = Picture(user_id=user2.id, rating=5)
        self.db.add(user1)
        self.db.add(user2)
        self.db.add(picture1)
        self.db.add(picture2)
        self.db.commit()

        # Test search_users_by_picture function with not moderator user
        mock_get_current_user.return_value = User(username="testuser", email="test@example.com", avatar="test.jpg", is_moderator=False)
        mock_get_db.return_value = self.db

        with pytest.raises(HTTPException) as exc_info:
            client.post("/search/users_by_picture")

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "User filtering is only available to moderators and administrators."
        