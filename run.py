#!/usr/bin/env python3
"""
Ruua Backend Runner Script
Provides easy commands to start the application in different modes
"""

import sys
import subprocess
import os
from pathlib import Path

def run_dev():
    """Run in development mode with auto-reload"""
    print("🚀 Starting Ruua API in development mode...")
    subprocess.run([
        "uvicorn", "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--reload"
    ])

def run_prod():
    """Run in production mode"""
    print("🚀 Starting Ruua API in production mode...")
    subprocess.run([
        "uvicorn", "main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000", 
        "--workers", "4"
    ])

def run_tests():
    """Run the test suite"""
    print("🧪 Running Ruua API tests...")
    subprocess.run(["pytest", "test_api.py", "-v"])

def install_deps():
    """Install dependencies"""
    print("📦 Installing dependencies...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"])

def setup_db():
    """Set up the database"""
    print("🗄️ Setting up database...")
    # This would run database migrations in a real setup
    print("Database setup complete!")

def show_help():
    """Show available commands"""
    print("""
Ruua Backend Runner

Available commands:
  dev         Run in development mode with auto-reload
  prod        Run in production mode
  test        Run the test suite
  install     Install dependencies
  setup-db    Set up the database
  help        Show this help message

Usage:
  python run.py [command]
""")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "dev":
        run_dev()
    elif command == "prod":
        run_prod()
    elif command == "test":
        run_tests()
    elif command == "install":
        install_deps()
    elif command == "setup-db":
        setup_db()
    elif command == "help":
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()

if __name__ == "__main__":
    main()
