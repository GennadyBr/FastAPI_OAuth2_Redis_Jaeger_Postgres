import uuid
from datetime import datetime

from sqlalchemy import Column, Boolean, String, ForeignKey, DateTime
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
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    login = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    password = Column(String, nullable=False)


class Role(Base):
    __tablename__ = 'role'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)


class Entry(Base):
    __tablename__ = 'entry'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.uuid), nullable=False)
    user_agent = Column(String)
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    refresh_token = Column(String)
    is_active = Column(Boolean(), default=True)


class UserRole(Base):
    __tablename__ = 'user_role'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.uuid), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey(Role.uuid), nullable=False)
