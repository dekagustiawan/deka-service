import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Security, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from pydantic import BaseModel
import jwt
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI()
security = HTTPBearer()

# Get the JWT secret key from an environment variable
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "mysecretkey")

# Get the JWT expiration time from an environment variable
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "30"))

# Example user credentials (replace with your own authentication logic)
USERS = {
    "john": "password123",
    "jane": "qwerty456"
}

class ExampleRequest(BaseModel):
    name: str

class ExampleResponse(BaseModel):
    message: str

def authenticate_user(username: str, password: str):
    if username in USERS and USERS[username] == password:
        return True
    return False

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

@app.post('/api/example', response_model=ExampleResponse)
def example(
    request: ExampleRequest,
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
def login(username: str, password: str):
    if authenticate_user(username, password):
        expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
        token = jwt.encode({"sub": username, "exp": expiration}, SECRET_KEY, algorithm="HS256")
        return {"access_token": token}
    raise HTTPException(status_code=401, detail="Invalid username or password")

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
