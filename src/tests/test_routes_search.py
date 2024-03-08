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
from PIL import Image
from io import BytesIO
from faker import Faker
import random

from src.routes.search import search_pictures, search_users, search_users_by_picture
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.database.models import Base, User, Picture, Tag
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse, UserSearch
from src.services.auth import Auth
from src.tests.conftest import fake_db_for_search_test
from src.tests.conftest import login_user_confirmed_true_and_hash_password, login_as_admin
from src.tests.test_routes_auth import login_user_token_created
from src.services.auth import auth_service
from main import app


def test_picture_search_with_valid_search_parameters(self, db):
    # Arrange
    search_params = PictureSearch(...)
    rating = 5
    added_after = datetime(2022, 1, 1)
    sort_by = "created_at"
    sort_order = "desc"
    db = Session()

    # Act
    result = search_pictures(search_params, rating, added_after, sort_by, sort_order, db)

    # Assert
    assert isinstance(result, list)
    assert all(isinstance(picture, PictureResponse) for picture in result)