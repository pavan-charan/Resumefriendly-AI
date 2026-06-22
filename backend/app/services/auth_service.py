from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.repositories.user import UserRepository
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, user_create: UserCreate) -> UserResponse:
        existing_user = self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        hashed_password = get_password_hash(user_create.password)
        db_user = self.user_repo.create(user_create, hashed_password)
        return UserResponse.from_orm(db_user)

    def login(self, user_login: UserLogin) -> Token:
        user = self.user_repo.get_by_email(user_login.email)
        if not user or not verify_password(user_login.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
