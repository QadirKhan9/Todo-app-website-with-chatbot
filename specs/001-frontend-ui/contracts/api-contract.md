# API Contracts: Frontend UI & Integration

## Overview
This document defines the API contracts for the Frontend UI & Integration of the Todo Full-Stack Web Application, specifying endpoints, request/response formats, authentication requirements, and error handling from the frontend perspective.

## Base URL
```
https://api.todoapp.com/v1
```
*Note: During development, this will be replaced with the appropriate localhost or staging URL.*

## Authentication
All API endpoints require authentication using JWT tokens issued by Better Auth.

### Authentication Header
```
Authorization: Bearer <JWT_TOKEN>
```

### Token Handling
- Frontend will automatically attach JWT token to all API requests
- Token will be retrieved from auth context/state
- Requests will be made with proper authentication headers

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": { /* response data */ },
  "message": "Optional success message"
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {} // Optional additional error details
  }
}
```

## API Endpoints

### 1. Authentication Endpoints

#### POST /auth/signup
Register a new user account with Better Auth.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "created_at": "2023-01-01T00:00:00Z"
    },
    "token": "jwt-token-string"
  },
  "message": "Account created successfully"
}
```

**Validation**:
- Email must be valid format
- Password must meet security requirements
- Email must be unique

**Errors**:
- 400: Invalid input data
- 409: Email already exists

#### POST /auth/login
Authenticate user and return JWT token.

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "created_at": "2023-01-01T00:00:00Z"
    },
    "token": "jwt-token-string"
  },
  "message": "Login successful"
}
```

**Errors**:
- 400: Invalid input data
- 401: Invalid credentials

#### POST /auth/logout
Logout user and invalidate session.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

### 2. Task Management Endpoints

#### GET /users/{user_id}/tasks
Retrieve all tasks for the authenticated user.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user whose tasks to retrieve (must match authenticated user)

**Query Parameters**:
- `completed` (optional): Filter by completion status (true/false)
- `priority` (optional): Filter by priority (low, medium, high)
- `limit` (optional): Number of tasks to return (default: 20, max: 100)
- `offset` (optional): Number of tasks to skip (for pagination)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": "uuid-string",
        "title": "Task title",
        "description": "Task description",
        "is_completed": false,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T00:00:00Z",
        "due_date": "2023-01-10T00:00:00Z",
        "priority": "medium"
      }
    ],
    "pagination": {
      "total": 100,
      "limit": 20,
      "offset": 0
    }
  }
}
```

**Errors**:
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (trying to access another user's tasks)
- 404: User not found

#### POST /users/{user_id}/tasks
Create a new task for the authenticated user.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user creating the task (must match authenticated user)

**Request Body**:
```json
{
  "title": "New task title",
  "description": "Task description (optional)",
  "due_date": "2023-01-10T00:00:00Z (optional)",
  "priority": "medium (optional, default: medium)"
}
```

**Response (201 Created)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "uuid-string",
      "title": "New task title",
      "description": "Task description (optional)",
      "is_completed": false,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z",
      "due_date": "2023-01-10T00:00:00Z",
      "priority": "medium",
      "user_id": "uuid-string"
    }
  },
  "message": "Task created successfully"
}
```

**Validation**:
- Title is required and must not exceed 200 characters
- Description, if provided, must not exceed 1000 characters
- Due date, if provided, must be a future date
- Priority must be one of: low, medium, high

**Errors**:
- 400: Invalid input data
- 401: Unauthorized
- 403: Forbidden (trying to create task for another user)

#### GET /users/{user_id}/tasks/{task_id}
Get a specific task for the authenticated user.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user (must match authenticated user)
- `task_id`: The ID of the task to retrieve

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "uuid-string",
      "title": "Task title",
      "description": "Task description",
      "is_completed": false,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-01T00:00:00Z",
      "due_date": "2023-01-10T00:00:00Z",
      "priority": "medium",
      "user_id": "uuid-string"
    }
  }
}
```

**Errors**:
- 401: Unauthorized
- 403: Forbidden (trying to access another user's task)
- 404: Task not found

#### PUT /users/{user_id}/tasks/{task_id}
Update an existing task for the authenticated user.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user (must match authenticated user)
- `task_id`: The ID of the task to update

**Request Body**:
```json
{
  "title": "Updated task title (optional)",
  "description": "Updated task description (optional)",
  "due_date": "2023-01-10T00:00:00Z (optional)",
  "priority": "high (optional)"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "uuid-string",
      "title": "Updated task title",
      "description": "Updated task description",
      "is_completed": false,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z",
      "due_date": "2023-01-10T00:00:00Z",
      "priority": "high",
      "user_id": "uuid-string"
    }
  },
  "message": "Task updated successfully"
}
```

**Errors**:
- 400: Invalid input data
- 401: Unauthorized
- 403: Forbidden (trying to update another user's task)
- 404: Task not found

#### DELETE /users/{user_id}/tasks/{task_id}
Delete a task for the authenticated user.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user (must match authenticated user)
- `task_id`: The ID of the task to delete

**Response (200 OK)**:
```json
{
  "success": true,
  "message": "Task deleted successfully"
}
```

**Errors**:
- 401: Unauthorized
- 403: Forbidden (trying to delete another user's task)
- 404: Task not found

#### PATCH /users/{user_id}/tasks/{task_id}/complete
Toggle the completion status of a task for the authenticated user.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user (must match authenticated user)
- `task_id`: The ID of the task to update

**Request Body**:
```json
{
  "is_completed": true
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "task": {
      "id": "uuid-string",
      "title": "Task title",
      "description": "Task description",
      "is_completed": true,
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z",
      "due_date": "2023-01-10T00:00:00Z",
      "priority": "medium",
      "user_id": "uuid-string"
    }
  },
  "message": "Task completion status updated"
}
```

**Errors**:
- 400: Invalid input data
- 401: Unauthorized
- 403: Forbidden (trying to update another user's task)
- 404: Task not found

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTH_001 | 401 | Invalid or expired token |
| AUTH_002 | 401 | Invalid credentials |
| AUTH_003 | 403 | Insufficient permissions |
| VALIDATION_001 | 400 | Invalid input format |
| VALIDATION_002 | 400 | Missing required field |
| RESOURCE_001 | 404 | Resource not found |
| RESOURCE_002 | 409 | Resource conflict (e.g., duplicate email) |
| SERVER_001 | 500 | Internal server error |

## Frontend Integration Requirements

### API Client Responsibilities
1. Automatically attach Authorization header with JWT token
2. Handle token expiration and refresh if needed
3. Transform API responses to frontend data models
4. Handle network errors gracefully
5. Provide loading states during API requests
6. Implement retry mechanisms for failed requests

### Authentication Flow Integration
1. Store JWT token securely after successful authentication
2. Include token in all subsequent API requests
3. Redirect to login page on 401 responses
4. Clear token on logout or token expiration
5. Handle concurrent session scenarios

### Task Management Integration
1. Filter tasks by authenticated user ID
2. Validate that user can only modify their own tasks
3. Update UI state after successful API operations
4. Handle optimistic updates where appropriate
5. Show appropriate loading and error states