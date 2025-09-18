# main.py
import os
import logging
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Request as FastAPIRequest
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

from database import get_db, engine, Base, test_connection
from models import Request as DBRequest, Client, Admin
from routers import auth, requests, admin, storage
from config import settings

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test DB connection and create tables
try:
    test_connection()
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database connected and tables created")
except Exception as e:
    logger.error(f"❌ Database initialization failed: {e}")

# Initialize FastAPI
app = FastAPI(
    title="Synthetic Data Generation Service",
    description="Generate synthetic datasets based on client requests",
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
    # Public paths
    public_paths = ["/api/", "/static/", "/docs", "/redoc", "/login", "/health", "/"]
    if any(request.url.path.startswith(path) for path in public_paths):
        return await call_next(request)

    # Get JWT token
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        return RedirectResponse(url="/login")

    # Decode token and enforce role
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

    return await call_next(request)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(requests.router, prefix="/api/v1/request", tags=["requests"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(storage.router, prefix="/api/v1/storage", tags=["storage"])

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Basic API endpoints
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

# ---- Startup for local or Render ----
def start():
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"🚀 Starting Synthetic Data Generation Service on port {port}")
    logger.info(f"🌐 API Documentation: http://localhost:{port}/docs")
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    start()
