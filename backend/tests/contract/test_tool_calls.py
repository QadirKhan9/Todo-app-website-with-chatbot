"""
Contract test for tool call handling
Verifies that the API properly handles AI agent tool calls
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from src.main import app
from src.models.conversation import Conversation
from src.models.message import Message, MessageRole
from src.services.conversation_service import ConversationService
from src.services.ai_agent_service import AIAgentService
from src.services.tool_execution_service import ToolExecutionService


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


@pytest.fixture
def mock_tool_execution_service():
    """Mock the tool execution service for testing"""
    with patch('src.services.tool_execution_service.ToolExecutionService') as mock:
        yield mock


def test_tool_call_handling_contract_success(mock_conversation_service, mock_ai_agent_service):
    """Test that the API properly handles tool calls from the AI agent"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting a conversation (return None to trigger creation of new conversation)
    mock_conv_instance.get_conversation.return_value = None
    
    # Mock creating a new conversation
    new_conversation = Conversation(
        conversation_id="tool-call-test-id",
        user_id="test-user-id",
        title="Tool Call Test"
    )
    mock_conv_instance.create_conversation.return_value = new_conversation
    
    # Mock adding messages
    user_message = Message(
        id=1,
        conversation_id="tool-call-test-id",
        role=MessageRole.USER,
        content="What time is it?",
        timestamp="2023-01-01T10:00:00"
    )
    ai_message = Message(
        id=2,
        conversation_id="tool-call-test-id",
        role=MessageRole.ASSISTANT,
        content="Let me check the current time for you.",
        timestamp="2023-01-01T10:01:00"
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
    assert "message_id" in data
    assert "response" in data
    assert "timestamp" in data
    
    # Verify response content includes tool call information
    assert "10:30 AM" in data["response"]["content"]
    assert data["response"]["role"] == "assistant"
    assert data["response"]["tool_calls"] == []  # Tool calls should be processed internally
    
    # Verify conversation ID matches
    assert data["conversation_id"] == "tool-call-test-id"


def test_multiple_tool_calls_handling_contract(mock_conversation_service, mock_ai_agent_service):
    """Test that the API properly handles multiple tool calls from the AI agent"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="multi-tool-call-test-id",
        user_id="test-user-id",
        title="Multi Tool Call Test"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock adding messages
    user_message = Message(
        id=3,
        conversation_id="multi-tool-call-test-id",
        role=MessageRole.USER,
        content="Get the current weather and time",
        timestamp="2023-01-01T10:00:00"
    )
    ai_message = Message(
        id=4,
        conversation_id="multi-tool-call-test-id",
        role=MessageRole.ASSISTANT,
        content="Here's the current weather and time.",
        timestamp="2023-01-01T10:01:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service to return a response with multiple tool calls
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "The current time is 10:30 AM UTC and the weather is sunny with a temperature of 22°C.",
        "tool_calls": [
            {
                "id": "call_456",
                "type": "function",
                "function": {
                    "name": "get_current_time",
                    "arguments": "{}"
                }
            },
            {
                "id": "call_789",
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "current"}'
                }
            }
        ]
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Prepare request payload that would trigger multiple tool calls
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "multi-tool-call-test-id",
        "message": "Get the current weather and time",
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
    
    # Verify response content includes information from both tools
    response_content = data["response"]["content"].lower()
    assert "time" in response_content
    assert "weather" in response_content
    assert "22" in response_content or "sunny" in response_content
    
    # Verify tool calls were processed internally
    assert data["response"]["tool_calls"] == []


def test_tool_call_error_handling_contract(mock_conversation_service, mock_ai_agent_service):
    """Test that the API properly handles errors during tool call execution"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="tool-call-error-test-id",
        user_id="test-user-id",
        title="Tool Call Error Test"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock adding messages
    user_message = Message(
        id=5,
        conversation_id="tool-call-error-test-id",
        role=MessageRole.USER,
        content="Try to call an invalid tool",
        timestamp="2023-01-01T10:00:00"
    )
    ai_message = Message(
        id=6,
        conversation_id="tool-call-error-test-id",
        role=MessageRole.ASSISTANT,
        content="I encountered an error while processing your request.",
        timestamp="2023-01-01T10:01:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service to return a response with tool calls that might fail
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "I encountered an error while processing your request.",
        "tool_calls": [
            {
                "id": "call_error",
                "type": "function",
                "function": {
                    "name": "invalid_tool",
                    "arguments": "{}"
                }
            }
        ]
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Prepare request payload
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "tool-call-error-test-id",
        "message": "Try to call an invalid tool",
        "metadata": {}
    }
    
    # Make request to the endpoint
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    response = client.post("/chat", headers=headers, json=payload)
    
    # Even with tool call errors, the API should return a successful response
    # The error should be handled gracefully and reflected in the AI's response
    assert response.status_code == 200
    
    # Parse response data
    data = response.json()
    
    # Verify response structure
    assert "conversation_id" in data
    assert "response" in data
    
    # The AI should have responded with an error message
    assert "error" in data["response"]["content"].lower()


def test_no_tool_calls_contract(mock_conversation_service, mock_ai_agent_service):
    """Test that the API properly handles messages that don't require tool calls"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="no-tool-call-test-id",
        user_id="test-user-id",
        title="No Tool Call Test"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock adding messages
    user_message = Message(
        id=7,
        conversation_id="no-tool-call-test-id",
        role=MessageRole.USER,
        content="Tell me a joke",
        timestamp="2023-01-01T10:00:00"
    )
    ai_message = Message(
        id=8,
        conversation_id="no-tool-call-test-id",
        role=MessageRole.ASSISTANT,
        content="Why don't scientists trust atoms? Because they make up everything!",
        timestamp="2023-01-01T10:01:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service to return a response without tool calls
    mock_ai_instance = AsyncMock()
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "Why don't scientists trust atoms? Because they make up everything!",
        "tool_calls": []
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Prepare request payload that doesn't require tool calls
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "no-tool-call-test-id",
        "message": "Tell me a joke",
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
    
    # Verify response content is a joke
    assert "joke" in data["response"]["content"].lower() or "atoms" in data["response"]["content"].lower()
    
    # Verify no tool calls were made
    assert data["response"]["tool_calls"] == []