# Data Model: Todo AI Chatbot

## Overview
This document defines the data models for the Todo AI Chatbot feature, including entities, relationships, and validation rules based on the functional requirements.

## Entity Models

### 1. User
Represents the system user with authentication and authorization details.

```python
class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(sa_column=Column(String, unique=True, index=True, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversations: List["Conversation"] = Relationship(back_populates="user")
    todos: List["Todo"] = Relationship(back_populates="user")
```

**Validation Rules**:
- Email must be valid and unique
- Created_at and updated_at timestamps are automatically managed

### 2. Conversation
Represents a sequence of exchanges between a user and the AI assistant.

```python
class Conversation(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(max_length=200)  # Auto-generated from first message or user-edited
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    openai_thread_id: str = Field(nullable=True)  # Thread ID in OpenAI's system
    
    # Relationships
    user: User = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")
```

**Validation Rules**:
- Must be associated with a valid user
- Title is auto-generated from first message if not provided by user
- Only one conversation can be active per user at a time (optional constraint)
- openai_thread_id is nullable until first interaction with OpenAI

### 3. Message
Represents an individual exchange within a conversation.

```python
class Message(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(foreign_key="conversation.id", nullable=False)
    role: str = Field(sa_column=Column(Enum("user", "assistant", name="message_role"), nullable=False))  # 'user' or 'assistant'
    content: str = Field(sa_column=Column(Text, nullable=False))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    message_type: str = Field(default="standard")  # 'standard', 'tool_call', 'tool_response'
    tool_calls: Optional[dict] = Field(default=None)  # Serialized tool call information if applicable
    tool_responses: Optional[dict] = Field(default=None)  # Serialized tool response information if applicable
    
    # Relationships
    conversation: Conversation = Relationship(back_populates="messages")
```

**Validation Rules**:
- Must be associated with a valid conversation
- Role must be either 'user' or 'assistant'
- Content cannot be empty
- If message_type is 'tool_call', tool_calls must be provided
- If message_type is 'tool_response', tool_responses must be provided

### 4. Todo
Represents a task item managed through the AI chatbot.

```python
class Todo(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id", nullable=False)
    title: str = Field(sa_column=Column(String, nullable=False))
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending", sa_column=Column(Enum("pending", "in_progress", "completed", name="todo_status")))
    priority: str = Field(default="medium", sa_column=Column(Enum("low", "medium", "high", name="todo_priority")))
    due_date: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Relationships
    user: User = Relationship(back_populates="todos")
```

**Validation Rules**:
- Must be associated with a valid user
- Title cannot be empty
- Status must be one of the defined enum values
- If status is 'completed', completed_at must be set
- If status is not 'completed', completed_at must be null

## Relationships

### User ↔ Conversation
- One-to-many relationship
- A user can have multiple conversations
- When a user is deleted, their conversations are also deleted (CASCADE)

### Conversation ↔ Message
- One-to-many relationship
- A conversation contains multiple messages
- When a conversation is deleted, its messages are also deleted (CASCADE)

### User ↔ Todo
- One-to-many relationship
- A user can have multiple todos
- When a user is deleted, their todos are also deleted (CASCADE)

## Indexes

### Performance Indexes
- User.email: Unique index for fast authentication lookups
- Conversation.user_id: Index for filtering conversations by user
- Message.conversation_id: Index for retrieving messages by conversation
- Todo.user_id: Index for filtering todos by user
- Todo.status: Index for filtering todos by status
- Todo.due_date: Index for sorting/filtering by due date

## Constraints

### Business Logic Constraints
- A user can only access their own conversations and todos
- Messages in a conversation are immutable after creation
- Todo status transitions follow specific rules (pending → in_progress → completed)
- Due dates cannot be in the past for completed todos

## API Contract Considerations

### Data Transfer Objects (DTOs)
For API operations, we'll use specialized DTOs that may differ slightly from the database models:

1. **CreateTodoRequest**: Contains only fields needed for creation (title, description, etc.)
2. **UpdateTodoRequest**: Contains only fields that can be updated (status, priority, etc.)
3. **ConversationResponse**: Includes messages with limited content for performance
4. **ChatRequest**: Contains user message and conversation context
5. **ChatResponse**: Contains AI response and any tool call information