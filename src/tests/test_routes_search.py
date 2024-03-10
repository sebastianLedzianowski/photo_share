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
from src.tests.conftest import login_user_confirmed_true_and_hash_password, login_as_admin, user_s, picture_s
from src.tests.test_routes_auth import login_user_token_created
from src.services.auth import auth_service
from main import app


class Test_Search_Picture:

    # The function returns a list of PictureResponse objects when given valid search parameters.
    def test_valid_search_parameters(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function returns an empty list when given an empty search_params object.
    def test_empty_search_params(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = []

        # Call the search_pictures function with an empty search_params object
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function returns a list of PictureResponse objects when given valid search parameters and a valid database connection.
    def test_valid_search_parameters(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function returns a list of PictureResponse objects sorted by created_at in descending order by default.
    def test_default_sort_order(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with default sort order
        result = self.search_pictures(PictureSearch())

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

        # Assert that the search_pictures method was called with the correct parameters
        mock_service.search_pictures.assert_called_once_with(PictureSearch(), "created_at", "desc")

    # The function returns a list of PictureResponse objects sorted by the specified sort_by parameter in the specified sort_order parameter.
    def test_search_pictures_sorting(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with different sort_by and sort_order parameters
        result1 = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')
        result2 = self.search_pictures(PictureSearch(), sort_by='likes', sort_order='asc')
        result3 = self.search_pictures(PictureSearch(), sort_by='views', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result1, list)
        assert all(isinstance(picture, PictureResponse) for picture in result1)
        assert isinstance(result2, list)
        assert all(isinstance(picture, PictureResponse) for picture in result2)
        assert isinstance(result3, list)
        assert all(isinstance(picture, PictureResponse) for picture in result3)

        # Assert that the results are sorted correctly
        assert result1 == [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]
        assert result2 == [PictureResponse(id=2, url='example.com/pic2.jpg'), PictureResponse(id=1, url='example.com/pic1.jpg')]
        assert result3 == [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

    # The function returns an empty list when given valid search parameters but an invalid database connection.
    def test_invalid_database_connection(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method to raise an exception
        mock_service.search_pictures.side_effect = Exception("Invalid database connection")

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function returns an empty list when no pictures match the search parameters.
    def test_empty_list_returned_when_no_pictures_match_search_parameters(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method to return an empty list
        mock_service.search_pictures.return_value = []

        # Call the search_pictures function with search parameters that don't match any pictures
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function can handle search_params with multiple fields set to the same value.
    def test_handle_multiple_fields_same_value(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with search_params having multiple fields set to the same value
        search_params = PictureSearch(field1="value", field2="value", field3="value")
        result = self.search_pictures(search_params, sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function can handle large amounts of data without crashing or running out of memory.
    def test_handle_large_amounts_of_data(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)

    # The function returns an empty list when given search_params with all fields set to empty strings.
    def test_empty_search_params(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Call the search_pictures function with empty search_params
        result = self.search_pictures(PictureSearch(), sort_by='created_at', sort_order='desc')

        # Assert that the result is an empty list
        assert result == []

    # The function can handle search_params with multiple fields set to different values.
    def test_handle_multiple_fields(self, mocker):
        # Mock the PictureSearchService
        mock_service = mocker.Mock()
        mocker.patch('src.routes.search.PictureSearchService', return_value=mock_service)

        # Mock the search_pictures method
        mock_service.search_pictures.return_value = [PictureResponse(id=1, url='example.com/pic1.jpg'), PictureResponse(id=2, url='example.com/pic2.jpg')]

        # Call the search_pictures function with multiple fields set to different values
        search_params = PictureSearch(field1='value1', field2='value2', field3='value3')
        result = self.search_pictures(search_params, sort_by='created_at', sort_order='desc')

        # Assert that the result is a list of PictureResponse objects
        assert isinstance(result, list)
        assert all(isinstance(picture, PictureResponse) for picture in result)
        
        


class Test_Search_Users:

    # Returns a list of UserResponse objects when given valid search parameters.
    def test_valid_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)
    
        # Act
        result = search_users(search_params, db)
    
        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Raises an HTTPException with status code 403 when the current user is not a moderator or administrator.
    def test_non_moderator_or_admin_user(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)
    
        # Act and Assert
        with pytest.raises(HTTPException) as exc:
            search_users(search_params, db)
    
        assert exc.value.status_code == 403

    # Returns an empty list when no users match the search parameters.
    def test_returns_empty_list_when_no_users_match_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    # Returns a list of UserResponse objects when given search parameters that match multiple users.
    def test_returns_list_of_user_responses_when_given_matching_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Returns an empty list when given search parameters that do not match any users.
    def test_empty_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0

    # Returns a list of UserResponse objects when given search parameters that match a single user.
    def test_returns_list_of_userresponse_objects_when_given_matching_search_parameters(self):
        # Arrange
        search_params = UserSearch(...)
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Returns a list of UserResponse objects when given search parameters that include a match on a user's email address.
    def test_returns_list_of_userresponse_objects_with_matching_email(self):
        # Arrange
        search_params = UserSearch(email="test@example.com")
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)

    # Returns a list of UserResponse objects when given search parameters that include a match on a user's username.
    def test_returns_list_of_userresponse_objects_with_matching_username(self):
        # Arrange
        search_params = UserSearch(username="john")
        db = Session(...)

        # Act
        result = search_users(search_params, db)

        # Assert
        assert isinstance(result, list)
        assert all(isinstance(user, UserResponse) for user in result)
        

class Test_Search_Users_By_Picture:

    # The function is called with valid user_id, picture_id, rating, and added_after parameters.
    def test_valid_parameters(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with user_id parameter set to a non-existent user id.
    def test_nonexistent_user_id(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=999, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid added_after parameter.
    def test_valid_added_after_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid user_id parameter.
    def test_valid_user_id_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1)

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The current user is a moderator and the function is called with valid parameters.
    def test_valid_parameters(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid rating parameter.
    def test_valid_rating_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.services.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.services.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(rating=5)

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The function is called with valid picture_id parameter.
    def test_valid_picture_id_parameter(self, mocker):
        # Mock the dependencies
        mocker.patch('src.database.db.get_db')
        mocker.patch('src.services.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.services.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(picture_id=1)

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value

    # The current user is an administrator and the function is called with valid parameters.
    def test_valid_parameters(self, mocker):
        # Mock the dependencies
        mocker.patch('src.routes.search.get_db')
        mocker.patch('src.routes.search.get_current_user')

        # Mock the UserPictureSearchService
        mock_search_service = mocker.Mock()
        mocker.patch('src.routes.search.UserPictureSearchService', return_value=mock_search_service)

        # Call the function under test
        result = search_users_by_picture(user_id=1, picture_id=1, rating=5, added_after=datetime.now())

        # Assert the result
        assert result == mock_search_service.search_users_by_picture.return_value