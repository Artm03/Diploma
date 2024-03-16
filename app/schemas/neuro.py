from pydantic import BaseModel

from app.db_base import Base

from fastapi import UploadFile

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey
)
from sqlalchemy_utils import force_auto_coercion


force_auto_coercion()


class FileWithName(BaseModel):
    file: UploadFile
    name: str


class UsersImages(Base):
    __tablename__ = "users_images"

    id = Column(Text, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    filename = Column(Text, nullable=False)


class ImagesPeople(Base):
    __tablename__ = "images_names"
    id = Column(Text, nullable=False, primary_key=True)
    image_id = Column(Text, ForeignKey('users_images.id', ondelete='CASCADE'), nullable=False)
    name = Column(Text, nullable=False)
