from pydantic import BaseModel, EmailStr
from pydantic.types import constr


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: constr(strip_whitespace=True, min_length=8)


class Login(BaseModel):
    email: EmailStr
    password: constr(strip_whitespace=True, min_length=8)
