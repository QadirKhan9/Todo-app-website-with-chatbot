#!/usr/bin/env python3
"""
Test script to check how UUIDs are stored in the database
"""
import sys
import os

# Add the backend directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from src.db.session import get_session
from src.models.user_model import User
from sqlmodel import Session
import uuid

def check_uuid_format():
    """Check how UUIDs are stored in the database"""
    print("Checking UUID format in database...")
    
    # Create a session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Get the first user from the database
        user = session.query(User).first()
        
        if user:
            print(f"User ID from database: {user.id}")
            print(f"Type of user ID: {type(user.id)}")
            print(f"String representation: {str(user.id)}")
            
            # Test if it's a valid UUID
            try:
                parsed_uuid = uuid.UUID(str(user.id))
                print(f"Parsed UUID: {parsed_uuid}")
                print(f"UUID hex: {parsed_uuid.hex}")
            except ValueError as e:
                print(f"Error parsing UUID: {e}")
        else:
            print("No users found in database")
            
    except Exception as e:
        print(f"Error checking UUID format: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the session
        session.close()

if __name__ == "__main__":
    check_uuid_format()