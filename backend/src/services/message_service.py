from typing import List, Optional
from sqlmodel import Session, select
from uuid import UUID
from ..models.message import Message
from .base_service import BaseService


class MessageService:
    """
    Service class for handling message-related operations
    """
    
    def __init__(self):
        self.base_service = BaseService(Message)
    
    def create_message(self, db: Session, conversation_id: UUID, role: str, content: str, message_type: str = "standard", 
                       tool_calls: Optional[dict] = None, tool_responses: Optional[dict] = None):
        """
        Create a new message in a conversation
        """
        message_data = {
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "message_type": message_type,
            "tool_calls": tool_calls,
            "tool_responses": tool_responses
        }
        return self.base_service.create(db, message_data)
    
    def get_message(self, db: Session, message_id: UUID):
        """
        Get a specific message by ID
        """
        statement = select(Message).where(Message.id == message_id)
        return db.exec(statement).first()
    
    def get_messages_for_conversation(self, db: Session, conversation_id: UUID, skip: int = 0, limit: int = 100):
        """
        Get all messages for a specific conversation
        """
        statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp).offset(skip).limit(limit)
        return db.exec(statement).all()
    
    def update_message(self, db: Session, message_id: UUID, message_data: dict):
        """
        Update a specific message
        """
        message = self.get_message(db, message_id)
        if message:
            for field, value in message_data.items():
                setattr(message, field, value)
            db.add(message)
            db.commit()
            db.refresh(message)
        return message
    
    def delete_message(self, db: Session, message_id: UUID):
        """
        Delete a specific message
        """
        message = self.get_message(db, message_id)
        if message:
            db.delete(message)
            db.commit()
        return message