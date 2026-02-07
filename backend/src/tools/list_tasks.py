from typing import List
from sqlmodel import Session, select
from backend.src.database.session import get_session
from backend.src.models.task import Task, TaskStatus
from backend.src.models.responses import TaskResponse
from backend.src.models.tool_schemas import ListTasksOutput
from uuid import UUID

async def list_tasks_handler(
    user_id: str,
    status: str = "all"
) -> ListTasksOutput:
    """
    Handler for listing tasks for a user.

    Args:
        user_id: The ID of the user whose tasks to list
        status: Filter by status ("pending", "completed", "all")

    Returns:
        ListTasksOutput: Response with list of tasks and count
    """
    # Convert user_id to UUID
    user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

    # Build query based on status filter
    query = select(Task).where(Task.user_id == user_uuid)

    if status.lower() == "pending":
        query = query.where(Task.status == TaskStatus.pending)
    elif status.lower() == "completed":
        query = query.where(Task.status == TaskStatus.completed)
    # If status is "all" or any other value, don't filter by status

    # Execute query
    from backend.src.database.session import sync_engine
    from sqlmodel import Session

    with Session(sync_engine) as session:
        tasks = session.exec(query).all()

    # Convert to response format
    task_responses = [
        {
            "id": str(task.id),
            "title": task.title,
            "description": task.description,
            "status": task.status.value if hasattr(task.status, 'value') else task.status,
            "created_at": task.created_at.isoformat() if hasattr(task.created_at, 'isoformat') else task.created_at,
            "updated_at": task.updated_at.isoformat() if hasattr(task.updated_at, 'isoformat') else task.updated_at
        }
        for task in tasks
    ]

    # Return response
    return ListTasksOutput(
        success=True,
        tasks=task_responses,
        count=len(tasks),
        message=f"Retrieved {len(tasks)} task(s)"
    )