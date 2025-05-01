from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
import uuid
from db.models import User, Chat, Message, Model, MessageTypeEnum
from db.repositories import UserRepository

class BaseService:
    """Base service class with common functionality"""
    def __init__(self, session: Session):
        self.db = session
        self.user_repo = UserRepository(session)

class UserService(BaseService):
    def add_user(self, email: str, password: str, role: str = "user", subscription_type: str = "free") -> User:
        return self.user_repo.create_user(email=email, password=password, role=role, subscription_type=subscription_type)

    def find_user_by_id(self, user_id: int) -> Optional[User]:
        return self.user_repo.get_user_by_id(user_id=user_id)

    def find_user_by_uid(self, user_uid) -> Optional[User]:
        return self.user_repo.get_user_by_uid(user_uid=user_uid)

    def find_user_by_email(self, email: str) -> Optional[User]:
        return self.user_repo.get_user_by_email(email=email)

    def delete_user(self, user_uid: str) -> bool:
        return self.user_repo.delete_user(user_uid=user_uid)

class ChatService(BaseService):
    def __init__(self, db: Session, user_id: int):
        super().__init__(db)
        self.user_id = user_id

    def create_chat(self, title: Optional[str] = "Untitled Chat", chat_uid: Optional[str] = str(uuid.uuid4())) -> Chat:
        chat = Chat(user_id=self.user_id, title=title, chat_uid = chat_uid)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def update_chat_title(self, title: str, chat_uid: str) -> Chat:
        chat = self.get_chat_by_uid(chat_uid)
        chat.title = title
        self.db.commtt()
        self.db.refresh(chat)
        return chat

    def get_user_chats(self) -> List[Chat]:
        return self.db.query(Chat).filter_by(user_id=self.user_id).order_by(Chat.created_at.desc()).all()

    def get_chat_by_uid(self, chat_uid: str) -> Optional[Chat]:
        return self.db.query(Chat).filter_by(user_id=self.user_id, chat_uid=chat_uid).first()

    def delete_chat(self, chat_uid: str) -> bool:
        chat = self.get_chat_by_uid(chat_uid)
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
        self.chat_service = ChatService(db, user_id)

    def add_message(self, chat_uid: str, message: str, response: Optional[str] = None, message_type: Optional[MessageTypeEnum] = MessageTypeEnum.TEXT) -> Message:
        chat = self.chat_service.get_chat_by_uid(chat_uid)
        if not chat:
            chat = self.chat_service.create_chat(chat_uid=chat_uid)
            print(chat.chat_uid)
        msg = Message(user_id=self.user_id, chat_id=chat.id, message=message, response=response)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_message_by_uid(self, message_uid: str) -> Optional[Message]:
        return self.db.query(Message).filter_by(message_uid=message_uid, user_id=self.user_id).first()

    def delete_message(self, message_uid: str) -> bool:
        msg = self.get_message_by_uid(message_uid)
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        self.db.delete(msg)
        self.db.commit()
        return True

    def update_message(self, message_uid: str, new_message: str, new_response: Optional[str] = None) -> Message:
        msg = self.get_message_by_uid(message_uid)
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        msg.message = new_message
        if new_response is not None:
            msg.response = new_response
        self.db.commit()
        return msg

    def get_messages_by_chat(self, chat_uid: str) -> List[Message]:
        chat = self.chat_service.get_chat_by_uid(chat_uid)
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

    def get_file_by_uid(self, file_uid: str) -> Optional[Model]:
        return self.db.query(Model).filter(Model.uid == file_uid, Model.user_id == self.user_id).first()

    def update_file_title(self, file_uid: str, new_title: str) -> Optional[Model]:
        db_file = self.get_file_by_uid(file_uid)
        if db_file:
            db_file.title = new_title
            self.db.commit()
            self.db.refresh(db_file)
            return db_file
        return None

    def delete_file(self, file_uid: str) -> bool:
        db_file = self.get_file_by_uid(file_uid)
        if db_file:
            self.db.delete(db_file)
            self.db.commit()
            return True
        return False
