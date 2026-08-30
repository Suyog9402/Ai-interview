from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password
from typing import Optional
import re

class UserService:
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        # Check if email already exists
        if UserService.get_user_by_email(db, user.email):
            raise ValueError("Email already registered")
        
        # Check if username already exists
        if UserService.get_user_by_username(db, user.username):
            raise ValueError("Username already taken")
        
        # Validate password strength
        if len(user.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Validate username format
        if not re.match(r'^[a-zA-Z0-9_]{3,20}$', user.username):
            raise ValueError("Username must be 3-20 characters and contain only letters, numbers, and underscores")
        
        # Create new user
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_user_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
        
        # Check if new email already exists (if email is being updated)
        if user_update.email and user_update.email != user.email:
            existing_user = UserService.get_user_by_email(db, user_update.email)
            if existing_user:
                raise ValueError("Email already registered")
        
        # Check if new username already exists (if username is being updated)
        if user_update.username and user_update.username != user.username:
            existing_user = UserService.get_user_by_username(db, user_update.username)
            if existing_user:
                raise ValueError("Username already taken")
        
        # Update user fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True 