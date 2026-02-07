from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
import json
import enum


class MessageRole(str, enum.Enum):
    """
    Enum for message roles (sender types).
    """
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """
    Represents a single communication unit in a conversation, containing sender, content, and timestamp.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.conversation_id", index=True)
    role: MessageRole = Field(sa_column_kwargs={"default": MessageRole.USER})
    content: str = Field(min_length=1)  # The actual message content
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_metadata: Optional[str] = Field(default=None)  # Optional, for storing additional data like tool calls (as JSON string)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate content is not empty
        if not kwargs.get('content', '').strip():
            raise ValueError("Content cannot be empty")