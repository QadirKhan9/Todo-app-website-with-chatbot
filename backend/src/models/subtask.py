from sqlmodel import SQLModel, Field, Relationship
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4
from datetime import datetime

if TYPE_CHECKING:
    from .todo import Todo, TodoStatus


class SubtaskBase(SQLModel):
    title: str = Field(nullable=False)
    is_completed: bool = Field(default=False)


class Subtask(SubtaskBase, table=True):
    __tablename__ = "subtasks"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    todo_id: UUID = Field(foreign_key="todos.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    todo: "Todo" = Relationship(back_populates="subtasks")


class SubtaskCreate(SubtaskBase):
    title: str
    is_completed: Optional[bool] = False


class SubtaskUpdate(SQLModel):
    title: Optional[str] = None
    is_completed: Optional[bool] = None


class SubtaskRead(SubtaskBase):
    id: UUID
    todo_id: UUID
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]