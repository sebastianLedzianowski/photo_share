from typing import Optional

import httpx
import redis.asyncio as redis
import uvicorn
from fastapi import FastAPI, Request
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_limiter import FastAPILimiter
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.routes import users, auth, messages, tags, search, comments, users_role, pictures
from src.database.db import get_db
from src.database.models import User
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
app.include_router(users_role.router, prefix='/api')
app.include_router(pictures.router, prefix='/api')


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


async def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    user_id = request.cookies.get("user_id")
    if user_id is None:
        return None  # Return None instead of raising an exception
    user = db.query(User).filter(User.id == user_id).first()
    return user


@app.get("/")
async def index(request: Request,
                db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)
                ):
    user = db.query(User).filter(User.id == current_user).first()
    print(user)

    context = {'request': request, 'user': user}

    return templates.TemplateResponse('index.html', context)


@app.get("/pictures")
async def index(request: Request):
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


@app.post("/login")
async def process_login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    form_data_fields = {
        "username": form_data.username,
        "password": form_data.password
    }
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8000/api/auth/login", data=form_data_fields)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            response = RedirectResponse(url="/", status_code=303)
            response.set_cookie(key="access_token", value=access_token, httponly=True)
            response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
            return response
        else:
            return templates.TemplateResponse("login.html", {"request": request, "errors": ["Login failed. Please try again."]})


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
