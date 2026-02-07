from sqlmodel import Session, select
from backend.src.database.session import get_session
from backend.src.models.task import Task
from backend.src.models.responses import TaskOperationResponse
from backend.src.models.tool_schemas import TaskOperationOutput
from backend.src.exceptions import http_task_not_found, http_unauthorized_access
from uuid import UUID

async def delete_task_handler(
    task_id: str,
    user_id: str
) -> TaskOperationOutput:
    """
    Handler for deleting a task.

    Args:
        task_id: The ID of the task to delete
        user_id: The ID of the user deleting the task

    Returns:
        TaskOperationOutput: Response with task ID and success message
    """
    # Convert IDs to UUIDs
    task_uuid = UUID(task_id) if isinstance(task_id, str) else task_id
    user_uuid = UUID(user_id) if isinstance(user_id, str) else user_id

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

        # Delete the task
        session.delete(task)
        session.commit()

    # Return success response
    return TaskOperationOutput(
        success=True,
        task_id=task_id,
        message=f"Task '{task.title}' deleted successfully"
    )