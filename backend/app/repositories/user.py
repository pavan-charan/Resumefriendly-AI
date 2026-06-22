from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.models.user import User
from app.schemas.auth import UserCreate

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, user_create: UserCreate, hashed_password: str) -> User:
        db_user = User(
            email=user_create.email,
            password_hash=hashed_password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            role=user_create.role
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
