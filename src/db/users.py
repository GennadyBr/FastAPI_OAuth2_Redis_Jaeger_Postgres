import uuid
from datetime import datetime


from sqlalchemy import Column, Boolean, String, ForeignKey, DATETIME, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import sessionmaker, declarative_base

##############################
# BLOCK WITH DATABASE MODELS #
##############################
# это алхимия
# пайдентик на одной стороне, а алхимия на стороне приложения с базой данных

Base = declarative_base()


# что бы наследовать модели для общения с алхимией

def default_time():
    return datetime.utcnow()


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    login = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    hashed_password = Column(String, nullable=False, unique=True)  # пока строка


class Role(Base):
    __tablename__ = "role"

    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


class Entry(Base):
    __tablename__ = "entry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.user_id), nullable=False)
    user_agent = Column(String, default='', nullable=False)
    date_time = Column(String, default='default_time', nullable=False)
    refresh_token = Column(String, default='', nullable=False)
    is_active = Column(Boolean(), default=True)


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.user_id), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey(User.user_id), nullable=False)
