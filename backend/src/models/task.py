from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional
import uuid
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"

class PriorityLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(max_length=1000, default=None)
    status: TaskStatus = Field(default=TaskStatus.pending)

class Task(TaskBase, table=True):
    id: Optional[uuid.UUID] = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")  # Removed ondelete parameter
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"

# Pydantic models for API requests/responses
class TaskCreate(TaskBase):
    title: str
    description: Optional[str] = None
    priority: Optional[PriorityLevel] = None
    user_id: uuid.UUID  # Add user_id as required field for creation

class TaskRead(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[PriorityLevel] = None