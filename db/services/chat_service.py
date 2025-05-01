from sqlalchemy.orm import Session
from .models import *
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

# Chat Services
class ChatService:
    def create_chat(session: Session, user_id: str, title: Optional[str] = "Untitled Chat") -> Chat:
        chat = Chat(user_id=user_id, title=title)
        session.add(chat)
        session.commit()
        session.refresh(chat)
        return chat

    def get_user_chats(session: Session, user_id: str) -> List[Chat]:
        return session.query(Chat).filter_by(user_id=user_id).order_by(Chat.created_at.desc()).all()

    def delete_chat(session: Session, chat_id: int, user_id: str):
        chat = session.query(Chat).filter_by(id=chat_id, user_id=user_id).first()
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        # Optionally delete messages in that chat
        session.query(Message).filter_by(chat_id=chat_id).delete()
        session.delete(chat)
        session.commit()
