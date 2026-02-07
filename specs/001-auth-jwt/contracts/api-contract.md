# API Contracts: Authentication & Authorization

## Overview
This document defines the API contracts for the authentication and authorization functionality of the Todo Full-Stack Web Application, specifying endpoints, request/response formats, authentication requirements, and error handling.

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

### Token Verification
- Backend will verify JWT signature using shared secret (BETTER_AUTH_SECRET)
- Token expiration will be checked
- User ID will be extracted from token payload
- Requests will be authorized based on user ID in token

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

### 2. Protected Endpoints (Require Authentication)

#### GET /users/{user_id}/profile
Retrieve user profile information.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user whose profile to retrieve (must match authenticated user)

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "user@example.com",
      "created_at": "2023-01-01T00:00:00Z",
      "updated_at": "2023-01-02T00:00:00Z"
    }
  }
}
```

**Errors**:
- 401: Unauthorized (invalid/expired token)
- 403: Forbidden (trying to access another user's profile)
- 404: User not found

#### PUT /users/{user_id}/profile
Update user profile information.

**Headers**:
```
Authorization: Bearer <JWT_TOKEN>
```

**Path Parameters**:
- `user_id`: The ID of the user to update (must match authenticated user)

**Request Body**:
```json
{
  "email": "newemail@example.com"
}
```

**Response (200 OK)**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid-string",
      "email": "newemail@example.com",
      "updated_at": "2023-01-02T00:00:00Z"
    }
  },
  "message": "Profile updated successfully"
}
```

**Errors**:
- 400: Invalid input data
- 401: Unauthorized
- 403: Forbidden (trying to update another user's profile)
- 404: User not found

## Authorization Enforcement

### Cross-User Access Prevention
All endpoints that accept a `{user_id}` parameter must validate that:
- The authenticated user's ID (from JWT) matches the `{user_id}` in the path
- If IDs don't match, return HTTP 403 Forbidden
- Example: If JWT contains user_id="abc123" but path is `/users/xyz789/profile`, reject the request

### Unauthenticated Request Handling
- If no Authorization header is present, return HTTP 401 Unauthorized
- If Authorization header is malformed, return HTTP 401 Unauthorized
- If JWT token is invalid or expired, return HTTP 401 Unauthorized

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| AUTH_001 | 401 | Invalid or expired token |
| AUTH_002 | 401 | Invalid credentials |
| AUTH_003 | 403 | Insufficient permissions / Cross-user access attempt |
| VALIDATION_001 | 400 | Invalid input format |
| VALIDATION_002 | 400 | Missing required field |
| RESOURCE_001 | 404 | Resource not found |
| RESOURCE_002 | 409 | Resource conflict (e.g., duplicate email) |
| SERVER_001 | 500 | Internal server error |

## Security Requirements

1. All endpoints require valid JWT authentication
2. Users can only access their own resources (user_id in token must match user_id in path)
3. Input validation must be performed on all requests
4. Rate limiting should be implemented to prevent brute force attacks
5. Sensitive data should not be exposed in error messages
6. JWT tokens must be verified using the shared BETTER_AUTH_SECRET
7. Token expiration must be validated on each request