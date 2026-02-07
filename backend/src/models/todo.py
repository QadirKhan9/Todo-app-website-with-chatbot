from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from .user_model import User
from .subtask import Subtask  # Import directly for relationship

if TYPE_CHECKING:
    pass


class TodoStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class TodoPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoBase(SQLModel):
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    status: TodoStatus = Field(default=TodoStatus.PENDING)
    priority: TodoPriority = Field(default=TodoPriority.MEDIUM)
    due_date: Optional[datetime] = Field(default=None, nullable=True)


class Todo(TodoBase, table=True):
    __tablename__ = "todos"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)
    
    # Relationships
    user: "User" = Relationship(back_populates="todos")
    subtasks: list["Subtask"] = Relationship(back_populates="todo", sa_relationship_kwargs={"lazy": "select", "cascade": "all, delete-orphan"})