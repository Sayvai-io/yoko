from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status
import uuid
import os
from db.models import User, Chat, Message, File, MessageTypeEnum, generate_unique_uid
from db.repositories import *
from openai import OpenAI
import fastapi
import bcrypt

def hash_password(password: str) -> str:
    """Hash a plain password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


class BaseService:
    """Base service class with common functionality"""
    def __init__(self, session: Session):
        self.db = session
        self.user_repo = UserRepository(session)

class UserService(BaseService):
    def add_user(self, email: str, password: str, role: str = "user", subscription_type: str = "free") -> User:
        hashed_pwd = hash_password(password)
        return self.user_repo.create_user(
            email=email,
            password=hashed_pwd,
            role=role,
            subscription_type=subscription_type
        )

    def verify_user_password(self, user: User, plain_password: str) -> bool:
        return verify_password(plain_password, user.password)

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
        self.chat_repo = ChatRepository(db=db, user_id=user_id)

    def set_chat_title_with_prompt(self,prompt:str) -> str:
        system_prompt = (
            "You are an expert fashion assistant helping tailors and designers. "
            "Your only task is to generate a concise, professional 2–3 word title for a dress design prompt. "
            "The title must reflect the core idea, mood, or style described in the prompt. "
            "Avoid generic words like 'design' or 'dress' unless absolutely essential. "
            "Never ask for clarification or provide explanations. "
            "Just return the 2–3 word title only — no other text. "
            "If you can't get the context, just return 'Untitled Chat'."
        )

        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": system_prompt}] + [
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()


    def create_chat(self, title: Optional[str] = None, chat_uid: Optional[str] = generate_unique_uid(model=Chat, field='chat_uid')) -> Chat:
        return self.chat_repo.create_chat(title=title, chat_uid = chat_uid)

    def update_chat_title(self, title: str, chat_uid: str) -> Chat:
        chat = self.get_chat_by_uid(chat_uid)
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
        return self.chat_repo.update_chat_title(title, chat_uid)

    def get_user_chats(self) -> List[Chat]:
        return self.chat_repo.get_user_chats()

    def get_chat_by_uid(self, chat_uid: str) -> Optional[Chat]:
        return self.chat_repo.get_chat_by_uid(chat_uid=chat_uid)

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
            # title = self.chat_service.set_chat_title_with_prompt(prompt = message)
            title = "Untitled Chat"
            chat = self.chat_service.create_chat(title=title, chat_uid=chat_uid)
        msg = Message(user_id=self.user_id, chat_id=chat.id, message=message, response=response, message_type=message_type)
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

    def create_file(self, title: str, zip_file_link: str) -> File:
        db_file = File(
            user_id=self.user_id,
            title=title,
            zip_file_link=zip_file_link
        )
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        return db_file

    def get_user_files(self) -> List[File]:
        return self.db.query(File).filter(File.user_id == self.user_id).all()

    def get_file_by_uid(self, file_uid: str) -> Optional[File]:
        return self.db.query(File).filter(File.uid == file_uid, File.user_id == self.user_id).first()

    def update_file_title(self, file_uid: str, new_title: str) -> Optional[File]:
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
