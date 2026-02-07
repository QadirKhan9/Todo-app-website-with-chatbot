from pydantic import BaseModel
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"

# Input models for tools
class AddTaskInput(BaseModel):
    title: str
    description: Optional[str] = None

class ListTasksInput(BaseModel):
    status: Optional[str] = "all"  # "pending", "completed", or "all"

class CompleteTaskInput(BaseModel):
    task_id: str

class UpdateTaskInput(BaseModel):
    task_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None

class DeleteTaskInput(BaseModel):
    task_id: str

# Output models for tools
class AddTaskOutput(BaseModel):
    success: bool
    task_id: str
    message: str

class ListTasksOutput(BaseModel):
    success: bool
    tasks: list
    count: int
    message: str

class TaskOperationOutput(BaseModel):
    success: bool
    task_id: str
    message: str

class ErrorOutput(BaseModel):
    success: bool
    error: str
    error_code: str