from datetime import datetime
from fastapi import FastAPI
from src.services.search import search_pictures, search_users, search_users_with_photos, search_comments
from src.database.models import User, Picture
from typing import List
from src.services.auth import Auth


app = FastAPI()


@app.get("/search/pictures")
async def search_pictures_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    pictures = search_pictures(keywords_or_tags=query.split())
    if tags:
        pictures = [picture for picture in pictures if any(tag.name in tags for tag in picture.tags)]
    if rating is not None:
        pictures = [picture for picture in pictures if picture.rating == rating]
    if date_added is not None:
        start_date = datetime.combine(date_added, datetime.min.time())
        end_date = datetime.combine(date_added, datetime.max.time())
        pictures = [picture for picture in pictures if start_date <= picture.created_at <= end_date]
    return pictures


@app.get("/search/users")
async def search_users_endpoint(query: str, tags: List[str] = None, rating: int = None, date_added: datetime = None):
    users = search_users(keywords=query.split())
    if tags:
        users = [user for user in users if any(tag.name in tags for tag in user.tags)]
    if rating is not None:
        users = [user for user in users if user.rating == rating]
    if date_added is not None:
        start_date = datetime.combine(date_added, datetime.min.time())
        end_date = datetime.combine(date_added, datetime.max.time())
        users = [user for user in users if start_date <= user.created_at <= end_date]
    return users


get_current_user = Auth.get_current_user


@app.get("/search/users/photos")
async def search_users_with_photos_endpoint(query: str = '', picture_ids: List[int] = None, current_user: User = get_current_user):
    users = search_users(keywords=query.split())
    if picture_ids:
        pictures = Picture.query.filter(Picture.id.in_(picture_ids)).all()
        user_ids = {picture.user_id for picture in pictures}
        users = [user for user in users if user.id in user_ids]
    return users


@app.get("/search/comments")
async def search_comments_endpoint(query: str, tag_names: List[str] = None):
    comments = search_comments(keywords=query.split())
    if tag_names:
        comments = search_comments(tag_names)
    return comments