from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from db.models import User, Chat, Message, File, generate_unique_uid

class BaseRepository:
    """Base repository class with common functionality"""
    def __init__(self, session: Session):
        self.db = session

class UserRepository(BaseRepository):
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

    def get_user_by_uid(self, user_uid) -> Optional[User]:
        return self.db.query(User).filter(User.user_uid == user_uid).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def delete_user(self, user_uid: str) -> bool:
        db_user = self.get_user_by_uid(user_uid)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

class ChatRepository(BaseRepository):
    def __init__(self, db: Session, user_id: int):
        super().__init__(db)
        self.user_id = user_id

    def create_chat(self, title: Optional[str] = "Untitled Chat", chat_uid: Optional[str] = generate_unique_uid(model=Chat, field='chat_uid')) -> Chat:
        chat = Chat(user_id=self.user_id, title=title, chat_uid = chat_uid)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def update_chat_title(self, title: str, chat_uid: str) -> Chat:
        chat = self.get_chat_by_uid(chat_uid)
        chat.title = title
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_user_chats(self) -> List[Chat]:
        return self.db.query(Chat).filter_by(user_id=self.user_id).order_by(Chat.created_at.desc()).all()

    def get_chat_by_uid(self, chat_uid: str) -> Optional[Chat]:
        chat = self.db.query(Chat).filter_by(user_id=self.user_id, chat_uid=chat_uid).first()
        return chat

    def delete_chat(self, chat_uid: str) -> bool:
        chat = self.get_chat_by_uid(chat_uid)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        # Delete associated messages
        self.db.query(Message).filter_by(chat_id=chat.id).delete()
        self.db.delete(chat)
        self.db.commit()
        return True
