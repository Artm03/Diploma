import datetime
import typing as tp

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.schemas import users

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext


SECRET_KEY = "2f4658af0a03e1e501dc540da010c5d98ca60270c3e80b6843a92b39692ac869"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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


def create_access_token(data: dict, expires_delta: datetime.timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: tp.Annotated[str, Depends(oauth2_scheme)], conn: AsyncSession):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = users.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(conn=conn, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: tp.Annotated[users.User, Depends(get_current_user)],
    conn: AsyncSession,
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_user_by_email(email: str, conn: AsyncSession):
    query = select(users.User.email, users.User.first_name, users.User.last_name, users.User.password, users.User.disabled).where(users.User.email == email)
    res = (await conn.exec(query)).fetchall()
    return res[0] if res else None
