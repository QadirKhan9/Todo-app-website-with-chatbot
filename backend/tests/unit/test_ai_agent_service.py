import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.ai_agent_service import AIAgentService
from src.models.todo import Todo
from src.services.todo_service import TodoService
from src.services.conversation_service import ConversationService
from src.utils.mcp_tool_handler import MCPToolHandler
from uuid import UUID


@pytest.fixture
def mock_todo_service():
    service = MagicMock(spec=TodoService)
    return service


@pytest.fixture
def mock_conversation_service():
    service = MagicMock(spec=ConversationService)
    return service


@pytest.fixture
def mock_tool_handler():
    handler = MagicMock(spec=MCPToolHandler)
    return handler


@pytest.fixture
def ai_agent_service(mock_todo_service, mock_conversation_service, mock_tool_handler):
    service = AIAgentService()
    service.todo_service = mock_todo_service
    service.conversation_service = mock_conversation_service
    service.tool_handler = mock_tool_handler
    return service


@pytest.mark.asyncio
async def test_process_user_message_creates_todo(ai_agent_service, mock_todo_service):
    # Arrange
    db = MagicMock()
    user_id = "user-123"
    conversation_id = "conv-123"
    message = "Create a todo to buy groceries"
    
    # Mock conversation
    mock_conversation = MagicMock()
    mock_conversation.id = UUID(int=1)
    ai_agent_service.conversation_service.get_conversation.return_value = mock_conversation
    
    # Mock todo creation
    mock_todo = Todo(
        id=UUID(int=2),
        user_id=UUID(int=1),
        title="buy groceries",
        status="pending",
        priority="medium"
    )
    mock_todo_service.create_todo.return_value = mock_todo
    
    # Act
    result = await ai_agent_service.process_user_message(db, user_id, conversation_id, message)
    
    # Assert
    assert result["response"] is not None
    assert result["action_taken"]["type"] == "tool_execution"
    mock_todo_service.create_todo.assert_called_once()


@pytest.mark.asyncio
async def test_process_user_message_gets_todos(ai_agent_service, mock_todo_service):
    # Arrange
    db = MagicMock()
    user_id = "user-123"
    conversation_id = "conv-123"
    message = "Show me my todos"
    
    # Mock conversation
    mock_conversation = MagicMock()
    mock_conversation.id = UUID(int=1)
    ai_agent_service.conversation_service.get_conversation.return_value = mock_conversation
    
    # Mock todos retrieval
    mock_todos = [
        Todo(
            id=UUID(int=1),
            user_id=UUID(int=1),
            title="Test todo",
            status="pending",
            priority="medium"
        )
    ]
    mock_todo_service.get_todos.return_value = mock_todos
    
    # Act
    result = await ai_agent_service.process_user_message(db, user_id, conversation_id, message)
    
    # Assert
    assert result["response"] is not None
    mock_todo_service.get_todos.assert_called_once_with(db, user_id)


@pytest.mark.asyncio
async def test_execute_create_todo(ai_agent_service, mock_todo_service):
    # Arrange
    db = MagicMock()
    user_id = "user-123"
    args = {
        "title": "Test todo",
        "description": "Test description",
        "priority": "high"
    }
    
    # Mock todo creation
    mock_todo = Todo(
        id=UUID(int=2),
        user_id=UUID(int=1),
        title="Test todo",
        description="Test description",
        status="pending",
        priority="high"
    )
    mock_todo_service.create_todo.return_value = mock_todo
    
    # Act
    result = await ai_agent_service._execute_create_todo(db, user_id, args)
    
    # Assert
    assert result["success"] is True
    assert result["message"] == f"Created todo: {mock_todo.title}"
    mock_todo_service.create_todo.assert_called_once()


@pytest.mark.asyncio
async def test_execute_get_todos(ai_agent_service, mock_todo_service):
    # Arrange
    db = MagicMock()
    user_id = "user-123"
    
    # Mock todos retrieval
    mock_todos = [
        Todo(
            id=UUID(int=1),
            user_id=UUID(int=1),
            title="Test todo",
            status="pending",
            priority="medium"
        )
    ]
    mock_todo_service.get_todos.return_value = mock_todos
    
    # Act
    result = await ai_agent_service._execute_get_todos(db, user_id)
    
    # Assert
    assert result["success"] is True
    assert result["count"] == 1
    assert len(result["todos"]) == 1
    mock_todo_service.get_todos.assert_called_once_with(db, user_id)