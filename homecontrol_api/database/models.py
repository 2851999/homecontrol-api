import uuid

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, LargeBinary, String, Uuid
from sqlalchemy.orm import declarative_base
from sqlalchemy_json import mutable_json_type

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


class RoomInDB(Base):
    __tablename__ = "rooms"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True)
    # Could use JSONB here when using just PostgreSQL, but for compatibility
    # use plain JSON for now
    controllers = Column(mutable_json_type(dbtype=JSON, nested=True))


class TemperatureInDB(Base):
    __tablename__ = "temperatures"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, index=True)
    value = Column(Float)
    room_name = Column(String, index=True)


class JobInDB(Base):
    __tablename__ = "jobs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    task = Column(String)
    trigger = Column(mutable_json_type(dbtype=JSON, nested=True))
