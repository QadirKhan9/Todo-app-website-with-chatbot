from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional
import json
import enum


class ToolCallStatus(str, enum.Enum):
    """
    Enum for status of the tool call.
    """
    PENDING = "pending"
    EXECUTED = "executed"
    FAILED = "failed"


class ToolCall(SQLModel, table=True):
    """
    Represents an action initiated by the AI agent that requires external system interaction.
    """
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    message_id: UUID = Field(foreign_key="message.id")  # Foreign key referencing the Message that triggered the tool call
    tool_name: str = Field(min_length=1)  # Name of the tool to call
    tool_input: str = Field(default="{}")  # JSON string input parameters for the tool
    result: Optional[str] = Field(default=None)  # JSON string result returned by the tool
    status: ToolCallStatus = Field(sa_column_kwargs={"default": ToolCallStatus.PENDING})  # Status of the tool call
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate tool_input is a valid JSON string
        try:
            json.loads(self.tool_input)
        except json.JSONDecodeError:
            raise ValueError("tool_input must be a valid JSON string")
        
        # If result is provided, validate it's a valid JSON string
        if self.result:
            try:
                json.loads(self.result)
            except json.JSONDecodeError:
                raise ValueError("result must be a valid JSON string")