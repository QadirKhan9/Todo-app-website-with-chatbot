import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db
from src.models import SQLModel
from src.dependencies.auth import get_current_user
from uuid import UUID


# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency override for database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Dependency override for authentication
def override_get_current_user():
    # Return a mock user for testing
    class MockUser:
        id = UUID(int=1)
        email = "test@example.com"
    return MockUser()


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


client = TestClient(app)


def setup_module():
    """Setup the test database"""
    SQLModel.metadata.create_all(bind=engine)


def teardown_module():
    """Teardown the test database"""
    SQLModel.metadata.drop_all(bind=engine)


def test_chat_endpoint():
    """Test the chat endpoint"""
    response = client.post(
        "/chat/",
        json={"message": "Create a todo to buy groceries"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data
    assert "message_id" in data


def test_create_conversation():
    """Test creating a conversation"""
    response = client.post(
        "/conversations/",
        json={"title": "Test Conversation"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert data["title"] == "Test Conversation"


def test_get_conversations():
    """Test getting conversations"""
    response = client.get("/conversations/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_specific_conversation():
    """Test getting a specific conversation by creating one first"""
    # Create a conversation first
    create_response = client.post(
        "/conversations/",
        json={"title": "Specific Test Conversation"}
    )
    assert create_response.status_code == 200
    created_conv = create_response.json()
    conv_id = created_conv["id"]
    
    # Now get the specific conversation
    response = client.get(f"/conversations/{conv_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == conv_id
    assert data["title"] == "Specific Test Conversation"


def test_update_conversation():
    """Test updating a conversation"""
    # Create a conversation first
    create_response = client.post(
        "/conversations/",
        json={"title": "Original Title"}
    )
    assert create_response.status_code == 200
    created_conv = create_response.json()
    conv_id = created_conv["id"]
    
    # Update the conversation
    response = client.put(
        f"/conversations/{conv_id}",
        json={"title": "Updated Title", "is_active": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["is_active"] is False


def test_get_conversation_messages():
    """Test getting messages for a conversation"""
    # Create a conversation first
    create_response = client.post(
        "/conversations/",
        json={"title": "Conversation for Messages"}
    )
    assert create_response.status_code == 200
    created_conv = create_response.json()
    conv_id = created_conv["id"]
    
    # Get messages for the conversation
    response = client.get(f"/conversations/{conv_id}/messages")
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "messages" in data
    assert data["conversation_id"] == conv_id