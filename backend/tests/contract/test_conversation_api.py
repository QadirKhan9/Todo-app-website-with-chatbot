"""
Contract test for GET /conversations/{conversation_id} endpoint
Verifies that the conversation API conforms to the expected contract
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.conversation_service import ConversationService


client = TestClient(app)


@pytest.fixture
def mock_conversation_service():
    """Mock the conversation service for testing"""
    with patch('src.api.chat_router.ConversationService') as mock:
        yield mock


def test_get_conversation_endpoint_contract_success(mock_conversation_service):
    """Test that the GET /conversations/{conversation_id} endpoint returns the expected response structure"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting a conversation
    conversation = Conversation(
        conversation_id="test-conversation-id",
        user_id="test-user-id",
        title="Test Conversation"
    )
    mock_conv_instance.get_conversation.return_value = conversation
    
    # Mock getting messages for the conversation
    messages = [
        Message(
            id=1,
            conversation_id="test-conversation-id",
            role=MessageRole.USER,
            content="Hello, AI!",
            timestamp="2023-01-01T10:00:00"
        ),
        Message(
            id=2,
            conversation_id="test-conversation-id",
            role=MessageRole.ASSISTANT,
            content="Hello, user!",
            timestamp="2023-01-01T10:01:00"
        )
    ]
    mock_conv_instance.get_messages.return_value = messages
    mock_conversation_service.return_value = mock_conv_instance
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.get("/conversations/test-conversation-id", headers=headers)
    
    # Assertions for status code
    assert response.status_code == 200
    
    # Assertions for response structure
    data = response.json()
    assert "conversation_id" in data
    assert "messages" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    # Assertions for conversation data
    assert data["conversation_id"] == "test-conversation-id"
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) == 2
    
    # Assertions for message structure
    for msg in data["messages"]:
        assert "id" in msg
        assert "role" in msg
        assert "content" in msg
        assert "timestamp" in msg
        assert "tool_calls" in msg
        assert "tool_call_results" in msg
        
        # Verify role is valid
        assert msg["role"] in ["user", "assistant"]
        
        # Verify timestamp format
        assert isinstance(msg["timestamp"], str)
    
    # Verify created_at and updated_at are ISO format strings
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)


def test_get_conversation_endpoint_contract_not_found(mock_conversation_service):
    """Test that the GET /conversations/{conversation_id} endpoint returns 404 for non-existent conversation"""
    
    # Mock conversation service to return None (conversation not found)
    mock_conv_instance = AsyncMock()
    mock_conv_instance.get_conversation.return_value = None
    mock_conversation_service.return_value = mock_conv_instance
    
    # Make request to the endpoint with a non-existent conversation ID
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.get("/conversations/non-existent-id", headers=headers)
    
    # Should return 404 Not Found
    assert response.status_code == 404


def test_get_conversation_endpoint_contract_invalid_id_format():
    """Test that the GET /conversations/{conversation_id} endpoint properly validates the conversation ID format"""
    
    # Make request to the endpoint with an invalid conversation ID format
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.get("/conversations/invalid!@#$%id", headers=headers)
    
    # Should return 422 Unprocessable Entity for validation error
    # (assuming the API validates the ID format)
    assert response.status_code in [404, 422]


def test_get_conversation_endpoint_contract_empty_messages(mock_conversation_service):
    """Test that the GET /conversations/{conversation_id} endpoint handles conversations with no messages"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting a conversation
    conversation = Conversation(
        conversation_id="empty-conversation-id",
        user_id="test-user-id",
        title="Empty Conversation"
    )
    mock_conv_instance.get_conversation.return_value = conversation
    
    # Mock getting empty messages list
    mock_conv_instance.get_messages.return_value = []
    mock_conversation_service.return_value = mock_conv_instance
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.get("/conversations/empty-conversation-id", headers=headers)
    
    # Assertions for status code
    assert response.status_code == 200
    
    # Assertions for response structure
    data = response.json()
    assert "conversation_id" in data
    assert "messages" in data
    assert "created_at" in data
    assert "updated_at" in data
    
    # Assertions for conversation data
    assert data["conversation_id"] == "empty-conversation-id"
    assert isinstance(data["messages"], list)
    assert len(data["messages"]) == 0  # Should be empty list
    
    # Verify created_at and updated_at are ISO format strings
    assert isinstance(data["created_at"], str)
    assert isinstance(data["updated_at"], str)


def test_get_conversation_endpoint_contract_with_tool_calls(mock_conversation_service):
    """Test that the GET /conversations/{conversation_id} endpoint properly handles messages with tool calls"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting a conversation
    conversation = Conversation(
        conversation_id="tool-call-conversation-id",
        user_id="test-user-id",
        title="Tool Call Conversation"
    )
    mock_conv_instance.get_conversation.return_value = conversation
    
    # Mock getting messages for the conversation with tool call metadata
    import json
    messages = [
        Message(
            id=3,
            conversation_id="tool-call-conversation-id",
            role=MessageRole.USER,
            content="What time is it?",
            timestamp="2023-01-01T10:00:00"
        ),
        Message(
            id=4,
            conversation_id="tool-call-conversation-id",
            role=MessageRole.ASSISTANT,
            content="Let me check the time for you.",
            message_metadata=json.dumps([{
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "arguments": "{}"
                }
            }]),
            timestamp="2023-01-01T10:01:00"
        )
    ]
    mock_conv_instance.get_messages.return_value = messages
    mock_conversation_service.return_value = mock_conv_instance
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.get("/conversations/tool-call-conversation-id", headers=headers)
    
    # Assertions for status code
    assert response.status_code == 200
    
    # Assertions for response structure
    data = response.json()
    assert "conversation_id" in data
    assert "messages" in data
    assert len(data["messages"]) == 2
    
    # Find the assistant message and verify tool calls
    assistant_msg = next((msg for msg in data["messages"] if msg["role"] == "assistant"), None)
    assert assistant_msg is not None
    assert len(assistant_msg["tool_calls"]) == 1
    assert assistant_msg["tool_calls"][0]["id"] == "call_123"
    assert assistant_msg["tool_calls"][0]["function"]["name"] == "get_current_time"