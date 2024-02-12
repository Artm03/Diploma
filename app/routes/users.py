import typing as tp

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app import db
from app.api import v1_user_registry_post as user_registry_api
from app.api import token
from app.schemas import users

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


@router.post('/v1/user/registry')
async def v1_user_registry_post(
    user: users.UserCreate,
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await user_registry_api.handle(user=user, conn=conn)


@router.post("/token")
async def login_for_access_token(
    form_data: tp.Annotated[OAuth2PasswordRequestForm, Depends()],
    conn: tp.Annotated[AsyncSession, Depends(db.get_db)],
):
    return await token.handle(form_data=form_data, conn=conn)
