from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, OAuth2PasswordBearer
import jwt
from app.services.auth_service import authenticate_user
from app.config import SECRET_KEY
from app.utils import get_db
from sqlalchemy.orm import Session

router = APIRouter()
security = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

@router.post('/api/login')
def login(username: str, password: str, db: Session = Depends(get_db)):
    if authenticate_user(username, password, db):
        token = jwt.encode({"sub": username}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid username or password")

@router.post('/api/example')
def example(request: dict, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["sub"]
        name = request["name"]
        message = f"Hello, {name}! User: {username}"
        return {"message": message}
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
