"""
Contract test for POST /chat endpoint
Verifies that the chat API conforms to the expected contract
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message
from src.services.conversation_service import ConversationService
from src.services.ai_agent_service import AIAgentService


client = TestClient(app)


@pytest.fixture
def mock_conversation_service():
    """Mock the conversation service for testing"""
    with patch('src.api.chat_router.ConversationService') as mock:
        yield mock


@pytest.fixture
def mock_ai_agent_service():
    """Mock the AI agent service for testing"""
    with patch('src.api.chat_router.AIAgentService') as mock:
        yield mock


def test_post_chat_endpoint_contract_success(mock_conversation_service, mock_ai_agent_service):
    """Test that the POST /chat endpoint returns the expected response structure"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    mock_conv_instance.get_conversation.return_value = None  # New conversation
    mock_conv_instance.create_conversation.return_value = Conversation(
        conversation_id="test-conversation-id",
        user_id="test-user-id",
        title="Test Conversation"
    )
    mock_conv_instance.add_message.return_value = Message(
        id=1,
        conversation_id="test-conversation-id",
        role="user",
        content="Test message"
    )
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "Test response from AI",
        "tool_calls": []
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Prepare request payload
    payload = {
        "user_id": "test-user-id",
        "message": "Hello, AI!",
        "metadata": {}
    }
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assertions for status code
    assert response.status_code == 200
    
    # Assertions for response structure
    data = response.json()
    assert "conversation_id" in data
    assert "message_id" in data
    assert "response" in data
    assert "timestamp" in data
    
    # Assertions for response content
    assert data["conversation_id"] == "test-conversation-id"
    assert isinstance(data["message_id"], str) or isinstance(data["message_id"], int)
    assert isinstance(data["response"], dict)
    assert "role" in data["response"]
    assert "content" in data["response"]
    assert "tool_calls" in data["response"]
    assert data["response"]["role"] == "assistant"
    assert "Test response from AI" in data["response"]["content"]
    assert isinstance(data["response"]["tool_calls"], list)
    assert isinstance(data["timestamp"], str)  # ISO format string


def test_post_chat_endpoint_contract_with_existing_conversation(mock_conversation_service, mock_ai_agent_service):
    """Test that the POST /chat endpoint works with an existing conversation"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    mock_conv_instance.get_conversation.return_value = Conversation(
        conversation_id="existing-conversation-id",
        user_id="test-user-id",
        title="Existing Conversation"
    )
    mock_conv_instance.add_message.return_value = Message(
        id=2,
        conversation_id="existing-conversation-id",
        role="user",
        content="Follow-up message"
    )
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "Follow-up response from AI",
        "tool_calls": [{"id": "call_1", "name": "test_tool", "arguments": "{}"}]
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Prepare request payload with conversation_id
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "existing-conversation-id",
        "message": "Follow-up message",
        "metadata": {"source": "test"}
    }
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assertions for status code
    assert response.status_code == 200
    
    # Assertions for response structure
    data = response.json()
    assert "conversation_id" in data
    assert data["conversation_id"] == "existing-conversation-id"
    assert "response" in data
    assert data["response"]["content"] == "Follow-up response from AI"
    assert len(data["response"]["tool_calls"]) == 1


def test_post_chat_endpoint_contract_validation_error():
    """Test that the POST /chat endpoint properly validates inputs"""
    
    # Prepare request payload with empty message
    payload = {
        "user_id": "test-user-id",
        "message": "",  # Empty message should trigger validation error
        "metadata": {}
    }
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.post("/chat", headers=headers, json=payload)
    
    # Should return validation error
    assert response.status_code == 422  # Unprocessable Entity for validation error


def test_post_chat_endpoint_missing_required_fields():
    """Test that the POST /chat endpoint properly handles missing required fields"""
    
    # Prepare request payload with missing required fields
    payload = {
        # Missing user_id and message
    }
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.post("/chat", headers=headers, json=payload)
    
    # Should return validation error due to missing required fields
    assert response.status_code == 422  # Unprocessable Entity for validation error