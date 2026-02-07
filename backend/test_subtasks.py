#!/usr/bin/env python3
"""
Test script to verify the new subtask functionality
"""
import sys
import os

# Add the backend directory to the path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

from src.db.session import get_session
from src.models.user_model import User
from src.models.todo import Todo
from src.models.subtask import Subtask
from sqlmodel import Session
import uuid

def test_subtask_functionality():
    """Test the new subtask functionality"""
    print("Testing subtask functionality...")
    
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
                email="test@example.com",
                username="testuser",
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
        
        # Get the first todo for this user
        todo = session.query(Todo).filter(Todo.user_id == user.id).first()
        
        if not todo:
            print("No todos found for user, creating a test todo...")
            # Create a test todo
            test_todo = Todo(
                title="Test Todo",
                description="This is a test todo",
                user_id=user.id
            )
            session.add(test_todo)
            session.commit()
            session.refresh(test_todo)
            todo = test_todo
            print(f"Created test todo: {todo.title}")
        
        print(f"Using todo: {todo.title}")
        
        # Create a subtask for this todo
        print("Creating a subtask...")
        subtask = Subtask(
            title="Complete the subtask",
            is_completed=False,
            todo_id=todo.id
        )
        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        
        print(f"Created subtask: {subtask.title}, ID: {subtask.id}")
        
        # Query the todo with its subtasks using SQLModel's exec method
        from sqlalchemy.orm import selectinload
        from sqlmodel import select
        stmt = select(Todo).options(selectinload(Todo.subtasks)).where(Todo.id == todo.id)
        todo_with_subtasks = session.exec(stmt).one()
        
        print(f"\nTodo: {todo_with_subtasks.title}")
        print(f"Number of subtasks: {len(todo_with_subtasks.subtasks)}")
        
        for idx, subtask in enumerate(todo_with_subtasks.subtasks):
            print(f"  Subtask {idx+1}: {subtask.title} - Completed: {subtask.is_completed}")
        
        # Update the subtask to mark as completed
        print("\nUpdating subtask to mark as completed...")
        subtask.is_completed = True
        session.add(subtask)
        session.commit()
        
        # Query again to see the updated status
        stmt = select(Todo).options(selectinload(Todo.subtasks)).where(Todo.id == todo.id)
        todo_with_subtasks = session.exec(stmt).one()
        
        print(f"After update - Number of subtasks: {len(todo_with_subtasks.subtasks)}")
        for idx, subtask in enumerate(todo_with_subtasks.subtasks):
            print(f"  Subtask {idx+1}: {subtask.title} - Completed: {subtask.is_completed}")
        
        print("\n✓ Subtask functionality test completed successfully!")
        
    except Exception as e:
        print(f"✗ Error testing subtask functionality: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        # Close the session
        session.close()

if __name__ == "__main__":
    test_subtask_functionality()