import typing as tp

from fastapi import APIRouter, Depends, Response, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from app.oauth2 import AuthJWT

from app import db
from app.api import v1_user_registry_post as user_registry_api
from app.api import token
from app.api import refresh
from app.api import logout
from app.schemas import users as user_model
from app.utils import users

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post('/v1/user/registry')
async def v1_user_registry_post(
    user: user_model.UserCreate,
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await user_registry_api.handle(user=user, conn=conn)


@router.post("/v1/user/login")
async def login_for_access_token(
    form_data: tp.Annotated[OAuth2PasswordRequestForm, Depends()],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    response: Response,
    Authorize: tp.Annotated[AuthJWT, Depends()],
):
    return await token.handle(form_data=form_data, conn=conn, response=response, Authorize=Authorize)


@router.get("/v1/user/me", response_model=user_model.UserModel)
async def read_users_me(
    current_user: tp.Annotated[user_model.UserModel, Depends(users.get_current_active_user)],
):
    return current_user


@router.get("/v1/user/refresh")
async def refresh_token(
    response: Response,
    request: Request,
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
    Authorize: tp.Annotated[AuthJWT, Depends()],
):
    return await refresh.handle(conn=conn, request=request, response=response, Authorize=Authorize)


@router.get('/v1/user/logout')
async def logout_user(response: Response, Authorize: AuthJWT = Depends()):
    return await logout.handle(response=response, Authorize=Authorize)
