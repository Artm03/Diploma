from pydantic.types import constr
import datetime
from pydantic import BaseModel, EmailStr

from app.db_base import Base

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from sqlalchemy_utils import EmailType, force_auto_coercion, PasswordType


force_auto_coercion()



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
    password = Column(PasswordType(schemes=["pbkdf2_sha512"]), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow())
