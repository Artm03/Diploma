import typing as tp

from fastapi import APIRouter, Depends, Response, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from app.oauth2 import AuthJWT

from app import db
from app.api import v1_user_registry_post as user_registry_api
from app.api import token
from app.api import refresh
from app.api import recovery
from app.api import logout
from app.schemas import users as user_model
from app.utils import users

from fastapi import Depends, Body
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post('/api/v1/user/registry')
async def v1_user_registry_post(
    user: user_model.UserCreate,
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await user_registry_api.handle(user=user, conn=conn)


@router.post("/api/v1/user/login")
async def login_for_access_token(
    request: Request,
    form_data: user_model.UserLogin,
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    response: Response,
    Authorize: tp.Annotated[AuthJWT, Depends()],
):
    return await token.handle(request=request, form_data=form_data, conn=conn, response=response, Authorize=Authorize)


@router.get("/api/v1/user/me")
async def read_users_me(
    current_user: tp.Annotated[user_model.User, Depends(users.get_current_active_user)],
):
    return user_model.UserModel(
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        disabled=current_user.disabled
    )


@router.get("/api/v1/user/refresh")
async def refresh_token(
    request: Request,
    response: Response,
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    Authorize: tp.Annotated[AuthJWT, Depends()],
):
    return await refresh.handle(conn=conn, request=request, response=response, Authorize=Authorize)


@router.get('/api/v1/user/recovery')
async def recovery_password(
    form_data: tp.Annotated[user_model.UserLogin, Body()],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await recovery.handle(form_data=form_data, conn=conn)


@router.get('/api/v1/user/logout')
async def logout_user(
    response: Response,
    current_user: tp.Annotated[user_model.User, Depends(users.get_current_active_user)],
    Authorize: tp.Annotated[AuthJWT, Depends()],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await logout.handle(response=response, user=current_user, Authorize=Authorize, conn=conn)
