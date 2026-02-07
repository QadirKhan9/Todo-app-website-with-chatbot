# API Contract: Chat API & Orchestration Layer

## Overview
This document defines the API contracts for the Chat API & Orchestration Layer. The API provides a stateless HTTP interface for chat functionality, allowing the frontend to interact with the AI agent while maintaining conversation context.

## Base URL
```
https://api.example.com/v1
```

## Authentication
All endpoints require authentication via JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Endpoints

### POST /chat
Send a message to the AI agent and receive a response.

#### Request
```json
{
  "user_id": "string",
  "conversation_id": "string (optional)",
  "message": "string (required)",
  "metadata": "object (optional)"
}
```

#### Response
```json
{
  "conversation_id": "string",
  "message_id": "string",
  "response": {
    "role": "assistant",
    "content": "string",
    "tool_calls": [
      {
        "id": "string",
        "type": "function",
        "function": {
          "name": "string",
          "arguments": "string (JSON)"
        }
      }
    ]
  },
  "timestamp": "ISO 8601 datetime"
}
```

#### Error Responses
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: User not authorized for this conversation
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

### GET /conversations/{conversation_id}
Retrieve conversation history.

#### Request
```
GET /conversations/{conversation_id}
Authorization: Bearer {jwt_token}
```

#### Response
```json
{
  "conversation_id": "string",
  "messages": [
    {
      "id": "string",
      "role": "string (user|assistant)",
      "content": "string",
      "timestamp": "ISO 8601 datetime",
      "tool_calls": [...],
      "tool_call_results": [...]
    }
  ],
  "created_at": "ISO 8601 datetime",
  "updated_at": "ISO 8601 datetime"
}
```

#### Error Responses
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: User not authorized for this conversation
- `404 Not Found`: Conversation does not exist
- `500 Internal Server Error`: Server error

### POST /conversations
Start a new conversation.

#### Request
```json
{
  "user_id": "string",
  "initial_message": "string (optional)"
}
```

#### Response
```json
{
  "conversation_id": "string",
  "message_id": "string (if initial_message was provided)",
  "response": {
    "role": "assistant",
    "content": "string",
    "tool_calls": [...]
  },
  "timestamp": "ISO 8601 datetime"
}
```

#### Error Responses
- `400 Bad Request`: Invalid request format
- `401 Unauthorized`: Missing or invalid authentication
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

## Common Error Format
All error responses follow this format:
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (optional)"
  }
}
```

## Data Types

### Message Role
Enum: `"user" | "assistant"`

### Tool Call
```json
{
  "id": "string",
  "type": "function",
  "function": {
    "name": "string",
    "arguments": "string (JSON)"
  }
}
```

### Timestamp Format
All timestamps use ISO 8601 format: `YYYY-MM-DDTHH:mm:ss.sssZ`