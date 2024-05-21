from pydantic import BaseModel
import datetime

from app.db_base import Base

from fastapi import UploadFile

from sqlalchemy import Column, Integer, Text, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy_utils import force_auto_coercion
import typing as tp


force_auto_coercion()


class Gallery(BaseModel):
    id: str
    name: str
    description: tp.Optional[str]


class UserGallery(Base):
    __tablename__ = "galleries"

    id = Column(Text, nullable=False, primary_key=True)
    name = Column(Text, nullable=False)
    description = Column(Text)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class UsersImages(Base):
    __tablename__ = "users_images"

    id = Column(Text, nullable=False, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    gallery_id = Column(
        Text, ForeignKey("galleries.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now(datetime.timezone.utc))


class ImagesPeople(Base):
    __tablename__ = "images_names"
    id = Column(Text, nullable=False, primary_key=True)
    image_id = Column(
        Text, ForeignKey("users_images.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(Text, nullable=False)
