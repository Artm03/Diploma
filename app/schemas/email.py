import datetime

from pydantic import EmailStr, BaseModel

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Text,
)
from sqlalchemy_utils import EmailType, force_auto_coercion

from app.db_base import Base


force_auto_coercion()


class EmailSchema(BaseModel):
    email: EmailStr


class EmailSend(Base):
    __tablename__ = "emails_send"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(EmailType(50), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now(datetime.timezone.utc))
    expired_at = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10))
    code = Column(Text, nullable=False)
    type = Column(Text, nullable=False)
