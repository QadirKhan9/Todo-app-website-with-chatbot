# Quickstart Guide: Todo AI Chatbot – MCP Server Tools

## Overview
This guide provides instructions for setting up and running the MCP server that exposes task operations as tools.

## Prerequisites
- Python 3.11+
- pip package manager
- Access to Neon Serverless PostgreSQL database
- Environment variables configured (see below)

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure the following environment variables in `.env`:
   ```
   DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require
   SECRET_KEY=your-super-secret-key-here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## Installation

1. Install Python dependencies:
   ```bash
   pip install fastapi sqlmodel python-multipart python-jose[cryptography] passlib[bcrypt] psycopg2-binary uvicorn python-mcp-sdk
   ```

2. For development, also install:
   ```bash
   pip install pytest httpx python-dotenv
   ```

## Running the Server

1. Start the MCP server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. The server will start on `http://localhost:8000`

## Connecting an AI Client

To connect an AI client to the MCP server:

1. The server exposes the following tools:
   - `add_task`: Create a new task
   - `list_tasks`: Retrieve user's tasks
   - `complete_task`: Mark a task as completed
   - `update_task`: Modify task details
   - `delete_task`: Remove a task

2. Each tool requires authentication via JWT token in the request headers

## Testing the Tools

You can test the tools using curl or a REST client:

```bash
# Example: Add a task
curl -X POST http://localhost:8000/tools/add_task \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "description": "This is a test"}'
```

## Database Migrations

To initialize the database:

1. Run the initialization script:
   ```bash
   python init_db.py
   ```

This will create the necessary tables for users and tasks.

## Development

1. The main server code is in `main.py`
2. Database models are in `models.py`
3. Tool implementations are in `tools.py`
4. Authentication utilities are in `auth.py`

## Troubleshooting

- If you get database connection errors, verify your Neon PostgreSQL connection string
- If authentication fails, ensure your JWT token is valid and properly formatted
- Check the server logs for detailed error information