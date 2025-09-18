#!/usr/bin/env python3
"""
Test script to verify Synthetic Data Generation Service installation
"""

import sys
import os
import importlib
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported."""
    print("🔍 Testing imports...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pandas',
        'numpy',
        'sklearn',
        'faker',
        'jose',
        'passlib',
        'pydantic',
        'jinja2'
    ]
    
    failed_imports = []
    
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All imports successful")
    return True

def test_project_structure():
    """Test if all required files exist."""
    print("\n🔍 Testing project structure...")
    
    required_files = [
        'main.py',
        'config.py',
        'database.py',
        'models.py',
        'schemas.py',
        'auth_utils.py',
        'synthetic_generator.py',
        'storage_manager.py',
        'requirements.txt',
        'README.md'
    ]
    
    required_dirs = [
        'routers',
        'templates',
        'static'
    ]
    
    missing_files = []
    missing_dirs = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"  ✅ {file}")
    
    for directory in required_dirs:
        if not os.path.isdir(directory):
            missing_dirs.append(directory)
        else:
            print(f"  ✅ {directory}/")
    
    if missing_files or missing_dirs:
        print(f"\n❌ Missing files: {missing_files}")
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Project structure is complete")
    return True

def test_database_creation():
    """Test if database can be created."""
    print("\n🔍 Testing database creation...")
    
    try:
        from database import engine, Base
        from models import Client, Admin, Request
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def test_synthetic_generator():
    """Test if synthetic data generator works."""
    print("\n🔍 Testing synthetic data generator...")
    
    try:
        from synthetic_generator import SyntheticDataGenerator
        from models import DataType, PrivacyLevel
        
        generator = SyntheticDataGenerator()
        
        # Test generating a small dataset
        test_file = generator.generate_dataset(
            data_type=DataType.HEALTH_RECORDS,
            size=10,
            privacy_level=PrivacyLevel.LOW,
            request_id=999
        )
        
        if os.path.exists(test_file):
            print("✅ Synthetic data generator works")
            # Clean up test file
            os.remove(test_file)
            os.rmdir(os.path.dirname(test_file))
            return True
        else:
            print("❌ Generated file not found")
            return False
            
    except Exception as e:
        print(f"❌ Synthetic data generator test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Synthetic Data Generation Service - Installation Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_project_structure,
        test_database_creation,
        test_synthetic_generator
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The service is ready to use.")
        print("\n📋 To start the service:")
        print("  python main.py")
        print("\n🌐 Then open: http://localhost:8000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
