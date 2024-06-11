from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from app.api import auth, user, student
from app.database import Base
from app.utils import engine
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Include the routers
app.include_router(auth.router, tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(student.router, prefix="/students", tags=["Students"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

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

    # Define security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/token",
                    "scopes": {}
                }
            }
        },
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer"
        }
    }

    # Apply security to routes
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            if path.startswith("/users") or path.startswith("/students") or path == "/api/example":
                openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]

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
