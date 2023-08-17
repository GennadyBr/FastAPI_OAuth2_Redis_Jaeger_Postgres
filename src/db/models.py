import uuid
from datetime import datetime

from sqlalchemy import Column, Boolean, String, ForeignKey, DATETIME, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

##############################
# BLOCK WITH DATABASE MODELS #
##############################
# это алхимия
# пайдентик на одной стороне, а алхимия на стороне приложения с базой данных

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    login = Column(String(100), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    password = Column(String(100), nullable=False)


class Role(Base):
    __tablename__ = 'role'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)   # я подумал что название ролей должно быть уникальным


class Entry(Base):
    __tablename__ = 'entry'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.uuid), nullable=False)
    user_agent = Column(String(100))
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    refresh_token = Column(String(100))
    is_active = Column(Boolean(), default=True)


class UserRole(Base):
    __tablename__ = 'user_role'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.uuid), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey(Role.uuid), nullable=False)
