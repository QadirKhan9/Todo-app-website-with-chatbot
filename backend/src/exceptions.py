from fastapi import HTTPException, status

class TaskNotFoundException(Exception):
    """Raised when a task is not found."""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")

class UnauthorizedAccessException(Exception):
    """Raised when a user tries to access another user's task."""
    def __init__(self, task_id: str, user_id: str):
        self.task_id = task_id
        self.user_id = user_id
        super().__init__(f"User {user_id} does not have access to task {task_id}")

class UserNotFoundException(Exception):
    """Raised when a user is not found."""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")

# HTTP exceptions for API responses
def http_task_not_found(task_id: str):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task with id {task_id} not found"
    )

def http_unauthorized_access(task_id: str, user_id: str):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"User {user_id} does not have access to task {task_id}"
    )

def http_user_not_found(user_id: str):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id {user_id} not found"
    )

def http_invalid_input(detail: str):
    return HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=detail
    )