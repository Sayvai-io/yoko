from sqlalchemy.orm import Session
from .models import *
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

# User Services
class UserService:
    def create_user(db: Session, email: str, password: str, role: str = "user", subscription_type: str = "free"):
        db_user = User(
            email=email,
            password=password,
            role=role,
            subscription_type=subscription_type
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_user_by_id(db: Session, user_id: int):
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_uuid(db: Session, user_uuid: str):
        return db.query(User).filter(User.uuid == user_uuid).first()

    def get_user_by_email(db: Session, email: str):
        return db.query(User).filter(User.email == email).first()

    def delete_user(db: Session, user_uuid: str):
        db_user = get_user_by_uuid(db, user_uuid)
        if db_user:
            db.delete(db_user)
            db.commit()
            return True
        return False
