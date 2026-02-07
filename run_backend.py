#!/usr/bin/env python3
"""
Script to initialize the database and start the FastAPI server
"""
import subprocess
import sys
import os
from pathlib import Path


def run_database_init():
    """Run the database initialization script"""
    print("Initializing database...")
    try:
        result = subprocess.run([sys.executable, "init_db.py"], cwd=".", capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Database initialization failed: {result.stderr}")
            return False
        print("Database initialized successfully!")
        return True
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        return False


def start_server():
    """Start the FastAPI server"""
    print("Starting server...")
    try:
        subprocess.run([
            "uvicorn",
            "src.main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload",
            "--log-level", "warning"  # Reduce logging level to warning to minimize noise
        ], cwd=".")
    except KeyboardInterrupt:
        print("\nServer stopped.")


if __name__ == "__main__":
    # Change to the backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Initialize database
    if not run_database_init():
        print("Failed to initialize database. Exiting...")
        sys.exit(1)
    
    # Start the server
    start_server()