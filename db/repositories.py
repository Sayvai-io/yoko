from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
from db.models import User, Chat, Message, Model

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
