"""Todo API endpoints"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from ..database import get_db
from ..models.user_model import User
from ..models.todo import Todo
from ..models.subtask import Subtask, SubtaskCreate, SubtaskUpdate
from ..schemas.todo import TodoCreate, TodoUpdate, TodoResponse, SubtaskResponse
from ..dependencies.auth import get_current_user
from ..services.todo_service import TodoService


# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/todos", tags=["todos"])


def get_todo_service() -> TodoService:
    """
    Dependency to get the todo service
    """
    return TodoService()


@router.post("/", response_model=TodoResponse, status_code=201)
def create_todo(
    todo_data: TodoCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Create a new todo for the current user
    """
    try:
        # Prepare todo data from the request
        todo_dict = todo_data.model_dump()
        todo = todo_service.create_todo(db, todo_dict, str(current_user.id))
        # Get subtasks for this todo
        subtasks = []
        if hasattr(todo, 'subtasks') and todo.subtasks:
            for subtask in todo.subtasks:
                subtasks.append(SubtaskResponse(
                    id=str(subtask.id),
                    todo_id=str(subtask.todo_id),
                    title=subtask.title,
                    is_completed=subtask.is_completed,
                    created_at=subtask.created_at or datetime.utcnow(),
                    updated_at=subtask.updated_at or datetime.utcnow(),
                    completed_at=subtask.completed_at
                ))

        return TodoResponse(
            id=str(todo.id),
            user_id=str(todo.user_id),
            title=todo.title,
            description=todo.description,
            is_completed=(todo.status == "completed"),  # Map status to is_completed
            created_at=todo.created_at or datetime.utcnow(),
            updated_at=todo.updated_at or datetime.utcnow(),
            subtasks=subtasks
        )
    except HTTPException as e:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the todo"
        )


@router.get("/", response_model=List[TodoResponse])
def get_todos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Get all todos for the current user
    """
    try:
        todos = todo_service.get_todos(db, str(current_user.id))
        return [
            TodoResponse(
                id=str(todo.id),
                user_id=str(todo.user_id),
                title=todo.title,
                description=todo.description,
                is_completed=(todo.status == "completed"),  # Map status to is_completed
                created_at=todo.created_at or datetime.utcnow(),
                updated_at=todo.updated_at or datetime.utcnow(),
                subtasks=[]  # Initialize with empty subtasks; populate if needed
            ) for todo in todos
        ]
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_todos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving todos"
        )


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Get a specific todo by ID for the current user
    """
    try:
        # Validate UUID format
        try:
            UUID(todo_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid todo ID format"
            )

        todo = todo_service.get_todo_by_id(db, todo_id, str(current_user.id))
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found or not owned by user"
            )

        # Get subtasks for this todo
        subtasks = []
        if hasattr(todo, 'subtasks') and todo.subtasks:
            for subtask in todo.subtasks:
                subtasks.append(SubtaskResponse(
                    id=str(subtask.id),
                    todo_id=str(subtask.todo_id),
                    title=subtask.title,
                    is_completed=subtask.is_completed,
                    created_at=subtask.created_at or datetime.utcnow(),
                    updated_at=subtask.updated_at or datetime.utcnow(),
                    completed_at=subtask.completed_at
                ))

        return TodoResponse(
            id=str(todo.id),
            user_id=str(todo.user_id),
            title=todo.title,
            description=todo.description,
            is_completed=(todo.status == "completed"),  # Map status to is_completed
            created_at=todo.created_at or datetime.utcnow(),
            updated_at=todo.updated_at or datetime.utcnow(),
            subtasks=subtasks
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving the todo"
        )


@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(
    todo_id: str,
    todo_update: TodoUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Update a specific todo by ID for the current user
    """
    try:
        # Validate UUID format
        try:
            UUID(todo_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid todo ID format"
            )

        # Convert the update data to a dictionary
        update_data = {}
        for field, value in todo_update.model_dump().items():
            if value is not None:
                # Map is_completed to status for internal representation
                if field == 'is_completed':
                    update_data['status'] = 'completed' if value else 'pending'
                else:
                    update_data[field] = value

        updated_todo = todo_service.update_todo(db, todo_id, update_data, str(current_user.id))
        if not updated_todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found or not owned by user"
            )

        return TodoResponse(
            id=str(updated_todo.id),
            user_id=str(updated_todo.user_id),
            title=updated_todo.title,
            description=updated_todo.description,
            is_completed=(updated_todo.status == "completed"),  # Map status to is_completed
            created_at=updated_todo.created_at or datetime.utcnow(),
            updated_at=updated_todo.updated_at or datetime.utcnow()
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the todo"
        )


@router.delete("/{todo_id}")
def delete_todo(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Delete a specific todo by ID for the current user
    """
    try:
        # Validate UUID format
        try:
            UUID(todo_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid todo ID format"
            )

        success = todo_service.delete_todo(db, todo_id, str(current_user.id))
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found or not owned by user"
            )

        return {"message": "Todo deleted successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_todo: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the todo"
        )


# Bulk operations
from pydantic import BaseModel

class BulkUpdateRequest(BaseModel):
    todo_ids: List[str]
    action: str  # "complete" or "delete"


@router.post("/bulk-update")
def bulk_update_todos(
    bulk_request: BulkUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Perform bulk operations on multiple todos (mark as complete, delete, etc.)
    """
    try:
        # Validate all todo IDs
        for todo_id in bulk_request.todo_ids:
            try:
                UUID(todo_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid todo ID format: {todo_id}"
                )

        if bulk_request.action == "complete":
            # Mark multiple todos as complete using the service method
            updated_count = todo_service.bulk_mark_complete(db, bulk_request.todo_ids, str(current_user.id))
            return {"message": f"Successfully marked {updated_count} todos as completed"}

        elif bulk_request.action == "delete":
            # Delete multiple todos
            deleted_count = 0
            for todo_id in bulk_request.todo_ids:
                success = todo_service.delete_todo(db, todo_id, str(current_user.id))
                if success:
                    deleted_count += 1

            return {"message": f"Successfully deleted {deleted_count} todos"}

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Supported actions: 'complete', 'delete'"
            )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in bulk_update_todos: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while performing bulk operation"
        )


# Subtask endpoints
@router.post("/{todo_id}/subtasks", response_model=SubtaskResponse, status_code=201)
def create_subtask(
    todo_id: str,
    subtask_data: SubtaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Create a new subtask for a specific todo
    """
    try:
        # Validate UUID format
        try:
            UUID(todo_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid todo ID format"
            )

        # Verify that the todo belongs to the current user
        todo = todo_service.get_todo_by_id(db, todo_id, str(current_user.id))
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found or not owned by user"
            )

        # Create the subtask
        subtask = Subtask(
            title=subtask_data.title,
            is_completed=subtask_data.is_completed,
            todo_id=UUID(todo_id)
        )

        db.add(subtask)
        db.commit()
        db.refresh(subtask)

        return SubtaskResponse(
            id=str(subtask.id),
            todo_id=str(subtask.todo_id),
            title=subtask.title,
            is_completed=subtask.is_completed,
            created_at=subtask.created_at or datetime.utcnow(),
            updated_at=subtask.updated_at or datetime.utcnow(),
            completed_at=subtask.completed_at
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in create_subtask: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the subtask"
        )


@router.get("/{todo_id}/subtasks", response_model=List[SubtaskResponse])
def get_subtasks(
    todo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    todo_service: TodoService = Depends(get_todo_service)
):
    """
    Get all subtasks for a specific todo
    """
    try:
        # Validate UUID format
        try:
            UUID(todo_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid todo ID format"
            )

        # Verify that the todo belongs to the current user
        todo = todo_service.get_todo_by_id(db, todo_id, str(current_user.id))
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Todo not found or not owned by user"
            )

        # Get subtasks for this todo
        from sqlmodel import select
        statement = select(Subtask).where(Subtask.todo_id == UUID(todo_id))
        result = db.execute(statement)
        subtasks = result.scalars().all()

        return [
            SubtaskResponse(
                id=str(subtask.id),
                todo_id=str(subtask.todo_id),
                title=subtask.title,
                is_completed=subtask.is_completed,
                created_at=subtask.created_at or datetime.utcnow(),
                updated_at=subtask.updated_at or datetime.utcnow(),
                completed_at=subtask.completed_at
            ) for subtask in subtasks
        ]
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_subtasks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while retrieving subtasks"
        )


@router.put("/{todo_id}/subtasks/{subtask_id}", response_model=SubtaskResponse)
def update_subtask(
    todo_id: str,
    subtask_id: str,
    subtask_update: SubtaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a specific subtask for a todo
    """
    try:
        # Validate UUID formats
        try:
            UUID(todo_id)
            UUID(subtask_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )

        # Get the subtask
        from sqlmodel import select
        statement = select(Subtask).where(Subtask.id == UUID(subtask_id), Subtask.todo_id == UUID(todo_id))
        result = db.execute(statement)
        subtask = result.scalar_one_or_none()

        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtask not found"
            )

        # Update the subtask with provided data
        for field, value in subtask_update.model_dump(exclude_unset=True).items():
            if hasattr(subtask, field) and value is not None:
                setattr(subtask, field, value)

        # Update timestamp
        subtask.updated_at = datetime.utcnow()

        # If marking as completed, set completed_at
        if subtask.is_completed and not subtask.completed_at:
            subtask.completed_at = datetime.utcnow()
        elif not subtask.is_completed:
            subtask.completed_at = None

        db.add(subtask)
        db.commit()
        db.refresh(subtask)

        return SubtaskResponse(
            id=str(subtask.id),
            todo_id=str(subtask.todo_id),
            title=subtask.title,
            is_completed=subtask.is_completed,
            created_at=subtask.created_at or datetime.utcnow(),
            updated_at=subtask.updated_at or datetime.utcnow(),
            completed_at=subtask.completed_at
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in update_subtask: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the subtask"
        )


@router.delete("/{todo_id}/subtasks/{subtask_id}")
def delete_subtask(
    todo_id: str,
    subtask_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific subtask from a todo
    """
    try:
        # Validate UUID formats
        try:
            UUID(todo_id)
            UUID(subtask_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ID format"
            )

        # Get the subtask
        from sqlmodel import select
        statement = select(Subtask).where(Subtask.id == UUID(subtask_id), Subtask.todo_id == UUID(todo_id))
        result = db.execute(statement)
        subtask = result.scalar_one_or_none()

        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subtask not found"
            )

        db.delete(subtask)
        db.commit()

        return {"message": "Subtask deleted successfully"}
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in delete_subtask: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the subtask"
        )