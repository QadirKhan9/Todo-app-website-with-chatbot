# Data Model: Todo AI Chatbot – MCP Server Tools

## Overview
This document defines the data models required for the MCP server that exposes task operations as tools.

## Entity Models

### Task
Represents a user's task with properties for tracking and management.

**Fields**:
- `id` (UUID): Unique identifier for the task
- `title` (str): Title of the task (required, max 255 chars)
- `description` (str): Detailed description of the task (optional, max 1000 chars)
- `status` (str): Current status of the task (enum: "pending", "completed", default: "pending")
- `user_id` (UUID): Foreign key linking to the user who owns the task
- `created_at` (datetime): Timestamp when the task was created
- `updated_at` (datetime): Timestamp when the task was last updated

**Validation Rules**:
- Title must not be empty
- Status must be one of the allowed values
- User_id must reference a valid user
- Cannot be deleted if user_id is invalid

**Relationships**:
- Belongs to one User (many-to-one)
- Each user can have many tasks

### User
Represents a system user with unique identifier for authentication.

**Fields**:
- `id` (UUID): Unique identifier for the user
- `email` (str): User's email address (unique, required)
- `created_at` (datetime): Timestamp when the user was registered
- `updated_at` (datetime): Timestamp when user info was last updated

**Validation Rules**:
- Email must be a valid email format
- Email must be unique across all users

**Relationships**:
- Has many Tasks (one-to-many)

## State Transitions

### Task Status Transitions
- `pending` → `completed` (via complete_task tool)
- `completed` → `pending` (via update_task tool)

## Database Schema

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## Indexes

- Index on `tasks.user_id` for efficient user-scoped queries
- Index on `tasks.status` for efficient status-based queries
- Composite index on `(user_id, status)` for common combined queries