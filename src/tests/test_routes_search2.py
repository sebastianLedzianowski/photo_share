import unittest
import pytest
import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, Mock

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, query
from sqlalchemy.pool import StaticPool
from typing import List, Optional
from pydantic import BaseModel
import httpx
import faker

from src.routes.search import search_pictures, search_users, search_users_by_picture, router
from src.services.search import PictureSearchService, UserSearchService, UserPictureSearchService
from src.tests.conftest import client, session
from src.database.models import Picture, Tag, User
from src.database.db import get_db, SessionLocal
from src.schemas import PictureResponse, PictureSearch, UserResponse


Base = declarative_base()


# models

class Picture(Base):
    __tablename__ = "picture"

    id = Column(Integer, primary_key=True, index=True)
    picture_name = Column(String(255), nullable=True)
    rating = Column(Integer, nullable=True)
    description = Column(String, nullable=True)
    created_at = Column('created_at', DateTime, default=func.now())

    user_id = Column('user_id', ForeignKey('user.id', ondelete='CASCADE'), default=None)
    user = relationship('User', back_populates='pictures')
    tags = relationship('Tag', secondary='picture_tags_association', back_populates='pictures')

    def dict(self):
        return {
            "id": self.id,
            "picture_name": self.picture_name,
            "rating": self.rating,
            "description":self.description,
            "created_at":self.created_at,
            "user_id":self.user_id,
            "user":self.user,
            "tags":self.tags
        }

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    pictures = relationship('Picture', back_populates='user')

    def dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
        }


# database

DATABASE_URL = "sqlite://test_routes_search.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()


app.on_event("start_up")
async def startup():
    Base.metadata.create_all(bind=engine)
    

app.get("/")
def read_root():
    return "Server is Running"



class TestPictureSearch(unittest.TestCase):

    def test_search_pictures_by_tags(self, picture, client):
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
