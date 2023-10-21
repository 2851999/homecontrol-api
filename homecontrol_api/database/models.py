import uuid

from sqlalchemy import Boolean, Column, DateTime, LargeBinary, String, Uuid
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserInDB(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(LargeBinary)
    account_type = Column(String)
    enabled = Column(Boolean)


class UserSessionInDB(Base):
    __tablename__ = "user_sessions"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    long_lived = Column(Boolean)
    expiry_time = Column(DateTime)
