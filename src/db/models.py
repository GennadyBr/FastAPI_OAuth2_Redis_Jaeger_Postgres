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

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    login = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean(), default=True)
    password = Column(String, nullable=False, unique=True)


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)   # я подумал что название ролей должно быть уникальным


class Entry(Base):
    __tablename__ = "entry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    user_agent = Column(String)# что пустая стока, что null не несут полезной информации
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    refresh_token = Column(String, default='')
    is_active = Column(Boolean(), default=True)


class UserRole(Base):
    __tablename__ = "user_role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.id), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey(Role.id), nullable=False)
