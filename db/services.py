from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
import uuid
from db.models import User, Chat, Message, Model

class BaseService:
    """Base service class with common functionality"""
    def __init__(self, session: Session):
        self.db = session

class UserService(BaseService):
    def create_user(self, email: str, password: str, role: str = "user", subscription_type: str = "free") -> User:
        db_user = User(
            email=email,
            password=password,
            role=role,
            subscription_type=subscription_type
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_uuid(self, user_uuid) -> Optional[User]:
        print(self.db.query(User).filter(User.uuid == user_uuid).first())
        return self.db.query(User).filter(User.uuid == user_uuid).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def delete_user(self, user_uuid: uuid.UUID) -> bool:
        db_user = self.get_user_by_uuid(user_uuid)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

class ChatService(BaseService):
    def __init__(self, db: Session, user_id: int):
        super().__init__(db)
        self.user_id = user_id

    def create_chat(self, title: Optional[str] = "Untitled Chat") -> Chat:
        chat = Chat(user_id=self.user_id, title=title)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_user_chats(self) -> List[Chat]:
        return self.db.query(Chat).filter_by(user_id=self.user_id).order_by(Chat.created_at.desc()).all()

    def get_chat_by_uuid(self, chat_uuid: uuid.UUID) -> Optional[Chat]:
        return self.db.query(Chat).filter_by(user_id=self.user_id, uuid=chat_uuid).first()

    def delete_chat(self, chat_uuid: uuid.UUID) -> bool:
        chat = self.get_chat_by_uuid(chat_uuid)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        # Delete associated messages
        self.db.query(Message).filter_by(chat_id=chat.id).delete()
        self.db.delete(chat)
        self.db.commit()
        return True

class MessageService(BaseService):
    def __init__(self, db: Session, user_id: int):
        super().__init__(db)
        self.user_id = user_id

    def add_message(self, chat_id: int, message: str, response: Optional[str] = None) -> Message:
        chat = self.db.query(Chat).filter_by(id=chat_id, user_id=self.user_id).first()
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found or access denied")

        msg = Message(user_id=self.user_id, chat_id=chat_id, message=message, response=response)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_message_by_uuid(self, message_uuid: uuid.UUID) -> Optional[Message]:
        return self.db.query(Message).filter_by(uuid=message_uuid, user_id=self.user_id).first()

    def delete_message(self, message_uuid: uuid.UUID) -> bool:
        msg = self.get_message_by_uuid(message_uuid)
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        self.db.delete(msg)
        self.db.commit()
        return True

    def update_message(self, message_uuid: uuid.UUID, new_message: str, new_response: Optional[str] = None) -> Message:
        msg = self.get_message_by_uuid(message_uuid)
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        msg.message = new_message
        if new_response is not None:
            msg.response = new_response
        self.db.commit()
        return msg

    def get_messages_by_chat(self, chat_uuid: uuid.UUID) -> List[Message]:
        chat = self.db.query(Chat).filter_by(uuid=chat_uuid, user_id=self.user_id).first()
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        return self.db.query(Message).filter_by(chat_id=chat.id).order_by(Message.created_at.asc()).all()

class FileService(BaseService):
    def __init__(self, db: Session, user_id: int):
        super().__init__(db)
        self.user_id = user_id

    def create_file(self, title: str, zip_file_link: str) -> Model:
        db_file = Model(
            user_id=self.user_id,
            title=title,
            zip_file_link=zip_file_link
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def get_user_files(self) -> List[Model]:
        return self.db.query(Model).filter(Model.user_id == self.user_id).all()

    def get_file_by_uuid(self, file_uuid: uuid.UUID) -> Optional[Model]:
        return self.db.query(Model).filter(Model.uuid == file_uuid, Model.user_id == self.user_id).first()

    def update_file_title(self, file_uuid: uuid.UUID, new_title: str) -> Optional[Model]:
        db_file = self.get_file_by_uuid(file_uuid)
        if db_file:
            db_file.title = new_title
            self.db.commit()
            self.db.refresh(db_file)
            return db_file
        return None

    def delete_file(self, file_uuid: uuid.UUID) -> bool:
        db_file = self.get_file_by_uuid(file_uuid)
        if db_file:
            self.db.delete(db_file)
            self.db.commit()
            return True
        return False
