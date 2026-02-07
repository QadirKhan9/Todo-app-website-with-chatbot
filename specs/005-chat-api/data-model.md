# Data Model: Chat API & Orchestration Layer

## Entities

### Conversation
Represents a chat session between a user and the AI agent, identified by a unique conversation_id.

**Fields**:
- id: UUID (primary key)
- conversation_id: String (unique identifier for the conversation)
- user_id: String (identifier for the user who owns this conversation)
- created_at: DateTime (timestamp when conversation was created)
- updated_at: DateTime (timestamp when conversation was last updated)
- title: String (optional, auto-generated title for the conversation)

**Validation rules**:
- conversation_id must be unique across all conversations
- user_id must be valid and authenticated
- created_at and updated_at are automatically managed

**State transitions**:
- Created when a new conversation is initiated
- Updated when new messages are added to the conversation

### Message
Represents a single communication unit in a conversation, containing sender, content, and timestamp.

**Fields**:
- id: UUID (primary key)
- conversation_id: String (foreign key referencing Conversation)
- role: String (sender role - 'user' or 'assistant')
- content: Text (the actual message content)
- timestamp: DateTime (when the message was created)
- metadata: JSON (optional, for storing additional data like tool calls)

**Validation rules**:
- conversation_id must reference an existing conversation
- role must be either 'user' or 'assistant'
- content must not be empty
- timestamp is automatically set when created

**State transitions**:
- Created when a new message is added to a conversation

### Agent Response
Represents the AI-generated response to a user message, potentially containing multiple content segments.

**Fields**:
- id: UUID (primary key)
- message_id: UUID (foreign key referencing the corresponding Message)
- content_segments: JSON (array of content segments in the response)
- finish_reason: String (reason why the agent stopped generating, e.g., 'stop', 'tool_calls')

**Validation rules**:
- message_id must reference an existing message with role 'user'
- content_segments must be a valid JSON array
- finish_reason must be one of the allowed values

### Tool Call
Represents an action initiated by the AI agent that requires external system interaction.

**Fields**:
- id: UUID (primary key)
- message_id: UUID (foreign key referencing the Message that triggered the tool call)
- tool_name: String (name of the tool to call)
- tool_input: JSON (input parameters for the tool)
- result: JSON (result returned by the tool)
- status: String (status of the tool call - 'pending', 'executed', 'failed')

**Validation rules**:
- message_id must reference an existing message
- tool_name must be a valid registered tool
- tool_input must be valid JSON
- status must be one of the allowed values

## Relationships

- Conversation (1) : Message (Many) - A conversation contains many messages
- Message (1) : Agent Response (0 or 1) - A message may have an associated agent response
- Message (1) : Tool Call (Many) - A message may trigger multiple tool calls
- User (1) : Conversation (Many) - A user may have many conversations