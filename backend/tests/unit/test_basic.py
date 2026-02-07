import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from backend.src.main import app
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message, MessageRole
from backend.src.services.conversation_service import ConversationService


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.mark.asyncio
async def test_create_conversation():
    """Test creating a new conversation."""
    service = ConversationService()
    
    # Create a conversation
    conversation = await service.create_conversation(
        conversation_id=str(uuid4()),
        user_id="test_user",
        title="Test Conversation"
    )
    
    assert conversation.user_id == "test_user"
    assert conversation.title == "Test Conversation"


@pytest.mark.asyncio
async def test_add_message_to_conversation():
    """Test adding a message to a conversation."""
    service = ConversationService()
    
    # Create a conversation
    conversation = await service.create_conversation(
        conversation_id=str(uuid4()),
        user_id="test_user",
        title="Test Conversation"
    )
    
    # Add a message
    message = Message(
        conversation_id=conversation.conversation_id,
        role=MessageRole.USER,
        content="Hello, world!"
    )
    saved_message = await service.add_message(message)
    
    assert saved_message.content == "Hello, world!"
    assert saved_message.role == MessageRole.USER


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "chat-api-orchestration"}