"""
Integration test for resuming conversations
Tests the complete flow of resuming a conversation with preserved context
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


def test_resume_conversation_integration(mock_conversation_service, mock_ai_agent_service):
    """Integration test for resuming a conversation with preserved context"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="resume-test-conversation-id",
        user_id="test-user-id",
        title="Resume Test Conversation"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock getting existing messages for the conversation
    existing_messages = [
        Message(
            id=1,
            conversation_id="resume-test-conversation-id",
            role=MessageRole.USER,
            content="Initial message: Create a todo to buy groceries",
            timestamp="2023-01-01T10:00:00"
        ),
        Message(
            id=2,
            conversation_id="resume-test-conversation-id",
            role=MessageRole.ASSISTANT,
            content="I've created a todo to buy groceries for you.",
            timestamp="2023-01-01T10:01:00"
        ),
        Message(
            id=3,
            conversation_id="resume-test-conversation-id",
            role=MessageRole.USER,
            content="Update that todo to include milk",
            timestamp="2023-01-01T10:02:00"
        ),
        Message(
            id=4,
            conversation_id="resume-test-conversation-id",
            role=MessageRole.ASSISTANT,
            content="I've updated the groceries todo to include milk.",
            timestamp="2023-01-01T10:03:00"
        )
    ]
    mock_conv_instance.get_messages.return_value = existing_messages
    
    # Mock adding a new message
    follow_up_message = Message(
        id=5,
        conversation_id="resume-test-conversation-id",
        role=MessageRole.USER,
        content="What were my todos again?",
        timestamp="2023-01-01T10:04:00"
    )
    follow_up_response = Message(
        id=6,
        conversation_id="resume-test-conversation-id",
        role=MessageRole.ASSISTANT,
        content="You have one todo: buy groceries including milk.",
        timestamp="2023-01-01T10:05:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return follow_up_message
        else:
            return follow_up_response
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service
    mock_ai_instance = AsyncMock()
    
    # Mock the AI agent to return a response that shows it has context of previous messages
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "You have one todo: buy groceries including milk.",
        "tool_calls": []
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # First, make a request to get the conversation history
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    history_response = client.get("/conversations/resume-test-conversation-id", headers=headers)
    
    # Verify the conversation history is returned correctly
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert len(history_data["messages"]) == 4  # 2 pairs of user/assistant messages
    
    # Now, send a follow-up message to test if the AI has the context
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "resume-test-conversation-id",
        "message": "What were my todos again?",
        "metadata": {}
    }
    
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assertions for successful response
    assert response.status_code == 200
    
    # Parse response data
    data = response.json()
    
    # Verify response content shows the AI had context of previous messages
    assert "groceries" in data["response"]["content"].lower()
    assert "milk" in data["response"]["content"].lower()
    
    # Verify that the conversation service methods were called correctly
    mock_conv_instance.get_conversation.assert_called_with("resume-test-conversation-id")
    mock_conv_instance.get_messages.assert_called_with("resume-test-conversation-id")
    assert mock_conv_instance.add_message.call_count == 2  # Once for user message, once for AI response
    
    # Verify that the AI agent service was called with the correct conversation ID
    mock_ai_instance.process_message_with_tools.assert_called_once_with(
        conversation_id="resume-test-conversation-id",
        user_message="What were my todos again?"
    )


def test_resume_conversation_with_context_preservation(mock_conversation_service, mock_ai_agent_service):
    """Integration test to verify that conversation context is preserved when resuming"""
    
    # Mock conversation service
    mock_conv_instance = AsyncMock()
    
    # Mock getting an existing conversation
    existing_conversation = Conversation(
        conversation_id="context-preservation-test-id",
        user_id="test-user-id",
        title="Context Preservation Test"
    )
    mock_conv_instance.get_conversation.return_value = existing_conversation
    
    # Mock getting existing messages for the conversation
    existing_messages = [
        Message(
            id=10,
            conversation_id="context-preservation-test-id",
            role=MessageRole.USER,
            content="I want to create a todo list for my trip to Paris",
            timestamp="2023-01-01T10:00:00"
        ),
        Message(
            id=11,
            conversation_id="context-preservation-test-id",
            role=MessageRole.ASSISTANT,
            content="Sure, I can help you with that. What items should be on your Paris trip todo list?",
            timestamp="2023-01-01T10:01:00"
        ),
        Message(
            id=12,
            conversation_id="context-preservation-test-id",
            role=MessageRole.USER,
            content="Book flights, reserve hotels, pack clothes",
            timestamp="2023-01-01T10:02:00"
        ),
        Message(
            id=13,
            conversation_id="context-preservation-test-id",
            role=MessageRole.ASSISTANT,
            content="I've added those items to your Paris trip todo list.",
            timestamp="2023-01-01T10:03:00"
        )
    ]
    mock_conv_instance.get_messages.return_value = existing_messages
    
    # Mock adding a new message that refers to previous context
    follow_up_message = Message(
        id=14,
        conversation_id="context-preservation-test-id",
        role=MessageRole.USER,
        content="Add visit Eiffel Tower to my Paris todo list",
        timestamp="2023-01-01T10:04:00"
    )
    follow_up_response = Message(
        id=15,
        conversation_id="context-persistence-test-id",
        role=MessageRole.ASSISTANT,
        content="I've added 'visit Eiffel Tower' to your Paris trip todo list.",
        timestamp="2023-01-01T10:05:00"
    )
    
    def mock_add_message(message):
        if message.role == MessageRole.USER:
            return follow_up_message
        else:
            return follow_up_response
    
    mock_conv_instance.add_message.side_effect = mock_add_message
    mock_conversation_service.return_value = mock_conv_instance
    
    # Mock AI agent service
    mock_ai_instance = AsyncMock()
    
    # Mock the AI agent to return a response that shows it understands the context
    mock_ai_instance.process_message_with_tools.return_value = {
        "role": "assistant",
        "content": "I've added 'visit Eiffel Tower' to your Paris trip todo list.",
        "tool_calls": []
    }
    mock_ai_agent_service.return_value = mock_ai_instance
    
    # Send a follow-up message that refers to the previous context
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "context-preservation-test-id",
        "message": "Add visit Eiffel Tower to my Paris todo list",
        "metadata": {"context": "referring to previous conversation"}
    }
    
    response = client.post("/chat", headers=headers, json=payload)
    
    # Assertions for successful response
    assert response.status_code == 200
    
    # Parse response data
    data = response.json()
    
    # Verify response content shows the AI understood the context of "Paris todo list"
    assert "paris" in data["response"]["content"].lower()
    assert "eiffel tower" in data["response"]["content"].lower()
    assert "added" in data["response"]["content"].lower()
    
    # Verify that the AI agent service was called with the correct conversation ID
    mock_ai_instance.process_message_with_tools.assert_called_once_with(
        conversation_id="context-preservation-test-id",
        user_message="Add visit Eiffel Tower to my Paris todo list"
    )


def test_resume_nonexistent_conversation_error(mock_conversation_service):
    """Integration test to verify appropriate error when resuming non-existent conversation"""
    
    # Mock conversation service to return None (conversation not found)
    mock_conv_instance = AsyncMock()
    mock_conv_instance.get_conversation.return_value = None
    mock_conversation_service.return_value = mock_conv_instance
    
    # Try to send a message to a non-existent conversation
    headers = {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }
    payload = {
        "user_id": "test-user-id",
        "conversation_id": "non-existent-conversation-id",
        "message": "Trying to resume a non-existent conversation",
        "metadata": {}
    }
    
    response = client.post("/chat", headers=headers, json=payload)
    
    # Should return 404 Not Found since conversation doesn't exist
    assert response.status_code == 404