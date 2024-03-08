from typing import Optional

import httpx
import redis.asyncio as redis
import uvicorn

from fastapi import FastAPI, Request
from fastapi.params import Depends
from fastapi_limiter import FastAPILimiter
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.routes import users, auth, messages, tags, search, comments, pictures, descriptions, admin

from src.database.db import get_db
from src.database.models import User
from src.services.auth import auth_service
from src.services.secrets_manager import get_secret


app = FastAPI()

templates = Jinja2Templates(directory='templates')

# Define allowed origins for CORS (Cross-Origin Resource Sharing)
origins = [
    "http://localhost:8000"
    ]

# Add CORS middleware to allow requests from the defined origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix='/api')
app.include_router(users.router, prefix='/api')
app.include_router(messages.router, prefix='/api')
app.include_router(search.router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(tags.router, prefix='/api')
app.include_router(pictures.router, prefix='/api')
app.include_router(admin.router, prefix='/api')
app.include_router(descriptions.router, prefix='/api')


REDIS_HOST = get_secret("REDIS_HOST")
REDIS_PORT = get_secret("REDIS_PORT")
REDIS_PASSWORD = get_secret("REDIS_PASSWORD")


@app.on_event("startup")
async def startup():
    """
    Function to initialize FastAPILimiter on application startup.
    """
    r = await redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        password=REDIS_PASSWORD,
        encoding="utf-8",
        decode_responses=True
    )
    await FastAPILimiter.init(r)


@app.get("/")
async def index(request: Request,
                db: Session = Depends(get_db),
                current_user: User = Depends(auth_service.get_current_user_optional)
                ):
    user = None
    if current_user:
        user = db.query(User).filter(User.id == current_user.id).first()

    print(user)
    context = {'request': request, 'user': user}
    return templates.TemplateResponse('index.html', context)


@app.get("/pictures")
async def pictures(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:8000/api/pictures/?skip=0&limit=20')
        pictures = response.json()

    return templates.TemplateResponse('pictures.html',
                                      {'request': request,
                                       'pictures': pictures})


@app.get('/users')
async def users(request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:8000/api/users/all')
        users = response.json()
        print(f'{users}')

    return templates.TemplateResponse('users.html',
                                      {'request': request,
                                       'users': users})


@app.get("/users/{user_id}")
async def show_user(request: Request, user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return templates.TemplateResponse("user_details.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login_form(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    errors = []

    # Validate inputs
    if not email or not password:
        errors.append('Please enter a valid email address and password.')

    # Attempt to retrieve the user and verify credentials
    user = db.query(User).filter(User.email == email).first() if not errors else None
    if user and auth_service.verify_password(password, user.password):
        # Create tokens
        data = {"sub": email}
        jwt_token = auth_service.create_access_token(data=data)
        jwt_refresh_token = auth_service.create_refresh_token(data=data)

        # Prepare the successful login response
        response = templates.TemplateResponse('index.html', {'request': request, 'user': user})
        response.set_cookie(key='access_token', value=f'Bearer {jwt_token}', httponly=True)
        response.set_cookie(key="refresh_token", value=jwt_refresh_token, httponly=True)
        return response
    else:
        # Handle invalid credentials or other errors
        errors.append('Invalid email or password.')

    # Use a single point for rendering the error response
    return templates.TemplateResponse('login.html', {'request': request, 'errors': errors})



if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
