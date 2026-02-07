"""
Integration test for tool call execution flow
Tests the complete flow of AI agent initiating tool calls and API handling them
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


def test_tool_call_execution_flow_integration(mock_conversation_service, mock_ai_agent_service, mock_tool_execution_service):
    """Integration test for the complete tool call execution flow"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting a conversation (return None to trigger creation of new conversation)
    mock_conv_instance.get_conversation.return_value = None
    
    # Mock creating a new conversation
    new_conversation = Conversation(
        conversation_id="integration-tool-call-test-id",
        user_id="test-user-id",
        title="Integration Tool Call Test"
    )
    mock_conv_instance.create_conversation.return_value = new_conversation
    
    # Mock adding messages
    user_message = Message(
        id=1,
        conversation_id="integration-tool-call-test-id",
        role=MessageRole.USER,
        content="What time is it?",
        timestamp="2023-01-01T10:00:00"
    )
    ai_message_with_tool_call = Message(
        id=2,
        conversation_id="integration-tool-call-test-id",
        role=MessageRole.ASSISTANT,
        content="Let me check the current time for you.",
        timestamp="2023-01-01T10:01:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message_with_tool_call
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service to return a response with tool calls initially,
    # then a final response after tool execution
    call_count = 0
    
    def mock_process_message_with_tools(conversation_id, user_message):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call: return a response with tool calls
            return {
                "role": "assistant",
                "content": "",
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
        else:
            # Second call: return final response after tool execution
            return {
                "role": "assistant",
                "content": "The current time is 10:30 AM UTC.",
                "tool_calls": []
            }
    
    mock_ai_agent_service.return_value.process_message_with_tools.side_effect = mock_process_message_with_tools
    
    # Mock tool execution service
    mock_tool_instance = AsyncMock()
    mock_tool_instance.execute_tool.return_value = {
        "current_time": "10:30 AM",
        "timezone": "UTC"
    }
    mock_tool_execution_service.return_value = mock_tool_instance
    
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
    
    # Verify conversation ID matches
    assert data["conversation_id"] == "integration-tool-call-test-id"
    
    # Verify response content includes the result from the tool
    assert "10:30 AM" in data["response"]["content"]
    assert "UTC" in data["response"]["content"]
    
    # Verify no active tool calls in the final response
    assert data["response"]["tool_calls"] == []
    
    # Verify that the tool execution service was called
    mock_tool_instance.execute_tool.assert_called_once_with(
        "get_current_time",
        {}
    )


def test_multiple_tool_calls_execution_flow_integration(mock_conversation_service, mock_ai_agent_service, mock_tool_execution_service):
    """Integration test for the complete flow with multiple tool calls"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="multi-integration-tool-call-test-id",
        user_id="test-user-id",
        title="Multi Integration Tool Call Test"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock adding messages
    user_message = Message(
        id=3,
        conversation_id="multi-integration-tool-call-test-id",
        role=MessageRole.USER,
        content="Get the current weather and time",
        timestamp="2023-01-01T10:00:00"
    )
    ai_message_with_tool_calls = Message(
        id=4,
        conversation_id="multi-integration-tool-call-test-id",
        role=MessageRole.ASSISTANT,
        content="Let me get the current weather and time for you.",
        timestamp="2023-01-01T10:01:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message_with_tool_calls
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service to return a response with multiple tool calls initially,
    # then a final response after tool execution
    call_count = 0
    
    def mock_process_message_with_tools(conversation_id, user_message):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call: return a response with multiple tool calls
            return {
                "role": "assistant",
                "content": "",
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
        else:
            # Second call: return final response after tool execution
            return {
                "role": "assistant",
                "content": "The current time is 10:30 AM UTC and the weather is sunny with a temperature of 22°C.",
                "tool_calls": []
            }
    
    mock_ai_agent_service.return_value.process_message_with_tools.side_effect = mock_process_message_with_tools
    
    # Mock tool execution service to handle multiple tools
    def mock_execute_tool(tool_name, arguments):
        if tool_name == "get_current_time":
            return {
                "current_time": "10:30 AM",
                "timezone": "UTC"
            }
        elif tool_name == "get_weather":
            return {
                "temperature": "22°C",
                "condition": "sunny",
                "location": "current"
            }
        else:
            return {"error": f"Unknown tool: {tool_name}"}
    
    mock_tool_instance = AsyncMock()
    mock_tool_instance.execute_tool.side_effect = mock_execute_tool
    mock_tool_execution_service.return_value = mock_tool_instance
    
    # Prepare request payload that would trigger multiple tool calls
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "multi-integration-tool-call-test-id",
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
    assert "10:30" in response_content
    
    # Verify no active tool calls in the final response
    assert data["response"]["tool_calls"] == []
    
    # Verify that the tool execution service was called for both tools
    assert mock_tool_instance.execute_tool.call_count == 2
    # Check that both tools were called
    calls = mock_tool_instance.execute_tool.call_args_list
    tool_names_called = [call[0][0] for call in calls]
    assert "get_current_time" in tool_names_called
    assert "get_weather" in tool_names_called


def test_tool_call_execution_with_error_integration(mock_conversation_service, mock_ai_agent_service, mock_tool_execution_service):
    """Integration test for handling errors during tool call execution"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="tool-error-integration-test-id",
        user_id="test-user-id",
        title="Tool Error Integration Test"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock adding messages
    user_message = Message(
        id=5,
        conversation_id="tool-error-integration-test-id",
        role=MessageRole.USER,
        content="Try to call an invalid tool",
        timestamp="2023-01-01T10:00:00"
    )
    ai_message_with_tool_call = Message(
        id=6,
        conversation_id="tool-error-integration-test-id",
        role=MessageRole.ASSISTANT,
        content="Attempting to call the tool.",
        timestamp="2023-01-01T10:01:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return user_message
        else:
            return ai_message_with_tool_call
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service to return a response with a tool call that will fail
    call_count = 0
    
    def mock_process_message_with_tools(conversation_id, user_message):
        nonlocal call_count
        call_count += 1
        
        if call_count == 1:
            # First call: return a response with a tool call that will fail
            return {
                "role": "assistant",
                "content": "",
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
        else:
            # Second call: return final response after tool execution attempt
            return {
                "role": "assistant",
                "content": "I encountered an error while processing your request.",
                "tool_calls": []
            }
    
    mock_ai_agent_service.return_value.process_message_with_tools.side_effect = mock_process_message_with_tools
    
    # Mock tool execution service to return an error
    mock_tool_instance = AsyncMock()
    mock_tool_instance.execute_tool.return_value = {
        "error": "Tool 'invalid_tool' not found or not available"
    }
    mock_tool_execution_service.return_value = mock_tool_instance
    
    # Prepare request payload
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "tool-error-integration-test-id",
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
    assert "error" in data["response"]["content"].lower() or \
           "encountered" in data["response"]["content"].lower()
    
    # Verify that the tool execution service was called
    mock_tool_instance.execute_tool.assert_called_once_with(
        "invalid_tool",
        {}
    )