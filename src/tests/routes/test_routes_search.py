import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock
from fastapi import FastAPI, HTTPException, Depends
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session, query
from datetime import datetime
from sqlalchemy.pool import StaticPool
from typing import List
from fastapi.templating import Jinja2Templates
from faker import Faker

from src.routes.search import search_pictures, search_users, search_users_by_picture
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.database.models import User, Picture
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
from src.services.auth import Auth, auth_service
from src.tests.conftest import client, session, engine, Base, TestingSessionLocal, picture_s, user_s, fake_db_for_search_test
from main import app


pictures = [
    (1, 3, ["picture1_tag", "picture1_tag2"], "picture1_name", datetime.now),
    (2, 4, ["picture1_tag2", "picture1_tag3"], "picture2_name", datetime.now),
    (3, 5, ["picture1_tag2", "picture1_tag3"], "picture3_name", datetime.now),
    (4, 2, ["picture1_tag3", "picture1_tag4"], "picture4_name", datetime.now),
    (5, 1, ["picture1_tag", "picture1_tag4"], "picture5_name", datetime.now),
    (6, 2, ["picture1_tag1", "picture1_tag2"], "picture6_name", datetime.now),
    (7, 3, ["picture1_tag1", "picture1_tag2"], "picture7_name", datetime.now),
    (8, 4, ["picture1_tag2", "picture1_tag3"], "picture8_name", datetime.now),
    (9, 5, ["picture1_tag3", "picture1_tag4"], "picture9_name", datetime.now),
    (10, 1, ["picture1_tag", "picture1_tag4"], "picture10_name", datetime.now)
]


users = [
    (1,f"test_email1",f"test_username1"), 
    (2,f"test_email2",f"test_username2"), 
    (3,f"test_email3",f"test_username3"), 
    (4,f"test_email4",f"test_username4"), 
    (5,f"test_email5",f"test_username5")
]       
    
@pytest.fixture(scope="function", autouse=True)
def setup_test_database(picture_s, user_s):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        for picture in pictures:
            p = picture_s(id=picture[0], user_id=picture[1], tags=picture[2], name=picture[3], created_at=picture[4])
            db.add(p)

        for user in users:
            u = user_s(id=user[0], email=user[1], username=user[2])
            db.add(u)

        db.commit()
        yield db
    finally:
        db.rollback()
        db.close()


get_current_user = Auth.get_current_user


class TestPictureSearch(unittest.TestCase):
                
    def test_search_pictures_with_picture_name_filter(self, client):
            response = client.post(f"/api/pictures/search?name=picture1_name")
            data = response.json()

            assert response.status_code == 200
            assert data["id"] == pictures.id
    
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