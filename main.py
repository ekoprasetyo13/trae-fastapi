from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import models, schemas, auth, database
from database import engine, get_db
from typing import List

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def _otel_traces_endpoint() -> str:
    traces_endpoint = os.getenv("OTEL_EXPORTER_OTLP_TRACES_ENDPOINT")
    if traces_endpoint:
        return traces_endpoint

    base_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if base_endpoint:
        return f"{base_endpoint.rstrip('/')}/v1/traces"

    return "http://172.15.1.100:4318/v1/traces"


def setup_otel():
    if os.getenv("OTEL_DISABLED", "").lower() in {"1", "true", "yes"}:
        return

    service_name = os.getenv("OTEL_SERVICE_NAME", "trae-fastapi")
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter(endpoint=_otel_traces_endpoint())
    provider.add_span_processor(BatchSpanProcessor(exporter))

# Create database tables
models.Base.metadata.create_all(bind=engine)

setup_otel()

app = FastAPI(
    title="Sample API App",
    description="A sample FastAPI application with SQLite, SQLAlchemy, and Authentication",
    version="1.0.0",
    docs_url="/docs-api", # Custom swagger path
    redoc_url=None
)

FastAPIInstrumentor.instrument_app(app)

# Helper function for standard response
def standard_response(code: int, status: str, message: str, data: any = None):
    return JSONResponse(
        status_code=code,
        content={
            "code": code,
            "status": status,
            "message": message,
            "data": data
        }
    )

# Authentication Endpoints
@app.post("/register", response_model=schemas.StandardResponse, tags=["Auth"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        return standard_response(400, "Bad Request", "Username already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return standard_response(201, "Created", "User registered successfully", {"username": new_user.username})

@app.post("/token", tags=["Auth"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# 10 Sample Public GET APIs (no-auth)
@app.get("/public/1", tags=["Public APIs"])
def public_api_1():
    return standard_response(200, "OK", "Public API 1 called successfully", {"info": "Welcome to Public API 1"})

@app.get("/public/2", tags=["Public APIs"])
def public_api_2():
    return standard_response(200, "OK", "Public API 2 called successfully", {"info": "Welcome to Public API 2"})

@app.get("/public/3", tags=["Public APIs"])
def public_api_3():
    return standard_response(200, "OK", "Public API 3 called successfully", {"info": "Welcome to Public API 3"})

@app.get("/public/4", tags=["Public APIs"])
def public_api_4():
    return standard_response(200, "OK", "Public API 4 called successfully", {"info": "Welcome to Public API 4"})

@app.get("/public/5", tags=["Public APIs"])
def public_api_5():
    return standard_response(200, "OK", "Public API 5 called successfully", {"info": "Welcome to Public API 5"})

@app.get("/public/6", tags=["Public APIs"])
def public_api_6():
    return standard_response(200, "OK", "Public API 6 called successfully", {"info": "Welcome to Public API 6"})

@app.get("/public/7", tags=["Public APIs"])
def public_api_7():
    return standard_response(200, "OK", "Public API 7 called successfully", {"info": "Welcome to Public API 7"})

@app.get("/public/8", tags=["Public APIs"])
def public_api_8():
    return standard_response(200, "OK", "Public API 8 called successfully", {"info": "Welcome to Public API 8"})

@app.get("/public/9", tags=["Public APIs"])
def public_api_9():
    return standard_response(200, "OK", "Public API 9 called successfully", {"info": "Welcome to Public API 9"})

@app.get("/public/10", tags=["Public APIs"])
def public_api_10():
    return standard_response(200, "OK", "Public API 10 called successfully", {"info": "Welcome to Public API 10"})

# 5 Sample Private GET APIs (with auth)
@app.get("/private/1", tags=["Private APIs"])
def private_api_1(current_user: models.User = Depends(auth.get_current_user)):
    return standard_response(200, "OK", f"Hello {current_user.username}, this is Private API 1", {"secret": "private-data-1"})

@app.get("/private/2", tags=["Private APIs"])
def private_api_2(current_user: models.User = Depends(auth.get_current_user)):
    return standard_response(200, "OK", f"Hello {current_user.username}, this is Private API 2", {"secret": "private-data-2"})

@app.get("/private/3", tags=["Private APIs"])
def private_api_3(current_user: models.User = Depends(auth.get_current_user)):
    return standard_response(200, "OK", f"Hello {current_user.username}, this is Private API 3", {"secret": "private-data-3"})

@app.get("/private/4", tags=["Private APIs"])
def private_api_4(current_user: models.User = Depends(auth.get_current_user)):
    return standard_response(200, "OK", f"Hello {current_user.username}, this is Private API 4", {"secret": "private-data-4"})

@app.get("/private/5", tags=["Private APIs"])
def private_api_5(current_user: models.User = Depends(auth.get_current_user)):
    return standard_response(200, "OK", f"Hello {current_user.username}, this is Private API 5", {"secret": "private-data-5"})

# Sample Error APIs
@app.get("/error/400", tags=["Error Samples"])
def error_400():
    return standard_response(400, "Bad Request", "This is a sample 400 Bad Request error")

@app.get("/error/401", tags=["Error Samples"])
def error_401():
    return standard_response(401, "Unauthorized", "This is a sample 401 Unauthorized error")

@app.get("/error/403", tags=["Error Samples"])
def error_403():
    return standard_response(403, "Forbidden", "This is a sample 403 Forbidden error")

@app.get("/error/404", tags=["Error Samples"])
def error_404():
    return standard_response(404, "Not Found", "This is a sample 404 Not Found error")

@app.get("/error/405", tags=["Error Samples"])
def error_405():
    return standard_response(405, "Method Not Allowed", "This is a sample 405 Method Not Allowed error")

@app.get("/error/408", tags=["Error Samples"])
def error_408():
    return standard_response(408, "Request Timeout", "This is a sample 408 Request Timeout error")

@app.get("/error/500", tags=["Error Samples"])
def error_500():
    return standard_response(500, "Internal Server Error", "This is a sample 500 Internal Server Error")

@app.get("/error/503", tags=["Error Samples"])
def error_503():
    return standard_response(503, "Service Unavailable", "This is a sample 503 Service Unavailable error")

@app.get("/error/504", tags=["Error Samples"])
def error_504():
    return standard_response(504, "Gateway Timeout", "This is a sample 504 Gateway Timeout error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
