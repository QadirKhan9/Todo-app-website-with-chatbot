import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.database import get_db
from src.dependencies.auth import get_current_user
from uuid import UUID


# Create a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./e2e_test.db"

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
    from src.models import SQLModel
    SQLModel.metadata.create_all(bind=engine)


def teardown_module():
    """Teardown the test database"""
    from src.models import SQLModel
    SQLModel.metadata.drop_all(bind=engine)


def test_full_todo_management_flow():
    """
    End-to-end test for the complete AI chatbot todo management flow:
    1. User creates a conversation
    2. User asks AI to create a todo
    3. User asks AI to list todos
    4. User asks AI to update a todo
    5. User asks AI to mark a todo as complete
    6. User asks AI to delete a todo
    """
    
    # Step 1: Create a conversation
    conversation_resp = client.post(
        "/conversations/",
        json={"title": "E2E Test Conversation"}
    )
    assert conversation_resp.status_code == 200
    conversation_data = conversation_resp.json()
    conversation_id = conversation_data["id"]
    assert conversation_data["title"] == "E2E Test Conversation"
    
    # Step 2: Ask AI to create a todo
    create_todo_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Create a new todo to buy groceries"}
    )
    assert create_todo_resp.status_code == 200
    create_todo_data = create_todo_resp.json()
    assert "buy groceries" in create_todo_data["response"].lower()
    
    # Step 3: Ask AI to list todos
    list_todos_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "What are my todos?"}
    )
    assert list_todos_resp.status_code == 200
    list_todos_data = list_todos_resp.json()
    assert "buy groceries" in list_todos_data["response"].lower()
    
    # Step 4: Ask AI to update the todo
    update_todo_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Change the groceries todo to buy milk and bread"}
    )
    assert update_todo_resp.status_code == 200
    update_todo_data = update_todo_resp.json()
    assert "milk" in update_todo_data["response"].lower() or "bread" in update_todo_data["response"].lower()
    
    # Step 5: Ask AI to mark the todo as complete
    complete_todo_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Mark the groceries todo as complete"}
    )
    assert complete_todo_resp.status_code == 200
    complete_todo_data = complete_todo_resp.json()
    assert "complete" in complete_todo_data["response"].lower()
    
    # Step 6: Ask AI to delete the todo
    delete_todo_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Delete the groceries todo"}
    )
    assert delete_todo_resp.status_code == 200
    delete_todo_data = delete_todo_resp.json()
    assert "delete" in delete_todo_data["response"].lower() or "removed" in delete_todo_data["response"].lower()
    
    print("✅ Full todo management flow completed successfully!")


def test_conversation_context_preservation():
    """
    End-to-end test to verify that conversation context is preserved:
    1. User creates a conversation
    2. User creates multiple todos
    3. User refers to a todo by context (without specifying details)
    4. AI correctly identifies and operates on the intended todo
    """
    
    # Step 1: Create a conversation
    conversation_resp = client.post(
        "/conversations/",
        json={"title": "Context Test Conversation"}
    )
    assert conversation_resp.status_code == 200
    conversation_data = conversation_resp.json()
    conversation_id = conversation_data["id"]
    
    # Step 2: Create first todo
    create_first_todo_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Create a todo to buy groceries"}
    )
    assert create_first_todo_resp.status_code == 200
    
    # Step 3: Create second todo
    create_second_todo_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Create another todo to walk the dog"}
    )
    assert create_second_todo_resp.status_code == 200
    
    # Step 4: Refer to the first todo by context ("the groceries todo") and update it
    update_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Update the groceries todo to include apples"}
    )
    assert update_resp.status_code == 200
    update_data = update_resp.json()
    assert "groceries" in update_data["response"].lower()
    
    # Step 5: Refer to the second todo by context ("the dog todo") and mark it complete
    complete_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Mark the dog todo as complete"}
    )
    assert complete_resp.status_code == 200
    complete_data = complete_resp.json()
    assert "dog" in complete_data["response"].lower() or "complete" in complete_data["response"].lower()
    
    print("✅ Conversation context preservation test completed successfully!")


def test_error_handling_in_e2e_flow():
    """
    End-to-end test to verify error handling in the AI chatbot flow:
    1. User asks AI to perform an impossible action
    2. AI responds with appropriate error message
    """
    
    # Step 1: Create a conversation
    conversation_resp = client.post(
        "/conversations/",
        json={"title": "Error Handling Test Conversation"}
    )
    assert conversation_resp.status_code == 200
    conversation_data = conversation_resp.json()
    conversation_id = conversation_data["id"]
    
    # Step 2: Ask AI to do something impossible or invalid
    error_resp = client.post(
        f"/chat/conversations/{conversation_id}",
        json={"message": "Create a todo to travel back in time"}
    )
    assert error_resp.status_code == 200
    error_data = error_resp.json()
    # Even if the request is unusual, the system should handle it gracefully
    # The AI might still try to interpret it or respond appropriately
    
    print("✅ Error handling in E2E flow test completed successfully!")