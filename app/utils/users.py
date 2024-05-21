import os
import typing as tp

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.schemas import users
from app import db

from fastapi import Depends, HTTPException, status, Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.utils import get_file_by_path


SECRET_KEY = get_file_by_path(os.environ.get("SECRET_KEY"))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10
REFRESH_TOKEN_EXPIRE_MINUTES = 10080

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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


async def authenticate_user_session(conn: AsyncSession, fingerprint: str, user_id: int):
    session = await get_session(user_id=user_id, fingerprint=fingerprint, conn=conn)
    return session is not None


async def get_current_user(
    request: Request, conn: tp.Annotated[AsyncSession, Depends(db.get_db)]
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = request.headers.get("Authorization")
        if token:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = int(payload.get("sub"))
            if user_id is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    fingerprint = request.headers.get("X-Fingerprint-ID")
    if (fingerprint is None) or (
        not await authenticate_user_session(
            conn=conn, fingerprint=fingerprint, user_id=user_id
        )
    ):
        raise credentials_exception

    user: tp.Optional[users.User] = await get_user_by_user_id(conn=conn, id=user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: tp.Annotated[users.User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_user_by_email(email: str, conn: AsyncSession):
    query = select(
        users.User.id,
        users.User.email,
        users.User.first_name,
        users.User.last_name,
        users.User.password,
        users.User.disabled,
    ).where(users.User.email == email)
    return (await conn.exec(query)).fetchone()


async def get_user_by_user_id(id: int, conn: AsyncSession):
    query = select(
        users.User.id,
        users.User.email,
        users.User.first_name,
        users.User.last_name,
        users.User.password,
        users.User.disabled,
    ).where(users.User.id == id)
    return (await conn.exec(query)).fetchone()


async def get_session(user_id: int, fingerprint: str, conn: AsyncSession):
    query = select(users.Sessions.user_id, users.Sessions.session_id).where(
        users.Sessions.user_id == user_id, users.Sessions.session_id == fingerprint
    )
    return (await conn.exec(query)).fetchone()
