"""
Integration test for sending message and receiving response
Tests the complete flow from sending a message to receiving an AI response
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
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


def test_send_message_receive_response_integration(mock_conversation_service, mock_ai_agent_service):
    """Integration test for sending a message and receiving an AI response"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting a conversation (return None to trigger creation of new conversation)
    mock_conv_instance.get_conversation.return_value = None
    
    # Mock creating a new conversation
    new_conversation = Conversation(
        conversation_id="test-conversation-id",
        user_id="test-user-id",
        title="Test Conversation"
    )
    mock_conv_instance.create_conversation.return_value = new_conversation
    
    # Mock adding a message
    user_message = Message(
        id=1,
        conversation_id="test-conversation-id",
        role=MessageRole.USER,
        content="Hello, AI!"
    )
    ai_message = Message(
        id=2,
        conversation_id="test-conversation-id",
        role=MessageRole.ASSISTANT,
        content="Hello, user! How can I assist you today?"
    )
    
    # Configure add_message to return different messages based on content
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "Hello, user! How can I assist you today?",
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
    
    # Assertions for successful response
    assert response.status_code == 200
    
    # Parse response data
    data = response.json()
    
    # Verify response structure
    assert "conversation_id" in data
    assert "message_id" in data
    assert "response" in data
    assert "timestamp" in data
    
    # Verify conversation ID matches what was created
    assert data["conversation_id"] == "test-conversation-id"
    
    # Verify response content
    assert data["response"]["content"] == "Hello, user! How can I assist you today?"
    assert data["response"]["role"] == "assistant"
    assert data["response"]["tool_calls"] == []
    
    # Verify that the conversation service methods were called correctly
    mock_conv_instance.get_conversation.assert_called_once_with(None)
    mock_conv_instance.create_conversation.assert_called_once()
    assert mock_conv_instance.add_message.call_count == 2  # Once for user message, once for AI response
    
    # Verify that the AI agent service was called
    mock_ai_instance.process_message_with_tools.assert_called_once_with(
        conversation_id="test-conversation-id",
        user_message="Hello, AI!"
    )


def test_send_message_receive_response_with_existing_conversation(mock_conversation_service, mock_ai_agent_service):
    """Integration test for sending a message to an existing conversation and receiving a response"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="existing-conversation-id",
        user_id="test-user-id",
        title="Existing Conversation"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock adding a message
    user_message = Message(
        id=3,
        conversation_id="existing-conversation-id",
        role=MessageRole.USER,
        content="Follow-up question?"
    )
    ai_message = Message(
        id=4,
        conversation_id="existing-conversation-id",
        role=MessageRole.ASSISTANT,
        content="Sure, I can help with that follow-up question."
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "Sure, I can help with that follow-up question.",
        "tool_calls": []
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Prepare request payload with existing conversation ID
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "existing-conversation-id",
        "message": "Follow-up question?",
        "metadata": {"context": "follow-up"}
    }
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assertions for successful response
    assert response.status_code == 200
    
    # Parse response data
    data = response.json()
    
    # Verify conversation ID matches the existing one
    assert data["conversation_id"] == "existing-conversation-id"
    
    # Verify response content
    assert data["response"]["content"] == "Sure, I can help with that follow-up question."
    
    # Verify that the conversation service methods were called correctly
    mock_conv_instance.get_conversation.assert_called_once_with("existing-conversation-id")
    mock_conv_instance.add_message.assert_any_call(user_message)  # Called twice, once for user, once for AI
    mock_ai_instance.process_message_with_tools.assert_called_once_with(
        conversation_id="existing-conversation-id",
        user_message="Follow-up question?"
    )


def test_send_message_triggers_tool_calls_integration(mock_conversation_service, mock_ai_agent_service):
    """Integration test for sending a message that triggers tool calls"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting a conversation (return None to trigger creation of new conversation)
    mock_conv_instance.get_conversation.return_value = None
    
    # Mock creating a new conversation
    new_conversation = Conversation(
        conversation_id="tool-test-conversation-id",
        user_id="test-user-id",
        title="Tool Test Conversation"
    )
    mock_conv_instance.create_conversation.return_value = new_conversation
    
    # Mock adding messages
    user_message = Message(
        id=5,
        conversation_id="tool-test-conversation-id",
        role=MessageRole.USER,
        content="What time is it?"
    )
    ai_message = Message(
        id=6,
        conversation_id="tool-test-conversation-id",
        role=MessageRole.ASSISTANT,
        content="The current time is 10:30 AM UTC."
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service to return a response with tool calls
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "The current time is 10:30 AM UTC.",
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "arguments": "{}"
                }
            }
        ]
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Prepare request payload that would trigger a tool call
    payload = {
        "user_id": "test-user-id",
        "message": "What time is it?",
        "metadata": {}
    }
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assertions for successful response
    assert response.status_code == 200
    
    # Parse response data
    data = response.json()
    
    # Verify response structure
    assert "conversation_id" in data
    assert data["conversation_id"] == "tool-test-conversation-id"
    
    # Verify response content includes tool call information
    assert "10:30 AM" in data["response"]["content"]
    assert data["response"]["role"] == "assistant"
    
    # Verify that the AI agent service was called
    mock_ai_instance.process_message_with_tools.assert_called_once_with(
        conversation_id="tool-test-conversation-id",
        user_message="What time is it?"
    )