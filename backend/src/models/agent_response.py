from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
import json
import enum


class FinishReason(str, enum.Enum):
    """
    Enum for reasons why the agent stopped generating.
    """
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"


class AgentResponse(SQLModel, table=True):
    """
    Represents the AI-generated response to a user message, potentially containing multiple content segments.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID = Field(foreign_key="message.id")  # Foreign key referencing the corresponding Message
    content_segments: str = Field(default="[]")  # JSON string array of content segments in the response
    finish_reason: FinishReason = Field(sa_column_kwargs={"default": FinishReason.STOP})  # Reason why the agent stopped generating

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate content_segments is a valid JSON array
        try:
            segments = json.loads(self.content_segments)
            if not isinstance(segments, list):
                raise ValueError("content_segments must be a JSON array")
        except json.JSONDecodeError:
            raise ValueError("content_segments must be a valid JSON string")