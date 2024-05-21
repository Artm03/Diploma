import datetime
from pydantic import BaseModel, EmailStr, Field
import typing as tp

from app.db_base import Base

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    Text,
    ForeignKey
)
from sqlalchemy_utils import EmailType, force_auto_coercion


force_auto_coercion()



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None


class UserModel(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    disabled: tp.Optional[bool] = None


class UserAuthorize(BaseModel):
    username: str
    password: tp.Annotated[str, Field(min_length=8)]


class UserLogin(UserAuthorize):
    email_code: str


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: tp.Annotated[str, Field(min_length=8)]
    email_code: str
    class Config:
        orm_mode = True


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(EmailType(50), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    password = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    disabled = Column(Boolean, default=False)


class Sessions(Base):
    __tablename__ = "users_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    session_id = Column(Text, nullable=False)
