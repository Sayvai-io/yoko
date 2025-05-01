from sqlalchemy.orm import Session
from .models import *
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

# Message Services
class MessageService:
    def add_message(session: Session, user_id: str, chat_id: int, message: str, response: Optional[str] = None) -> Message:
        chat_exists = session.query(Chat).filter_by(id=chat_id, user_id=user_id).first()
        if not chat_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found or access denied")

        msg = Message(user_id=user_id, chat_id=chat_id, message=message, response=response)
        session.add(msg)
        session.commit()
        session.refresh(msg)
        return msg

    def delete_message(session: Session, message_id: int, user_id: str):
        msg = session.query(Message).filter_by(id=message_id, user_id=user_id).first()
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
        session.delete(msg)
        session.commit()

    def update_message(session: Session, message_id: int, user_id: str, new_message: str, new_response: Optional[str] = None) -> Message:
        msg = session.query(Message).filter_by(id=message_id, user_id=user_id).first()
        if not msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        msg.message = new_message
        if new_response is not None:
            msg.response = new_response
        session.commit()
        return msg

    def get_messages_by_chat(session: Session, chat_id: int, user_id: str) -> List[Message]:
        chat = session.query(Chat).filter_by(id=chat_id, user_id=user_id).first()
        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")

        return session.query(Message).filter_by(chat_id=chat_id).order_by(Message.created_at.asc()).all()
