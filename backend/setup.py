#!/usr/bin/env python3
"""
RAN Insight Pro Backend Setup Script
This script helps set up the backend environment and configuration
"""

import os
import sys
import secrets
import shutil
from pathlib import Path

def create_env_file():
    """Create .env file from env.example if it doesn't exist"""
    env_file = Path(".env")
    env_example = Path("env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if not env_example.exists():
        print("❌ env.example file not found")
        return
    
    # Copy env.example to .env
    shutil.copy(env_example, env_file)
    print("✅ Created .env file from env.example")
    
    # Generate a secure secret key
    secret_key = secrets.token_urlsafe(32)
    
    # Read the .env file and replace the secret key
    with open(env_file, 'r') as f:
        content = f.read()
    
    content = content.replace(
        "SECRET_KEY=your-secret-key-here-change-in-production",
        f"SECRET_KEY={secret_key}"
    )
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    print("✅ Generated secure SECRET_KEY")

def create_directories():
    """Create necessary directories"""
    directories = [
        "uploads",
        "reports", 
        "logs",
        "temp"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn", 
        "pandas",
        "numpy",
        "openai",
        "sqlalchemy",
        "python-dotenv",
        "structlog"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == "python-dotenv":
                import dotenv
            else:
                __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All required packages are installed")
        return True

def setup_database():
    """Initialize the database"""
    try:
        from app.db.session import create_tables
        create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Failed to create database tables: {e}")
        return False
    return True

def main():
    """Main setup function"""
    print("🚀 RAN Insight Pro Backend Setup")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Create .env file
    print("\n📝 Setting up environment configuration...")
    create_env_file()
    
    # Create directories
    print("\n📁 Creating directories...")
    create_directories()
    
    # Check dependencies
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        print("\n❌ Setup incomplete due to missing dependencies")
        sys.exit(1)
    
    # Setup database
    print("\n🗄️  Setting up database...")
    if not setup_database():
        print("\n❌ Setup incomplete due to database issues")
        sys.exit(1)
    
    print("\n✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Edit .env file with your configuration (especially OPENAI_API_KEY)")
    print("2. Run the server: python run.py")
    print("3. Access API docs: http://localhost:8000/docs")
    print("4. Check health: http://localhost:8000/health")

if __name__ == "__main__":
    main()
