from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session
from typing import List, Optional
from ..database.session import get_session
from src.models.task import Task, TaskCreate, TaskRead, TaskUpdate
from src.services import task_service
from src.auth import get_current_user, TokenData
from src.utils.exceptions import ResourceNotFoundError


router = APIRouter()


@router.get("/{user_id}/tasks", response_model=List[TaskRead])
def get_tasks(
    user_id: str,
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    priority: Optional[str] = Query(None, description="Filter by priority (low, medium, high)"),
    limit: int = Query(20, ge=1, le=100, description="Number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip"),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access these tasks"
        )
    
    tasks = task_service.get_tasks_by_user(
        user_id=user_id,
        db_session=db,
        completed=completed,
        priority=priority,
        limit=limit,
        offset=offset
    )
    
    return tasks


@router.post("/{user_id}/tasks", response_model=TaskRead)
def create_task(
    user_id: str,
    task: TaskCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create tasks for this user"
        )
    
    # Ensure the task is being created for the authenticated user
    task.user_id = user_id
    
    try:
        created_task = task_service.create_task(task, db)
        return created_task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def get_task(
    user_id: str,
    task_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task"
        )
    
    try:
        task = task_service.get_task_by_id(task_id, user_id, db)
        return task
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: str,
    task_id: str,
    task_update: TaskUpdate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    try:
        updated_task = task_service.update_task(task_id, user_id, task_update, db)
        return updated_task
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.delete("/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: str,
    task_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this task"
        )
    
    try:
        success = task_service.delete_task(task_id, user_id, db)
        if success:
            return {"success": True, "message": "Task deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.patch("/{user_id}/tasks/{task_id}/complete", response_model=TaskRead)
def toggle_task_completion(
    user_id: str,
    task_id: str,
    is_completed: bool,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Verify that the user_id in the path matches the authenticated user
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this task"
        )
    
    try:
        updated_task = task_service.toggle_task_completion(task_id, user_id, is_completed, db)
        return updated_task
    except ResourceNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )