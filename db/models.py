from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
import uuid
from datetime import datetime
import enum
from db.db_config import Base, get_db, engine
Base.metadata.create_all(bind=engine)


db = next(get_db())

def generate_unique_uid(model, field: str) -> str:
    """
    Generate a unique UUID string that doesn't exist for the given model field.

    :param session: SQLAlchemy session object
    :param model: SQLAlchemy model class (e.g., Message)
    :param field: The unique field name to check against (default: 'message_uid')
    :return: A unique UUID string
    """
    while True:
        uid = str(uuid.uuid4())
        exists = db.query(model).filter(getattr(model, field) == uid).first()
        if not exists:
            return uid

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_uid = Column(String(36), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    password = Column(String(255))
    role = Column(String(50), default="user")
    subscription_type = Column(String(50), default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.user_uid:
            self.user_uid = generate_unique_uid(User, 'user_uid')

class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    chat_uid = Column(String(36), unique=True, index=True)
    title = Column(String(255), default="Untitled Chat")
    created_at = Column(DateTime, default=datetime.utcnow)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.chat_uid:
            self.chat_uid = generate_unique_uid(Chat, 'chat_uid')

class MessageTypeEnum(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), index=True)
    message_uid = Column(String(36), unique=True, index=True)
    message = Column(Text)
    message_type = Column(Enum(MessageTypeEnum), default=MessageTypeEnum.TEXT)
    response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.message_uid:
            self.message_uid = generate_unique_uid(Message, 'message_uid')

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    file_uid = Column(String(36), unique=True, index=True)
    title = Column(String(255))
    zip_file_link = Column(String(512))
    created_at = Column(DateTime, default=datetime.utcnow)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.file_uid:
            self.file_uid = generate_unique_uid(File, 'flie_uid')
