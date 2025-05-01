from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from db.db_config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=str(uuid.uuid4))
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="user")
    subscription_type = Column(String(50), default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    uuid = Column(String(36), unique=True, index=True, default=str(uuid.uuid4))
    title = Column(String(255), default="Untitled Chat")
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), index=True)
    uuid = Column(String(36), unique=True, index=True, default=str(uuid.uuid4))
    message = Column(Text)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    uuid = Column(String(36), unique=True, index=True, default=str(uuid.uuid4))
    title = Column(String(255))
    zip_file_link = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
