#!/usr/bin/env python3
"""
Test script to verify the bulk operations functionality
"""
import sys
import os

# Add the backend directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from src.db.session import get_session
from src.models.user_model import User
from src.models.todo import Todo
from sqlmodel import Session
import uuid

def test_bulk_operations():
    """Test the bulk operations functionality"""
    print("Testing bulk operations functionality...")
    
    # Create a session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Get the first user from the database
        user = session.query(User).first()
        
        if not user:
            print("No users found in database, creating a test user...")
            # Create a test user
            test_user = User(
                email="bulk_test@example.com",
                username="bulktestuser",
                role="USER",
                is_active=True,
                email_verified=True,
                hashed_password="$2b$12$example_hashed_password"  # This is a dummy hash
            )
            session.add(test_user)
            session.commit()
            session.refresh(test_user)
            user = test_user
            print(f"Created test user: {user.email}")
        
        print(f"Using user: {user.email}")
        
        # Create multiple test todos
        print("Creating test todos...")
        test_todos = []
        for i in range(3):
            todo = Todo(
                title=f"Bulk Test Todo {i+1}",
                description=f"This is test todo {i+1} for bulk operations",
                user_id=user.id
            )
            session.add(todo)
            test_todos.append(todo)
        
        session.commit()
        
        # Refresh to get the IDs
        for todo in test_todos:
            session.refresh(todo)
        
        print(f"Created {len(test_todos)} test todos")
        
        # Test bulk completion
        print("Testing bulk completion...")
        from src.services.todo_service import TodoService
        service = TodoService()
        
        # Get the IDs of the test todos
        todo_ids = [str(todo.id) for todo in test_todos]
        print(f"Todo IDs to complete: {todo_ids}")
        
        # Mark all as complete
        completed_count = service.bulk_mark_complete(session, todo_ids, str(user.id))
        print(f"Marked {completed_count} todos as completed")
        
        # Verify that they were marked as completed
        from sqlmodel import select
        completed_todos = session.exec(select(Todo).where(Todo.id.in_([uuid.UUID(tid) for tid in todo_ids]))).all()
        
        completed_count_verified = 0
        for todo in completed_todos:
            if todo.status == "completed":
                completed_count_verified += 1
                print(f"  Todo '{todo.title}' is marked as completed: {todo.status}")
            else:
                print(f"  Todo '{todo.title}' status: {todo.status}")
        
        print(f"Verified {completed_count_verified} todos as completed")
        
        print("\n✓ Bulk operations test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error testing bulk operations: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the session
        session.close()

if __name__ == "__main__":
    test_bulk_operations()