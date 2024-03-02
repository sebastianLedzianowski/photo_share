import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.database.models import Picture, Tag, User, Base
from src.schemas import PictureResponse


app = FastAPI()


class TestSearch(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.client = TestClient(app)

    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    @patch("app.main.repository_users.get_user_by_email", new_callable=MagicMock)
    def test_search_pictures_keywords(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = User(id=1, username="testuser", email="test@example.com", password="testpassword")

        picture1 = Picture(id=1, description="Test picture 1", created_at=datetime.utcnow(), user_id=1)
        picture2 = Picture(id=2, description="Test picture 2", created_at=datetime.utcnow(), user_id=1)
        picture3 = Picture(id=3, description="Test picture 3", created_at=datetime.utcnow(), user_id=2)

        with self.SessionLocal() as db:
            db.add(picture1)
            db.add(picture2)
            db.add(picture3)
            db.commit()

            response = self.client.post(
                "/api/search",
                json={
                    "keywords": "test",
                    "rating": 2,
                    "added_after": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                },
            )

        self.assertEqual(response.status_code, 200)
        pictures = PictureResponse.parse_obj(response.json())
        self.assertEqual(len(pictures), 1)
        self.assertEqual(pictures[0].id, 1)

    @patch("app.main.repository_users.get_user_by_email", new_callable=MagicMock)
    def test_search_pictures_tags(self, mock_get_user_by_email):
        mock_get_user_by_email.return_value = User(id=1, username="testuser", email="test@example.com", password="testpassword")

        tag1 = Tag(id=1, name="testtag1")
        tag2 = Tag(id=2, name="testtag2")
        picture1 = Picture(id=1, description="Test picture 1", created_at=datetime.utcnow(), user_id=1, tags=[tag1])
        picture2 = Picture(id=2, description="Test picture 2", created_at=datetime.utcnow(), user_id=1, tags=[tag2])
        picture3 = Picture(id=3, description="Test picture 3", created_at=datetime.utcnow(), user_id=2)

        with self.SessionLocal() as db:
            db.add(tag1)
            db.add(tag2)
            db.add(picture1)
            db.add(picture2)
            db.add(picture3)
            db.commit()

            response = self.client.post