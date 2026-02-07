from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Request model for chat endpoint
    """
    message: str


class ActionTaken(BaseModel):
    """
    Model for describing actions taken by the AI
    """
    type: str  # e.g., "todo_created", "todo_updated", "todo_deleted", "info_provided"
    details: Dict[str, Any]


class ChatResponse(BaseModel):
    """
    Response model for chat endpoint
    """
    conversation_id: str
    message_id: str
    response: str
    action_taken: ActionTaken
    timestamp: datetime


class ConversationResponse(BaseModel):
    """
    Response model for conversation-related endpoints
    """
    id: str
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool


class MessageResponse(BaseModel):
    """
    Response model for message-related endpoints
    """
    id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    type: str  # 'standard', 'tool_call', 'tool_response'


class TodoResponse(BaseModel):
    """
    Response model for todo-related endpoints
    """
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]