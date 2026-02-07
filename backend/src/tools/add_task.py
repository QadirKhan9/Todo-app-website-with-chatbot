from typing import Optional
from sqlmodel import Session
from backend.src.database.session import get_session
from backend.src.models.task import Task, TaskStatus
from backend.src.models.responses import AddTaskResponse
from backend.src.models.tool_schemas import AddTaskInput, AddTaskOutput
from backend.src.exceptions import http_invalid_input
from uuid import UUID
import uuid

async def add_task_handler(
    title: str,
    description: Optional[str] = None,
    user_id: str = None
) -> AddTaskOutput:
    """
    Handler for adding a new task.

    Args:
        title: The title of the task
        description: The description of the task (optional)
        user_id: The ID of the user creating the task

    Returns:
        AddTaskOutput: Response with task ID and success message
    """
    # Validate inputs
    if not title or len(title.strip()) == 0:
        raise http_invalid_input("Title is required and cannot be empty")

    if len(title) > 255:
        raise http_invalid_input("Title must be 255 characters or less")

    if description and len(description) > 1000:
        raise http_invalid_input("Description must be 1000 characters or less")

    # Create a new task instance
    task = Task(
        title=title,
        description=description,
        user_id=UUID(user_id) if isinstance(user_id, str) else user_id,
        status=TaskStatus.pending
    )

    # Save to database
    from backend.src.database.session import sync_engine
    from sqlmodel import Session

    with Session(sync_engine) as session:
        session.add(task)
        session.commit()
        session.refresh(task)

    # Return success response
    return AddTaskOutput(
        success=True,
        task_id=str(task.id),
        message=f"Task '{task.title}' created successfully"
    )