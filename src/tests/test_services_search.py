import unittest
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker, Session, query
from sqlalchemy.pool import StaticPool
from typing import List
import httpx
from faker import Faker

from src.routes.search import search_pictures, search_users, search_users_by_picture, router
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.tests.conftest import client, session
from src.tests.test_routes_search import user, picture
from src.database.models import Picture, Tag, User, Base
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse
from main import app


class TestPictureSearchService(unittest.TestCase):

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
    
class TestUserSearchService(unittest.TestCase):
    
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


class TestUserPictureSearchService(unittest.TestCase):
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
    