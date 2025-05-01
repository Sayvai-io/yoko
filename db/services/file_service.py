from sqlalchemy.orm import Session
from .models import *
from datetime import datetime
from typing import List, Optional
from fastapi import HTTPException, status

# Model Services
# After integrating AWS S3 bucket
class FileService:
    def create_file(db: Session, user_uuid: str, title: str, zip_file_link: str):
        db_file = Model(
            user_uuid=user_uuid,
            title=title,
            zip_file_link=zip_file_link
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
        return db_file

    def get_user_files(db: Session, user_uuid: str):
        return db.query(Model).filter(Model.user_uuid == user_uuid).all()

    def update_file_title(db: Session, model_id: int, new_title: str):
        db_file = db.query(Model).filter(Model.id == model_id).first()
        if db_file:
            db_file.title = new_title
            db.commit()
            db.refresh(db_file)
            return db_file
        return None

    def delete_file(db: Session, model_id: int):
        db_file = db.query(Model).filter(Model.id == model_id).first()
        if db_file:
            db.delete(db_file)
            db.commit()
            return True
        return False
