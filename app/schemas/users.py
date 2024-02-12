from pydantic.types import constr
import datetime
from pydantic import BaseModel, EmailStr
import typing as tp

from app.db_base import Base

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Boolean,
    Text,
)

from sqlalchemy_utils import EmailType, force_auto_coercion, PasswordType


force_auto_coercion()



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class UserModel(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    disabled: tp.Optional[bool] = None


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: constr(strip_whitespace=True, min_length=8) # type: ignore
    class Config:
        orm_mode = True


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(EmailType(50), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    password = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
    disabled = Column(Boolean, nullable=False, default=False)
