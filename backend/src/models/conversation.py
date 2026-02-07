from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
import enum


class Conversation(SQLModel, table=True):
    """
    Represents a chat session between a user and the AI agent, identified by a unique conversation_id.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: str = Field(unique=True, index=True)
    user_id: str = Field(index=True)  # Identifier for the user who owns this conversation
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    title: str = Field(default="New Conversation")  # Auto-generated title for the conversation

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure updated_at is set to current time on creation
        if not kwargs.get('updated_at'):
            self.updated_at = datetime.utcnow()