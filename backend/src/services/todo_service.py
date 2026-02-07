from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from ..models.todo import Todo, TodoBase
from ..models.subtask import Subtask
from .base_service import BaseService
from ..utils.cache import cache_manager, get_cache_key, get_user_cache_key


class TodoService:
    """
    Service class for handling todo-related operations
    """

    def __init__(self):
        self.base_service = BaseService(Todo)

    def create_todo(self, db: Session, todo_data: dict, user_id: str):
        """
        Create a new todo for a user
        """
        user_uuid = UUID(user_id)
        todo_data['user_id'] = user_uuid
        todo = self.base_service.create(db, todo_data)

        # Refresh the todo to load relationships
        db.refresh(todo)
        return todo

    def get_todo_by_id(self, db: Session, todo_id: str, user_id: str):
        """
        Get a specific todo for a user by ID with caching
        """
        # Try to get from cache first
        cache_key = get_cache_key("todo", todo_id, user_id)
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Convert string IDs to UUIDs
        todo_uuid = UUID(todo_id)
        user_uuid = UUID(user_id)

        statement = select(Todo).options(selectinload(Todo.subtasks)).where(Todo.id == todo_uuid, Todo.user_id == user_uuid)
        result = db.execute(statement)
        todo = result.scalar_one_or_none()

        # Cache the result if found
        if todo:
            cache_manager.set(cache_key, todo, expiration=600)  # Cache for 10 minutes

        return todo

    def get_todos(self, db: Session, user_id: str):
        """
        Get all todos for a user with caching
        """
        # Try to get from cache first
        cache_key = get_user_cache_key("todos", user_id)
        cached_result = cache_manager.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Convert string ID to UUID
        user_uuid = UUID(user_id)

        statement = select(Todo).options(selectinload(Todo.subtasks)).where(Todo.user_id == user_uuid)
        result = db.execute(statement)
        todos = result.scalars().all()  # Use scalars() to get model instances

        # Cache the result
        cache_manager.set(cache_key, todos, expiration=300)  # Cache for 5 minutes

        return todos

    def update_todo(self, db: Session, todo_id: str, todo_update_data: dict, user_id: str):
        """
        Update a specific todo for a user and invalidate cache
        """
        # Convert string IDs to UUIDs
        todo_uuid = UUID(todo_id)
        user_uuid = UUID(user_id)

        # Get the existing todo
        statement = select(Todo).where(Todo.id == todo_uuid, Todo.user_id == user_uuid)
        result = db.execute(statement)
        todo = result.scalar_one_or_none()

        if not todo:
            return None

        # Update the todo with provided data
        for field, value in todo_update_data.items():
            if hasattr(todo, field) and value is not None:
                setattr(todo, field, value)

        # Update timestamps
        todo.updated_at = func.now()

        db.add(todo)
        db.commit()
        db.refresh(todo)

        # Invalidate cache for this specific todo and the user's todo list
        cache_manager.delete(get_cache_key("todo", todo_id, user_id))
        cache_manager.delete(get_user_cache_key("todos", user_id))

        return todo

    def delete_todo(self, db: Session, todo_id: str, user_id: str):
        """
        Delete a specific todo for a user and invalidate cache
        """
        # Convert string IDs to UUIDs
        todo_uuid = UUID(todo_id)
        user_uuid = UUID(user_id)

        # Get the existing todo
        statement = select(Todo).where(Todo.id == todo_uuid, Todo.user_id == user_uuid)
        result = db.execute(statement)
        todo = result.scalar_one_or_none()

        if not todo:
            return False

        db.delete(todo)
        db.commit()

        # Invalidate cache for this specific todo and the user's todo list
        cache_manager.delete(get_cache_key("todo", todo_id, user_id))
        cache_manager.delete(get_user_cache_key("todos", user_id))

        return True

    def mark_complete(self, db: Session, todo_id: str, user_id: str):
        """
        Mark a todo as complete and invalidate cache
        """
        # Convert string IDs to UUIDs
        todo_uuid = UUID(todo_id)
        user_uuid = UUID(user_id)

        # Get the existing todo
        statement = select(Todo).where(Todo.id == todo_uuid, Todo.user_id == user_uuid)
        result = db.execute(statement)
        todo = result.scalar_one_or_none()

        if not todo:
            return None

        todo.status = "completed"
        todo.completed_at = func.now()
        todo.updated_at = func.now()

        db.add(todo)
        db.commit()
        db.refresh(todo)

        # Invalidate cache for this specific todo and the user's todo list
        cache_manager.delete(get_cache_key("todo", todo_id, user_id))
        cache_manager.delete(get_user_cache_key("todos", user_id))

        return todo

    def bulk_mark_complete(self, db: Session, todo_ids: List[str], user_id: str):
        """
        Mark multiple todos as complete and invalidate cache
        """
        user_uuid = UUID(user_id)
        completed_count = 0

        for todo_id in todo_ids:
            try:
                todo_uuid = UUID(todo_id)
                # Get the existing todo
                statement = select(Todo).where(Todo.id == todo_uuid, Todo.user_id == user_uuid)
                result = db.execute(statement)
                todo = result.scalar_one_or_none()

                if todo:
                    todo.status = "completed"
                    todo.completed_at = func.now()
                    todo.updated_at = func.now()
                    db.add(todo)
                    completed_count += 1
            except ValueError:
                # Skip invalid UUIDs
                continue

        db.commit()

        # Invalidate the user's todo list cache
        cache_manager.delete(get_user_cache_key("todos", user_id))

        return completed_count