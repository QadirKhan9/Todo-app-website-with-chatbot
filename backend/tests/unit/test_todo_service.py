import pytest
from unittest.mock import MagicMock
from src.services.todo_service import TodoService
from src.models.todo import Todo, TodoStatus, TodoPriority
from uuid import UUID


@pytest.fixture
def todo_service():
    return TodoService()


@pytest.fixture
def mock_db():
    return MagicMock()


def test_create_todo(todo_service, mock_db):
    # Arrange
    user_id = UUID(int=1)
    todo_data = {
        "title": "Test Todo",
        "description": "Test Description",
        "priority": "medium"
    }
    
    # Act
    result = todo_service.create_todo(mock_db, todo_data, str(user_id))
    
    # Assert
    assert result is not None
    assert result.title == "Test Todo"
    assert result.description == "Test Description"
    assert result.priority == TodoPriority.medium
    assert result.user_id == user_id


def test_get_todos(todo_service, mock_db):
    # Arrange
    user_id = UUID(int=1)
    mock_todos = [
        Todo(
            id=UUID(int=1),
            user_id=user_id,
            title="Test Todo 1",
            status=TodoStatus.pending,
            priority=TodoPriority.medium
        ),
        Todo(
            id=UUID(int=2),
            user_id=user_id,
            title="Test Todo 2",
            status=TodoStatus.completed,
            priority=TodoPriority.high
        )
    ]
    mock_db.exec.return_value.all.return_value = mock_todos
    
    # Act
    result = todo_service.get_todos(mock_db, str(user_id))
    
    # Assert
    assert len(result) == 2
    assert all(todo.user_id == user_id for todo in result)


def test_get_todo(todo_service, mock_db):
    # Arrange
    todo_id = UUID(int=1)
    user_id = UUID(int=2)
    
    # Mock todo in DB
    mock_todo = Todo(
        id=todo_id,
        user_id=user_id,
        title="Test Todo",
        status=TodoStatus.pending,
        priority=TodoPriority.medium
    )
    mock_db.get.return_value = mock_todo
    
    # Act
    result = todo_service.get_todo(mock_db, todo_id, str(user_id))
    
    # Assert
    assert result is not None
    assert result.id == todo_id
    assert result.user_id == user_id


def test_update_todo(todo_service, mock_db):
    # Arrange
    todo_id = UUID(int=1)
    user_id = UUID(int=2)
    update_data = {
        "title": "Updated Title",
        "status": "completed"
    }
    
    # Mock existing todo
    mock_existing_todo = Todo(
        id=todo_id,
        user_id=user_id,
        title="Original Title",
        status=TodoStatus.pending,
        priority=TodoPriority.medium
    )
    mock_db.get.return_value = mock_existing_todo
    
    # Act
    result = todo_service.update_todo(mock_db, todo_id, update_data, str(user_id))
    
    # Assert
    assert result is not None
    assert result.title == "Updated Title"
    assert result.status == TodoStatus.completed


def test_delete_todo(todo_service, mock_db):
    # Arrange
    todo_id = UUID(int=1)
    user_id = UUID(int=2)
    
    # Mock todo to delete
    mock_todo = Todo(
        id=todo_id,
        user_id=user_id,
        title="Test Todo to Delete",
        status=TodoStatus.pending,
        priority=TodoPriority.medium
    )
    mock_db.get.return_value = mock_todo
    
    # Act
    result = todo_service.delete_todo(mock_db, todo_id, str(user_id))
    
    # Assert
    assert result is True
    mock_db.delete.assert_called_once_with(mock_todo)


def test_mark_complete(todo_service, mock_db):
    # Arrange
    todo_id = UUID(int=1)
    user_id = UUID(int=2)
    
    # Mock existing todo
    mock_existing_todo = Todo(
        id=todo_id,
        user_id=user_id,
        title="Test Todo",
        status=TodoStatus.pending,
        priority=TodoPriority.medium
    )
    mock_db.get.return_value = mock_existing_todo
    
    # Act
    result = todo_service.mark_complete(mock_db, todo_id, str(user_id))
    
    # Assert
    assert result is not None
    assert result.status == TodoStatus.completed