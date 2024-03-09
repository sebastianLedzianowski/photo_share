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
from datetime import datetime, now, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, query
from sqlalchemy.pool import StaticPool
from typing import List
import httpx
import faker

from src.routes.search import search_pictures, search_users, search_users_by_picture, router
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.tests.conftest import client, session, engine
from src.database.models import Picture, Tag, User, Base
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse


app = FastAPI()


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client



class TestPictureSearch(unittest.TestCase):

    # Can successfully search for pictures with no filters applied
    def test_search_pictures_no_filters(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with no filters applied
        search_params = PictureSearch()
        result = picture_search_service.search_pictures(search_params)

        # Assert that the result contains both pictures
        assert len(result) == 2
        assert result[0].description == "Test picture 1"
        assert result[1].description == "Test picture 2"

    # Can handle search with no results
    def test_search_pictures_no_results(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with search parameters that won't match any pictures
        search_params = PictureSearch(keywords="Test", tags=["tag1"])
        result = picture_search_service.search_pictures(search_params)

        # Assert that the result is an empty list
        assert len(result) == 0

    # Can successfully search for pictures with sorting by created_at in ascending order
    def test_search_pictures_sort_by_created_at_ascending(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with sort_by set to "created_at" and sort_order set to "asc"
        search_params = PictureSearch()
        result = picture_search_service.search_pictures(search_params, sort_by="created_at", sort_order="asc")

        # Assert that the result contains both pictures in ascending order of created_at
        assert len(result) == 2
        assert result[0].description == "Test picture 1"
        assert result[1].description == "Test picture 2"

    # Can successfully search for pictures with tag filter applied
    def test_search_pictures_with_tag_filter(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        tag1 = Tag(name="tag1")
        tag2 = Tag(name="tag2")
        picture1.tags.append(tag1)
        picture2.tags.append(tag2)
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with tag filter applied
        search_params = PictureSearch(tags=["tag1"])
        result = picture_search_service.search_pictures(search_params)

        # Assert that the result contains only picture1
        assert len(result) == 1
        assert result[0].description == "Test picture 1"

    # Can successfully search for pictures with rating filter applied
    def test_search_pictures_with_rating_filter(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with rating filter applied
        search_params = PictureSearch()
        rating = 3
        result = picture_search_service.search_pictures(search_params, rating=rating)

        # Assert that the result contains only pictures with rating >= 3
        assert len(result) == 1
        assert result[0].description == "Test picture 1"

    # Can successfully search for pictures with added_after filter applied
    def test_search_pictures_with_added_after_filter(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with added_after filter applied
        search_params = PictureSearch()
        added_after = datetime.now()
        result = picture_search_service.search_pictures(search_params, added_after=added_after)

        # Assert that the result contains only the picture added after the specified datetime
        assert len(result) == 1
        assert result[0].description == "Test picture 2"

    # Can successfully search for pictures with keyword filter applied
    def test_search_pictures_with_keyword_filter(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with keyword filter applied
        search_params = PictureSearch(keywords="Test")
        result = picture_search_service.search_pictures(search_params)

        # Assert that the result contains both pictures
        assert len(result) == 2
        assert result[0].description == "Test picture 1"
        assert result[1].description == "Test picture 2"

    # Can successfully search for pictures with sorting by rating in ascending order
    def test_search_pictures_sort_by_rating_ascending(self):
        # Initialize PictureSearchService
        db = Session()
        picture_search_service = PictureSearchService(db)

        # Create test data
        picture1 = Picture(description="Test picture 1", rating=4, created_at=datetime.now())
        picture2 = Picture(description="Test picture 2", rating=3, created_at=datetime.now())
        db.add(picture1)
        db.add(picture2)
        db.commit()

        # Call search_pictures method with sorting by rating in ascending order
        search_params = PictureSearch()
        result = picture_search_service.search_pictures(search_params, sort_by="rating", sort_order="asc")

        # Assert that the result contains both pictures sorted by rating in ascending order
        assert len(result) == 2
        assert result[0].description == "Test picture 2"
        assert result[1].description == "Test picture 1"
    
    
class TestUserSearch(unittest.TestCase):

    # Can search for users with only picture search parameters
    def test_search_users_with_picture_search_parameters(self):
        # Arrange
        db = Session()
        user_search_service = UserSearchService(db)
        search_params = PictureSearch(keywords="picture")

        # Act
        result = user_search_service.search_users(search_params)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Can search for users with a single picture search parameter
    def test_search_users_with_single_picture_search_parameter(self):
        # Arrange
        db = Session()
        user_search_service = UserSearchService(db)
        search_params = PictureSearch(keywords="test")

        # Act
        result = user_search_service.search_users(search_params)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        
    def test_search_users_with_empty_search_parameters(self):
        # Arrange
        db = Session()
        user_search_service = UserSearchService(db)
        search_params = PictureSearch()

        # Act
        result = user_search_service.search_users(search_params)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        
    # Can search for users with only username search parameter
    def test_search_users_with_username_parameter(self):
        # Arrange
        db = Session()
        user_search_service = UserSearchService(db)
        username = "test_username"

        # Act
        result = user_search_service.search_users(PictureSearch(), username=username)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        
    # Can search for users with a single username search parameter
    def test_search_users_with_single_username_search_parameter(self):
        # Arrange
        db = Session()
        user_search_service = UserSearchService(db)
        username = "test_username"

        # Act
        result = user_search_service.search_users(username=username)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        
    def test_search_users_with_only_email_search_parameter(self):
        # Arrange
        db = Session()
        user_search_service = UserSearchService(db)
        search_params = PictureSearch(keywords=None)

        # Act
        result = user_search_service.search_users(search_params, email="test@example.com")

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        
    # Can search for users with all search parameters
    def test_search_users_with_all_parameters(self):
        # Arrange
        db = Session()
        user_search_service = UserSearchService(db)
        search_params = PictureSearch(keywords="test")
        username = "user"
        email = "user@example.com"

        # Act
        result = user_search_service.search_users(search_params, username, email)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        
class TestUserPictureSearch(unittest.TestCase):

    # Can search for users by picture with no filters
    def test_search_users_by_picture_with_no_filters(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with no filters
        result = service.search_users_by_picture()

        # Assert that the result is an empty list
        assert result == []

    # No users found
    def test_no_users_found(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with a non-existent user_id
        result = service.search_users_by_picture(user_id=999)

        # Assert that the result is an empty list
        assert result == []

    # Can search for users by picture with rating filter
    def test_search_users_by_picture_with_rating_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Create test data
        user1 = User(username="user1", email="user1@example.com", avatar="avatar1")
        user2 = User(username="user2", email="user2@example.com", avatar="avatar2")
        picture1 = Picture(user=user1, rating=4, created_at=datetime.now())
        picture2 = Picture(user=user1, rating=3, created_at=datetime.now())
        picture3 = Picture(user=user2, rating=5, created_at=datetime.now())
        db.add_all([user1, user2, picture1, picture2, picture3])
        db.commit()

        # Call the search_users_by_picture method with rating filter
        result = service.search_users_by_picture(rating=4)

        # Assert that the result contains the correct users
        assert len(result) == 1
        assert result[0].id == user1.id
        assert result[0].username == user1.username
        assert result[0].email == user1.email
        assert result[0].avatar == user1.avatar
        assert result[0].picture_count == 2

    # Can search for users by picture with user_id filter
    def test_search_users_by_picture_with_user_id_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Create test data
        user_id = 1
        picture_id = 1
        rating = 5
        added_after = datetime(2022, 1, 1)

        # Call the search_users_by_picture method with user_id filter
        result = service.search_users_by_picture(user_id=user_id)

        # Assert that the result is a list of UserResponse objects
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

        # Assert that the user_id filter is applied correctly
        assert all(user.id == user_id for user in result)

    # Can search for users by picture with picture_id filter
    def test_search_users_by_picture_with_picture_id_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Create a picture with a specific picture_id
        picture = Picture(user_id=1, rating=5)
        db.add(picture)
        db.commit()

        # Call the search_users_by_picture method with picture_id filter
        result = service.search_users_by_picture(picture_id=5)

        # Assert that the result is a list with one user
        assert len(result) == 1

        # Assert that the user has the correct attributes
        assert result[0].id == 1
        assert result[0].username == "test_user"
        assert result[0].email == "test_user@example.com"
        assert result[0].avatar == "avatar.jpg"
        assert result[0].picture_count == 1

    # No pictures found with rating filter
    def test_no_pictures_found_with_rating_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with rating filter set to None
        result = service.search_users_by_picture(rating=None)

        # Assert that the result is an empty list
        assert result == []

    # No pictures found
    def test_no_pictures_found(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with no filters
        result = service.search_users_by_picture()

        # Assert that the result is an empty list
        assert result == []

    # Returns correct number of pictures for each user
    def test_search_users_by_picture_returns_correct_number_of_pictures_for_each_user(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with no filters
        result = service.search_users_by_picture()

        # Assert that the result is an empty list
        assert result == []

    # No pictures found with added_after filter
    def test_no_pictures_found_with_added_after_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with added_after filter set to a date in the future
        added_after = datetime(2022, 1, 1)
        result = service.search_users_by_picture(added_after=added_after)

        # Assert that the result is an empty list
        assert result == []

    # Can search for users by picture with added_after filter
    def test_search_users_by_picture_with_added_after_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Create test data
        user1 = User(username="user1", email="user1@example.com", avatar="avatar1")
        user2 = User(username="user2", email="user2@example.com", avatar="avatar2")
        picture1 = Picture(user_id=1, rating=5, created_at=datetime(2022, 1, 1))
        picture2 = Picture(user_id=1, rating=4, created_at=datetime(2022, 2, 1))
        picture3 = Picture(user_id=2, rating=3, created_at=datetime(2022, 3, 1))
        db.add_all([user1, user2, picture1, picture2, picture3])
        db.commit()

        # Call the search_users_by_picture method with added_after filter
        added_after = datetime(2022, 2, 1)
        result = service.search_users_by_picture(added_after=added_after)

        # Assert that the result contains the expected users
        assert len(result) == 1
        assert result[0].id == 1
        assert result[0].username == "user1"
        assert result[0].email == "user1@example.com"
        assert result[0].avatar == "avatar1"
        assert result[0].picture_count == 1

    # No users found with user_id filter
    def test_no_users_found_with_user_id_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with user_id filter
        result = service.search_users_by_picture(user_id=1)

        # Assert that the result is an empty list
        assert result == []

    # Invalid rating filter
    def test_invalid_rating_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with an invalid rating filter
        result = service.search_users_by_picture(rating=-1)

        # Assert that the result is an empty list
        assert result == []

    # Invalid picture_id filter
    def test_invalid_picture_id_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with an invalid picture_id filter
        result = service.search_users_by_picture(picture_id="invalid")

        # Assert that the result is an empty list
        assert result == []

    # Invalid added_after filter
    def test_invalid_added_after_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with an invalid added_after filter
        result = service.search_users_by_picture(added_after="2022-01-01")

        # Assert that the result is an empty list
        assert result == []

    # Invalid user_id filter
    def test_invalid_user_id_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with an invalid user_id filter
        result = service.search_users_by_picture(user_id='invalid')

        # Assert that the result is an empty list
        assert result == []

    # No pictures found with picture_id filter
    def test_no_pictures_found_with_picture_id_filter(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Call the search_users_by_picture method with picture_id filter set to None
        result = service.search_users_by_picture(picture_id=None)

        # Assert that the result is an empty list
        assert result == []

    # Can search for users by picture with all filters
    def test_search_users_by_picture_with_all_filters(self):
        # Initialize the UserPictureSearchService class
        db = Session()
        service = UserPictureSearchService(db)

        # Create test data
        user_id = 1
        picture_id = 1
        rating = 5
        added_after = datetime(2022, 1, 1)

        # Call the search_users_by_picture method with all filters
        result = service.search_users_by_picture(user_id=user_id, picture_id=picture_id, rating=rating, added_after=added_after)

        # Assert that the result is a list of UserResponse objects
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

        # Assert that the user_id filter is applied correctly
        assert all(user.id == user_id for user in result)

        # Assert that the picture_id filter is applied correctly
        assert all(user.picture_count >= picture_id for user in result)

        # Assert that the rating filter is applied correctly
        assert all(user.picture_count >= rating for user in result)

        # Assert that the added_after filter is applied correctly
        assert all(user.picture_count >= added_after for user in result)
