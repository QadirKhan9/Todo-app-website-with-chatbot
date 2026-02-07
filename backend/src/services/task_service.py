from sqlmodel import Session, select
from typing import List, Optional
from ..models.task import Task, TaskCreate, TaskUpdate
from ..models.user_model import User
from ..utils.exceptions import ResourceNotFoundError
import uuid


def create_task(task: TaskCreate, db_session: Session) -> Task:
    # Get the user_id from the task object
    actual_user_id = getattr(task, 'user_id', None)

    if not actual_user_id:
        raise ResourceNotFoundError("User", "No user_id provided")

    # Verify the user exists - try to handle UUID format differences
    try:
        # Try getting the user with the UUID object
        user = db_session.get(User, actual_user_id)
        if not user:
            # If not found, try converting to string and back
            user = db_session.get(User, str(actual_user_id))
    except Exception:
        # If there's an error with the UUID format, try string format
        user = db_session.get(User, str(actual_user_id))

    if not user:
        raise ResourceNotFoundError("User", str(actual_user_id))

    # Create task from the input data
    db_task = Task.model_validate(task)  # Use model_validate instead of from_orm
    # The user_id is already set in the task object

    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)

    return db_task


def get_task_by_id(task_id: str, user_id: str, db_session: Session) -> Task:
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    task = db_session.exec(statement).first()
    if not task:
        raise ResourceNotFoundError("Task", str(task_id))
    return task


def get_tasks_by_user(user_id: str,
                     db_session: Session,
                     completed: Optional[bool] = None,
                     priority: Optional[str] = None,
                     limit: int = 20,
                     offset: int = 0) -> List[Task]:
    statement = select(Task).where(Task.user_id == user_id)

    if completed is not None:
        # Assuming there's an is_completed field in Task model
        # If not, we'll need to adjust based on actual model
        statement = statement.where(Task.status == ("completed" if completed else "pending"))

    if priority:
        statement = statement.where(Task.priority == priority)

    statement = statement.offset(offset).limit(limit)

    return db_session.exec(statement).all()


def update_task(task_id: str,
               user_id: str,
               task_update: TaskUpdate,
               db_session: Session) -> Task:
    db_task = get_task_by_id(task_id, user_id, db_session)

    # Update only the fields that are provided
    update_data = task_update.model_dump(exclude_unset=True)  # Pydantic v2 syntax
    for field, value in update_data.items():
        setattr(db_task, field, value)

    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)

    return db_task


def delete_task(task_id: str, user_id: str, db_session: Session) -> bool:
    db_task = get_task_by_id(task_id, user_id, db_session)

    db_session.delete(db_task)
    db_session.commit()

    return True


def toggle_task_completion(task_id: str, user_id: str,
                         is_completed: bool, db_session: Session) -> Task:
    db_task = get_task_by_id(task_id, user_id, db_session)

    # Update status based on is_completed flag
    db_task.status = "completed" if is_completed else "pending"
    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)

    return db_task