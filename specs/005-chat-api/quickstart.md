# Quickstart Guide: Chat API & Orchestration Layer

## Overview
This guide provides a quick introduction to setting up and using the Chat API & Orchestration Layer.

## Prerequisites
- Python 3.11+
- pip package manager
- Access to Neon Serverless PostgreSQL database
- OpenAI API key
- MCP server access

## Setup

### 1. Environment Configuration
Create a `.env` file with the following variables:
```bash
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=your_neon_database_url
MCP_SERVER_URL=your_mcp_server_url
JWT_SECRET_KEY=your_jwt_secret_key
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn sqlmodel openai python-jose[cryptography] python-multipart
```

### 3. Database Setup
Run the following command to initialize the database:
```bash
# This would typically be a migration command
python -m backend.src.models.init_db
```

## Running the Service

### Development
```bash
uvicorn backend.src.main:app --reload --port 8000
```

### Production
```bash
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Starting a New Conversation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_id": "user123",
    "message": "Hello, how can you help me today?"
  }'
```

### Continuing an Existing Conversation
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "user_id": "user123",
    "conversation_id": "conv456",
    "message": "Can you help me with my todo list?"
  }'
```

### Retrieving Conversation History
```bash
curl -X GET http://localhost:8000/conversations/conv456 \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Key Components

### Models
- `Conversation`: Manages conversation state and metadata
- `Message`: Stores individual messages in a conversation
- `ToolCall`: Tracks AI agent tool invocations

### Services
- `ConversationService`: Handles conversation lifecycle
- `AIAgentService`: Orchestrates AI agent interactions
- `ToolExecutionService`: Manages MCP tool calls

### API Routes
- `/chat`: Main endpoint for chat interactions
- `/conversations/{id}`: Retrieve conversation history
- `/conversations`: Create new conversations

## Architecture Notes

### Statelessness
Each request contains all necessary context. The API loads conversation history from the database for each request rather than maintaining server-side sessions.

### Tool Integration
When the AI agent requests to use an MCP tool:
1. The API detects the tool call request
2. Forwards the tool call to the MCP server
3. Receives results from the MCP server
4. Continues AI agent execution with tool results
5. Returns final response to the frontend

### Security
- All requests require JWT authentication
- Conversation access is limited to the owning user
- Input validation prevents injection attacks