import uuid
from datetime import datetime

from sqlalchemy import Column, Boolean, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship

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
    entries = relationship("Entry",
                           back_populates="user",
                           cascade="all, delete",
                           passive_deletes=True, )
    user_roles = relationship("UserRole",
                              back_populates="user",
                              cascade="all, delete",
                              passive_deletes=True, )


class Role(Base):
    __tablename__ = 'role'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False, unique=True)  # я подумал что название ролей должно быть уникальным
    user_roles = relationship("UserRole",
                              back_populates="role",
                              cascade="all, delete",
                              passive_deletes=True, )


class Entry(Base):
    __tablename__ = 'entry'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.uuid, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user_agent = Column(String(100))
    date_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    refresh_token = Column(String(100))
    is_active = Column(Boolean(), default=True)
    user = relationship("User", back_populates="entries")


class UserRole(Base):
    __tablename__ = 'user_role'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey(User.uuid, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey(Role.uuid, onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    user = relationship("User", back_populates="user_roles")
    role = relationship("Role", back_populates="user_roles")


class UserSocial(Base):
    __tablename__ = 'user_socials'

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sub_id = Column(UUID(as_uuid=True), nullable=False)
    provider = Column(String(100))
