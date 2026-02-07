#!/usr/bin/env python3
"""
Test script to verify that the signup functionality works correctly
"""
import sys
import os

# Add the backend directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.auth_service import AuthService
from src.db.session import get_session
from src.models.user_model import UserCreate
from sqlmodel import Session

def test_signup():
    """Test the signup functionality"""
    print("Testing signup functionality...")
    
    # Create a test user
    user_data = UserCreate(
        email="testuser2@example.com",
        password="securepassword123",
        username="testuser2"
    )
    
    # Create a session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Create an instance of AuthService
        auth_service = AuthService(db=session)
        
        # Attempt to register the user
        user = auth_service.register_user(user_data)
        
        if user:
            print(f"✓ Successfully registered user: {user.email}")
            print(f"  - User ID: {user.id}")
            print(f"  - Username: {user.username}")
            print(f"  - Email: {user.email}")
            print(f"  - Created at: {user.created_at}")
            
            # Verify the user was saved to the database
            from src.models.user_model import User
            retrieved_user = session.get(User, user.id)
            if retrieved_user:
                print(f"✓ User successfully saved to database")
            else:
                print(f"✗ User was not saved to database")
                
        else:
            print(f"✗ Failed to register user")
            
    except Exception as e:
        print(f"✗ Error during signup: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the session
        session.close()

if __name__ == "__main__":
    test_signup()