from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "")
    db_user: str = os.getenv("DB_USER", "root")
    db_pass: str = os.getenv("DB_PASS", "password")
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    profile_db: str = os.getenv("PROFILE_DB", "synthetic_data")
    
    # JWT
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Storage
    storage_type: str = "local"  # local, s3, gcs, azure
    local_storage_path: str = "./storage"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    s3_bucket_name: Optional[str] = None
    
    # Email (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()

# Derive SQLAlchemy URL if not explicitly set
if not settings.database_url:
    # Default to MariaDB/MySQL via PyMySQL
    settings.database_url = (
        f"mysql+pymysql://{settings.db_user}:{settings.db_pass}"
        f"@{settings.db_host}:{settings.db_port}/{settings.profile_db}?charset=utf8mb4"
    )
