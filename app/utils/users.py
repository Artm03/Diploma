import datetime
import typing as tp

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.schemas import users
from app import db

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext


SECRET_KEY = "2f4658af0a03e1e501dc540da010c5d98ca60270c3e80b6843a92b39692ac869"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_MINUTES = 10080

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def authenticate_user(conn: AsyncSession, user_email: str, password: str):
    user: users.User = await get_user_by_email(email=user_email, conn=conn)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


async def authenticate_user_session(conn: AsyncSession, fingerprint: str, id: int):
    session = await get_session(id=id, fingerprint=fingerprint, conn=conn)
    return session is not None


async def get_current_user(request: Request, token: tp.Annotated[str, Depends(oauth2_scheme)], conn: tp.Annotated[AsyncSession, Depends(db.get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = int(payload.get("sub"))
        if id is None:
            raise credentials_exception
        token_data = users.TokenData(id=id)
    except JWTError:
        raise credentials_exception

    fingerprint = request.headers.get('X-Fingerprint-ID')
    if not fingerprint or not await authenticate_user_session(conn=conn, fingerprint=fingerprint, id=id):
        raise credentials_exception

    user = await get_user_by_user_id(conn=conn, id=token_data.id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: tp.Annotated[users.User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return users.UserModel(
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        disabled=current_user.disabled
    )


async def get_user_by_email(email: str, conn: AsyncSession):
    query = select(users.User.id, users.User.email, users.User.first_name, users.User.last_name, users.User.password, users.User.disabled).where(users.User.email == email)
    res = (await conn.exec(query)).fetchall()
    return res[0] if res else None


async def get_user_by_user_id(id: int, conn: AsyncSession):
    query = select(users.User.id, users.User.email, users.User.first_name, users.User.last_name, users.User.password, users.User.disabled).where(users.User.id == id)
    res = (await conn.exec(query)).fetchall()
    return res[0] if res else None


async def get_session(id: int, fingerprint: str, conn: AsyncSession):
    query = select(users.Sessions.user_id, users.Sessions.session_id).where(users.Sessions.user_id == id, users.Sessions.session_id == fingerprint)
    res = (await conn.exec(query)).fetchall()
    return res[0] if res else None
