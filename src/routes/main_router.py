from fastapi import Request, HTTPException, APIRouter
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates
from src.database.db import get_db
from src.database.models import User, Picture
from src.services.auth import auth_service

templates = Jinja2Templates(directory='templates')
router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def index(request: Request,
                db: Session = Depends(get_db),
                current_user: User = Depends(auth_service.get_current_user_optional)
                ):
    if current_user is None:
        return RedirectResponse(url='/login', status_code=status.HTTP_302_FOUND)

    user = db.query(User).filter(User.id == current_user.id).first()
    pictures = db.query(Picture).all()

    context = {'request': request, 'user': user, 'pictures': pictures}
    return templates.TemplateResponse('home.html', context)


@router.get('/users')
async def users(request: Request,
                db: Session = Depends(get_db),
                current_user: User = Depends(auth_service.get_current_user_optional),
                ):
    if current_user is None or not current_user.admin:
        return RedirectResponse(url='/login', status_code=status.HTTP_401_UNAUTHORIZED)

    if current_user:
        user = db.query(User).filter(User.id == current_user.id).first()
        if user.admin:
            users_details = db.query(User).all()
            context = {'request': request, 'user': user, 'users_details': users_details}
            return templates.TemplateResponse('users.html', context)

    return RedirectResponse(url='/', status_code=status.HTTP_401_UNAUTHORIZED)


@router.get("/users/{user_id}")
async def show_user(request: Request,
                    user_id: int,
                    db: Session = Depends(get_db),
                    current_user: User = Depends(auth_service.get_current_user_optional)
                    ):
    user = db.query(User).filter(User.id == user_id).first()
    context = {"request": request, "user": user, 'current_user': current_user}

    return templates.TemplateResponse("user_details.html", context)


@router.post("/users/toggle-ban/{user_id}", response_class=HTMLResponse)
async def toggle_ban_user_by_admin(user_id: int,
                                   db: Session = Depends(get_db),
                                   current_user: User = Depends(auth_service.get_current_user_optional)
                                   ):
    if not current_user or not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action.")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    # Toggle the ban status
    user.ban_status = not user.ban_status
    db.commit()

    return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/users/delete/{user_id}")
async def delete_user(user_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user_optional)
                      ):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    # Check if the current user is trying to delete their own account or is an admin
    if current_user.id != user_id and not current_user.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action.")

    user_to_delete = db.query(User).filter(User.id == user_id).first()
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db.delete(user_to_delete)
    db.commit()

    if current_user.admin:
        return RedirectResponse(url="/users", status_code=status.HTTP_303_SEE_OTHER)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login", response_class=HTMLResponse)
async def authentication_page(request: Request):
    return templates.TemplateResponse('login.html', {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_form(request: Request,
                     db: Session = Depends(get_db)
                     ):
    form = await request.form()
    email = form.get('email')
    password = form.get('password')
    errors = []

    user = db.query(User).filter(User.email == email).first() if not errors else None

    if user.ban_status:
        msg = 'User is Baned'
        context = {'request': request, 'msg': msg}
        return templates.TemplateResponse('login.html', context)

    if user and auth_service.verify_password(password, user.password):
        data = {"sub": email}
        jwt_token = auth_service.create_access_token(data=data)
        jwt_refresh_token = auth_service.create_refresh_token(data=data)
        pictures = db.query(Picture).all()

        context = {'request': request, 'user': user, 'pictures': pictures}
        response = templates.TemplateResponse('home.html', context)
        response.set_cookie(key='access_token', value=f'Bearer {jwt_token}', httponly=True)
        response.set_cookie(key="refresh_token", value=jwt_refresh_token, httponly=True)
        return response
    else:
        msg = 'Incorrect Username or Password'

    context = {'request': request, 'msg': msg}
    return templates.TemplateResponse('login.html', context)


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request, response: Response):
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    return response
