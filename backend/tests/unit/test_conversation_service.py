import pytest
from unittest.mock import MagicMock
from src.services.conversation_service import ConversationService
from src.models.conversation import Conversation
from uuid import UUID


@pytest.fixture
def conversation_service():
    return ConversationService()


@pytest.fixture
def mock_db():
    return MagicMock()


def test_create_conversation(conversation_service, mock_db):
    # Arrange
    user_id = UUID(int=1)
    title = "Test Conversation"
    
    # Act
    result = conversation_service.create_conversation(mock_db, user_id, title)
    
    # Assert
    assert result is not None
    assert result.title == title
    assert result.user_id == user_id


def test_get_conversation(conversation_service, mock_db):
    # Arrange
    conversation_id = UUID(int=1)
    user_id = UUID(int=2)
    
    # Mock conversation in DB
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Test Conversation"
    )
    mock_db.get.return_value = mock_conversation
    
    # Act
    result = conversation_service.get_conversation(mock_db, conversation_id, user_id)
    
    # Assert
    assert result is not None
    assert result.id == conversation_id
    assert result.user_id == user_id


def test_get_conversations(conversation_service, mock_db):
    # Arrange
    user_id = UUID(int=1)
    mock_conversations = [
        Conversation(
            id=UUID(int=1),
            user_id=user_id,
            title="Test Conversation 1"
        ),
        Conversation(
            id=UUID(int=2),
            user_id=user_id,
            title="Test Conversation 2"
        )
    ]
    mock_db.exec.return_value.all.return_value = mock_conversations
    
    # Act
    result = conversation_service.get_conversations(mock_db, user_id)
    
    # Assert
    assert len(result) == 2
    assert all(conv.user_id == user_id for conv in result)


def test_update_conversation(conversation_service, mock_db):
    # Arrange
    conversation_id = UUID(int=1)
    user_id = UUID(int=2)
    update_data = {"title": "Updated Title"}
    
    # Mock existing conversation
    mock_existing_conversation = Conversation(
        id=conversation_id,
        user_id=user_id,
        title="Original Title"
    )
    mock_db.get.return_value = mock_existing_conversation
    
    # Act
    result = conversation_service.update_conversation(mock_db, conversation_id, update_data)
    
    # Assert
    assert result is not None
    assert result.title == "Updated Title"


def test_delete_conversation(conversation_service, mock_db):
    # Arrange
    conversation_id = UUID(int=1)
    
    # Mock conversation to delete
    mock_conversation = Conversation(
        id=conversation_id,
        user_id=UUID(int=2),
        title="Test Conversation to Delete"
    )
    mock_db.get.return_value = mock_conversation
    
    # Act
    result = conversation_service.delete_conversation(mock_db, conversation_id)
    
    # Assert
    assert result is True
    mock_db.delete.assert_called_once_with(mock_conversation)