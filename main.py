from fastapi import FastAPI, Depends, HTTPException, status, Request as FastAPIRequest
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import jwt
from dotenv import load_dotenv

from database import get_db, engine, Base, test_connection
from models import Request as DBRequest, Client, Admin
from routers import auth, requests, admin, storage
from config import settings

# Load environment variables
load_dotenv()

# Test DB connection and create tables
test_connection()
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Synthetic Data Generation Service",
    description="A service for generating synthetic datasets based on client requests",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Role-based access control middleware
@app.middleware("http")
async def role_based_access_control(request: FastAPIRequest, call_next):
    if (request.url.path.startswith("/api/") or 
        request.url.path.startswith("/static/") or 
        request.url.path.startswith("/docs") or
        request.url.path.startswith("/redoc") or
        request.url.path == "/login" or
        request.url.path == "/health" or
        request.url.path == "/"):
        response = await call_next(request)
        return response
    
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    if not token:
        return RedirectResponse(url="/login")
    
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_role = payload.get("role")
        if request.url.path.startswith("/admin/") and user_role != "admin":
            return RedirectResponse(url="/client/requests")
        elif request.url.path.startswith("/client/") and user_role != "client":
            return RedirectResponse(url="/admin/requests")
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login")
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/login")
    
    response = await call_next(request)
    return response

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(requests.router, prefix="/api/v1/request", tags=["requests"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(storage.router, prefix="/api/v1/storage", tags=["storage"])

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/api")
async def api_root():
    return {"message": "Synthetic Data Generation Service API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Frontend routes
@app.get("/", response_class=HTMLResponse)
async def root_page(request: FastAPIRequest):
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: FastAPIRequest):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/client/request", response_class=HTMLResponse)
async def client_request_page(request: FastAPIRequest):
    return templates.TemplateResponse("client_request.html", {"request": request})

@app.get("/client/requests", response_class=HTMLResponse)
async def client_requests_page(request: FastAPIRequest):
    return templates.TemplateResponse("client_requests.html", {"request": request})

@app.get("/admin/requests", response_class=HTMLResponse)
async def admin_requests_page(request: FastAPIRequest):
    return templates.TemplateResponse("admin_requests.html", {"request": request})

# ---- Main entrypoint for Render ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Use Render's PORT or fallback to 8000
    print(f"🚀 Starting Synthetic Data Generation Service on port {port}")
    print(f"🌐 API Documentation: http://localhost:{port}/docs")

    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")
