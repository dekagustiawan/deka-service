from sqlalchemy.orm import Session
from app.models.user import User
from app.utils import pwd_context


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return False
    return user
