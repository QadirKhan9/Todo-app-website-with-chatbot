from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum
import uuid

# Base response models for API contracts

class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

class SuccessResponse(BaseModel):
    success: bool
    message: str

class AddTaskResponse(SuccessResponse):
    task_id: str

class ListTasksResponse(SuccessResponse):
    tasks: List[TaskResponse]
    count: int

class TaskOperationResponse(SuccessResponse):
    task_id: str

class ErrorResponse(BaseModel):
    success: bool
    error: str
    error_code: str