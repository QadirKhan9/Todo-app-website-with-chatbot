# Chat API & Orchestration Layer

This is a thin, stateless HTTP layer that connects the frontend UI with the AI Agent and MCP tools. The API accepts chat messages from the frontend, loads and persists conversation context, invokes the AI agent with correct state, and relays agent responses back to the frontend while maintaining statelessness per request.

## Features

- Stateless API design that maintains conversation context
- Integration with OpenAI agents
- Tool call handling for external operations
- User authentication and conversation ownership
- Comprehensive logging and error handling

## Prerequisites

- Python 3.11+
- OpenAI API key
- Access to Neon Serverless PostgreSQL (optional, SQLite used by default)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Copy the environment file and add your API keys:
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key and other secrets
   ```

## Running the Application

1. Activate your virtual environment
2. Run the application:
   ```bash
   cd backend
   uvicorn src.main:app --reload --port 8000
   ```

The API will be available at `http://localhost:8000`.

## API Endpoints

- `POST /v1/chat` - Send a message to the AI agent
- `GET /v1/conversations/{conversation_id}` - Retrieve conversation history
- `POST /v1/conversations` - Start a new conversation
- `GET /health` - Health check endpoint

## Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - Database connection string (defaults to SQLite)
- `JWT_SECRET_KEY` - Secret key for JWT token signing
- `MCP_SERVER_URL` - URL for the MCP server (for tool calls)

## Architecture

The application follows a layered architecture:

- **API Layer** (`src/api/`) - Handles HTTP requests and responses
- **Service Layer** (`src/services/`) - Implements business logic
- **Model Layer** (`src/models/`) - Defines data structures
- **Database Layer** (`src/db/`) - Handles database operations
- **Utilities** (`src/utils/`) - Common utilities and error handling
- **Configuration** (`src/config/`) - Application settings

## Development

To run tests:
```bash
cd backend
pytest
```

To format code:
```bash
cd backend
black .
```

To lint code:
```bash
cd backend
ruff check .
```