#!/usr/bin/env python3
"""
Startup script for Synthetic Data Generation Service
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required packages are installed."""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pandas
        import numpy
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ['storage', 'storage/requests', 'static', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist."""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            import shutil
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your configuration")
        else:
            # Create basic .env file
            with open('.env', 'w') as f:
                f.write("""# Database
DATABASE_URL=sqlite:///./synthetic_data.db

# JWT Secret Key (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Storage Configuration
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage
""")
            print("✅ Created basic .env file")
    else:
        print("✅ .env file already exists")

def main():
    """Main startup function."""
    print("🚀 Starting Synthetic Data Generation Service Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your configuration")
    print("2. Run: python main.py")
    print("3. Open: http://localhost:8000")
    print("4. Register as a client or admin")
    print("\n📚 For more information, see README.md")

if __name__ == "__main__":
    main()
