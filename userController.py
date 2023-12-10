from connection import get_user_by_username
from sqlalchemy.orm import Session

def authenticate_user(db: Session, username: str, user_key: str):
    user = get_user_by_username(db=db, username=username, user_key=user_key)
    if not user:
        return False
    return user