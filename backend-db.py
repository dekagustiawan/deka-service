from fastapi import FastAPI, Depends, HTTPException, Security, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()
security = HTTPBearer()

# Example secret key for JWT (replace with your own secret key)
SECRET_KEY = "mysecretkey"

# Example MySQL connection string (replace with your own connection details)
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root@localhost/db_deka"

# Example user credentials (replace with your own authentication logic)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255))

# Configure password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Create the MySQL engine and session
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ExampleRequest(BaseModel):
    name: str

class ExampleResponse(BaseModel):
    message: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user or not pwd_context.verify(password, user.password_hash):
        return False
    return True

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

@app.post('/api/example', response_model=ExampleResponse)
def example(
    request: ExampleRequest,
    db=Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Security(security),
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload["sub"]
        name = request.name
        message = f"Hello, {name}! User: {username}"
        response = ExampleResponse(message=message)

        # Create a response object and add the JWT token to the headers
        custom_response = Response(content=response.json())
        custom_response.headers["Authorization"] = f"Bearer {token}"

        return custom_response
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

@app.post('/api/login')
def login(username: str, password: str, db=Depends(get_db)):
    if authenticate_user(username, password, db):
        token = jwt.encode({"sub": username}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid username or password")

# Create a new user
@app.post("/users")
def create_user(username: str, password: str, db=Depends(get_db)):
    user = User(username=username, password_hash=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# Get a user by ID
@app.get("/users/{user_id}")
def get_user(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update a user by ID
@app.put("/users/{user_id}")
def update_user(user_id: int, username: str, password: str, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.username = username
    user.password_hash = password
    db.commit()
    db.refresh(user)
    return user

# Delete a user by ID
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db=Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

# Generate Swagger/OpenAPI documentation
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="FastAPI Example API",
        version="1.0.0",
        description="This is an example API demonstrating FastAPI with JWT authentication.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Route to serve the Swagger UI
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="FastAPI Example API",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

# Route to serve the OpenAPI schema
@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return app.openapi()
