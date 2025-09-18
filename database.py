from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
from sqlalchemy import text
import logging

# Create database engine
# Configure engine with pool and timezone options similar to Sequelize setup
engine = create_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=1800,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test connection and provide better error handling
def test_connection() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print(
            f"DB connection successful on HOST {settings.db_host}:{settings.db_port} "
            f"DB: {settings.profile_db}"
        )
    except Exception as exc:
        print("DB connection failed:")
        print(f"Error: {getattr(exc, 'orig', exc)}")
        print(f"Database: {settings.profile_db}")
        print(f"Host: {settings.db_host}")
        print(f"Port: {settings.db_port}")
        print(f"User: {settings.db_user}")
        print(f"Password: {'***SET***' if settings.db_pass else '***NOT SET***'}")
