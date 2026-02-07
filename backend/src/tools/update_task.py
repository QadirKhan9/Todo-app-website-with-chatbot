from typing import Optional
from sqlmodel import Session, select
from backend.src.database.session import get_session
from backend.src.models.task import Task, TaskStatus
from backend.src.models.responses import TaskOperationResponse
from backend.src.models.tool_schemas import TaskOperationOutput
from backend.src.exceptions import http_task_not_found, http_unauthorized_access, http_invalid_input
from uuid import UUID

async def update_task_handler(
    task_id: str,
    user_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None
) -> TaskOperationOutput:
    """
    Handler for updating a task.

    Args:
        task_id: The ID of the task to update
        user_id: The ID of the user updating the task
        title: New title (optional)
        description: New description (optional)
        status: New status (optional)

    Returns:
        TaskOperationOutput: Response with task ID and success message
    """
    # Convert IDs to UUIDs
    task_uuid = UUID(task_id) if isinstance(task_id, str) else task_id
    user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

    # Validate status if provided
    if status is not None and status not in ["pending", "completed"]:
        raise http_invalid_input("Status must be either 'pending' or 'completed'")

    # Get the task from the database
    from backend.src.database.session import sync_engine
    from sqlmodel import Session, select

    with Session(sync_engine) as session:
        # First, verify the task exists and belongs to the user
        statement = select(Task).where(Task.id == task_uuid).where(Task.user_id == user_uuid)
        task = session.exec(statement).first()

        if not task:
            # Task doesn't exist or doesn't belong to the user
            raise http_unauthorized_access(task_id, user_id)

        # Update the task fields if provided
        if title is not None:
            if not title or len(title.strip()) == 0:
                raise http_invalid_input("Title cannot be empty")
            if len(title) > 255:
                raise http_invalid_input("Title must be 255 characters or less")
            task.title = title

        if description is not None:
            if len(description) > 1000:
                raise http_invalid_input("Description must be 1000 characters or less")
            task.description = description

        if status is not None:
            task.status = TaskStatus(status)

        session.add(task)
        session.commit()
        session.refresh(task)

    # Return success response
    return TaskOperationOutput(
        success=True,
        task_id=task_id,
        message=f"Task '{task.title}' updated successfully"
    )