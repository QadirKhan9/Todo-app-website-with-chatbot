from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List
from uuid import UUID
from ...models.todo import Todo
from ...models.todo_api_models import TodoCreate, TodoUpdate
from ...services.todo_service import TodoService
from ...utils.auth import get_current_user
from ...utils.database import get_session
from ...utils.responses import create_success_response, create_error_response
from ...utils.errors import ValidationError, NotFoundError

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=Todo)
async def create_todo(
    todo: TodoCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Create a new todo for the current user
    """
    try:
        # Convert the Pydantic model to a dict
        todo_data = todo.dict()
        
        # Create the todo using the service
        todo_service = TodoService()
        created_todo = todo_service.create_todo(db, todo_data, current_user.id)
        
        return created_todo
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating todo: {str(e)}"
        )


@router.get("/{todo_id}", response_model=Todo)
async def get_todo(
    todo_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get a specific todo by ID
    """
    try:
        todo_service = TodoService()
        todo = todo_service.get_todo(db, todo_id, current_user.id)
        
        if not todo:
            raise NotFoundError(f"Todo with ID {todo_id} not found")
        
        return todo
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving todo: {str(e)}"
        )


@router.get("/", response_model=List[Todo])
async def get_todos(
    skip: int = 0,
    limit: int = 100,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Get all todos for the current user
    """
    try:
        todo_service = TodoService()
        todos = todo_service.get_todos(db, current_user.id, skip=skip, limit=limit)
        
        return todos
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving todos: {str(e)}"
        )


@router.put("/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: UUID,
    todo_update: TodoUpdate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Update a specific todo
    """
    try:
        # Convert the Pydantic model to a dict
        update_data = todo_update.dict(exclude_unset=True)
        
        todo_service = TodoService()
        updated_todo = todo_service.update_todo(db, todo_id, update_data, current_user.id)
        
        if not updated_todo:
            raise NotFoundError(f"Todo with ID {todo_id} not found")
        
        return updated_todo
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating todo: {str(e)}"
        )


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Delete a specific todo
    """
    try:
        todo_service = TodoService()
        deleted_todo = todo_service.delete_todo(db, todo_id, current_user.id)
        
        if not deleted_todo:
            raise NotFoundError(f"Todo with ID {todo_id} not found")
        
        return {"message": f"Todo {deleted_todo.title} deleted successfully"}
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting todo: {str(e)}"
        )