from sqlalchemy.orm import Session
from typing import Optional

from app.models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.get(User, user_id)

def create_user(db: Session, payload: UserCreate) -> User:
    hashed = get_password_hash(payload.password)
    user = User(username=payload.username, email=payload.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user