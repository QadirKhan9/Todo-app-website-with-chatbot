"""Pydantic schemas for Todo operations"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SubtaskResponse(BaseModel):
    id: str
    todo_id: str
    title: str
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_completed: Optional[bool] = None


class TodoResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskResponse] = []

    class Config:
        from_attributes = True