# Quickstart Guide: Todo AI Chatbot

## Overview
This guide provides a quick introduction to setting up and running the Todo AI Chatbot feature.

## Prerequisites
- Python 3.11+
- Node.js 18+ (for frontend)
- OpenAI API key
- PostgreSQL-compatible database (Neon recommended)
- Better Auth configured for authentication

## Environment Setup

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
   
   Required environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `DATABASE_URL`: PostgreSQL connection string
   - `JWT_SECRET`: Secret for JWT token verification
   - `BETTER_AUTH_SECRET`: Secret for Better Auth

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the backend server:
   ```bash
   uvicorn src.api.main:app --reload --port 8000
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend_new
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Start the development server:
   ```bash
   npm run dev
   ```

## Key Components

### Backend Structure
```
backend/
├── src/
│   ├── models/           # Data models (SQLModel)
│   ├── services/         # Business logic
│   │   ├── ai_agent_service.py
│   │   ├── conversation_service.py
│   │   └── todo_service.py
│   ├── api/
│   │   ├── routes/
│   │   │   ├── chat.py
│   │   │   └── todos.py
│   │   └── main.py      # FastAPI app entry point
│   └── utils/
│       ├── mcp_tool_handler.py
│       └── auth.py
└── tests/
```

### Frontend Structure
```
frontend_new/
├── src/
│   ├── components/
│   │   └── ChatKitIntegration.jsx
│   ├── pages/
│   │   └── TodoChatPage.jsx
│   └── services/
│       └── apiClient.js
└── tests/
```

## Running Tests

### Backend Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_todo_service.py

# Run with coverage
pytest --cov=src
```

### Frontend Tests
```bash
# Run all tests
npm test

# Run end-to-end tests
npm run test:e2e
```

## API Endpoints

### Chat Operations
- `POST /users/{user_id}/conversations/{conversation_id}/chat` - Process user message
- `GET /users/{user_id}/conversations/{conversation_id}/messages` - Get conversation messages

### Conversation Management
- `POST /users/{user_id}/conversations` - Create new conversation
- `GET /users/{user_id}/conversations` - Get user's conversations
- `PUT /users/{user_id}/conversations/{conversation_id}` - Update conversation

### Todo Operations
- `GET /users/{user_id}/todos` - Get user's todos
- `POST /users/{user_id}/todos` - Create new todo
- `PUT /users/{user_id}/todos/{todo_id}` - Update todo
- `DELETE /users/{user_id}/todos/{todo_id}` - Delete todo

## Key Features

### 1. Natural Language Processing
The AI agent processes natural language input to identify todo-related intents (create, read, update, delete).

Example: "Add a task to buy groceries" → Creates a new todo with title "buy groceries"

### 2. Conversation Context
The system maintains conversation context across individual requests to enable coherent dialog.

### 3. Frontend Integration
Seamless integration with OpenAI ChatKit for a smooth user experience.

## Troubleshooting

### Common Issues
1. **OpenAI API errors**: Verify your API key is correct and has sufficient quota
2. **Database connection errors**: Check your DATABASE_URL is properly formatted
3. **Authentication errors**: Ensure JWT_SECRET matches your Better Auth configuration
4. **CORS errors**: Verify frontend URL is in the backend's CORS allowed origins

### Debugging Tips
- Enable debug logging by setting `DEBUG=true` in your environment
- Check the backend logs for detailed error messages
- Use browser developer tools to inspect API requests and responses