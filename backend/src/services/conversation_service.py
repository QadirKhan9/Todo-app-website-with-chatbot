from typing import List, Optional
from sqlmodel import select, Session
from uuid import UUID
from datetime import datetime
import json

from ..models.conversation import Conversation
from ..models.message import Message
from ..db.session import sync_engine


class ConversationService:
    """
    Service class to handle conversation-related operations.
    """

    async def create_conversation(
        self,
        conversation_id: str,
        user_id: str,
        title: str
    ) -> Conversation:
        """
        Create a new conversation.
        """
        # Note: Using sync session in an async method - this is acceptable for simple operations
        # but consider using async session for better performance in production
        with Session(sync_engine) as session:
            conversation = Conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                title=title
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation
    
    async def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Retrieve a conversation by its ID.
        """
        with Session(sync_engine) as session:
            statement = select(Conversation).where(Conversation.conversation_id == conversation_id)
            result = session.exec(statement)
            return result.first()

    async def get_conversations_by_user(self, user_id: str) -> List[Conversation]:
        """
        Retrieve all conversations for a specific user.
        """
        with Session(sync_engine) as session:
            statement = select(Conversation).where(Conversation.user_id == user_id)
            result = session.exec(statement)
            return result.all()

    async def update_conversation_title(self, conversation_id: str, title: str) -> Optional[Conversation]:
        """
        Update the title of a conversation.
        """
        with Session(sync_engine) as session:
            statement = select(Conversation).where(Conversation.conversation_id == conversation_id)
            result = session.exec(statement)
            conversation = result.first()

            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()
                session.refresh(conversation)
                return conversation

            return None

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation by its ID.
        """
        with Session(sync_engine) as session:
            statement = select(Conversation).where(Conversation.conversation_id == conversation_id)
            result = session.exec(statement)
            conversation = result.first()

            if conversation:
                session.delete(conversation)
                session.commit()
                return True

            return False

    async def add_message(self, message: Message) -> Message:
        """
        Add a message to a conversation.
        """
        with Session(sync_engine) as session:
            session.add(message)
            session.commit()
            session.refresh(message)

            # Update the conversation's updated_at timestamp
            conversation_statement = select(Conversation).where(
                Conversation.conversation_id == message.conversation_id
            )
            result = session.exec(conversation_statement)
            conversation = result.first()

            if conversation:
                conversation.updated_at = datetime.utcnow()
                session.add(conversation)
                session.commit()

            # Refresh the message again to ensure it's fully loaded
            session.refresh(message)
            # Return the message - it should be properly loaded now
            return message

    async def get_messages(self, conversation_id: str) -> List[Message]:
        """
        Retrieve all messages for a specific conversation.
        """
        with Session(sync_engine) as session:
            statement = select(Message).where(Message.conversation_id == conversation_id)
            result = session.exec(statement)
            return result.all()

    async def get_message(self, message_id: UUID) -> Optional[Message]:
        """
        Retrieve a specific message by its ID.
        """
        with Session(sync_engine) as session:
            statement = select(Message).where(Message.id == message_id)
            result = session.exec(statement)
            return result.first()