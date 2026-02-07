# Data Model: Frontend UI & Integration

## Overview
This document defines the data models for the Frontend UI & Integration of the Todo Full-Stack Web Application, focusing on the frontend representation of entities and their relationships in the UI context.

## Entity Definitions

### User
Represents a registered user with authentication credentials and account metadata as used in the frontend application.

**Fields**:
- `id` (string): Unique identifier for the user
- `email` (string): User's email address (Required, Valid email format)
- `authStatus` (enum): Authentication status (unauthenticated, authenticating, authenticated, error)
- `token` (string): JWT token for authenticated requests (Optional, only when authenticated)
- `isLoading` (boolean): Whether authentication state is loading (Default: false)
- `error` (string): Error message if authentication failed (Optional)

**Validation Rules**:
- Email must be a valid email format
- Token, if present, must be a valid JWT format
- AuthStatus must be one of the defined enum values

**State Transitions**:
- Unauthenticated → Authenticating (on login/signup attempt)
- Authenticating → Authenticated (on successful authentication)
- Authenticating → Error (on authentication failure)
- Authenticated → Unauthenticated (on logout)

### Task
Represents a user's task with title, description, completion status, and ownership information as used in the frontend application.

**Fields**:
- `id` (string): Unique identifier for the task
- `title` (string): Task title or subject (Required, Max 200 characters)
- `description` (string): Detailed description of the task (Optional, Max 1000 characters)
- `isCompleted` (boolean): Whether the task is completed (Default: false)
- `createdAt` (string/Date): Timestamp when the task was created (Required, ISO string format)
- `updatedAt` (string/Date): Timestamp when the task was last updated (Required, ISO string format)
- `dueDate` (string/Date): Optional deadline for the task (Optional, ISO string format)
- `priority` (enum): Priority level (low, medium, high) (Default: medium)
- `userId` (string): ID of the user who owns this task (Required, matches authenticated user)

**Validation Rules**:
- Title must be provided and not exceed 200 characters
- Description, if provided, must not exceed 1000 characters
- UserId must match the authenticated user's ID
- Due date, if set, must be a future date
- Priority must be one of the allowed values (low, medium, high)

**State Transitions**:
- Created → Active
- Active → Completed (when isCompleted is set to true)
- Completed → Active (when isCompleted is set to false)

## UI State Models

### AuthState
Represents the authentication state in the frontend application.

**Fields**:
- `user` (User | null): The currently authenticated user (null if unauthenticated)
- `isLoading` (boolean): Whether authentication state is loading (Default: false)
- `error` (string | null): Error message if authentication failed (Default: null)
- `isAuthenticated` (boolean): Whether a user is currently authenticated (Default: false)

### TaskState
Represents the task management state in the frontend application.

**Fields**:
- `tasks` (Task[]): List of tasks for the authenticated user (Default: [])
- `isLoading` (boolean): Whether tasks are loading (Default: false)
- `error` (string | null): Error message if task operations failed (Default: null)
- `currentTask` (Task | null): Currently selected task for editing (Default: null)

## Relationships

### User → Task (One-to-Many)
- A User can own many Tasks
- A Task belongs to exactly one User
- Frontend validation: All tasks displayed must belong to the authenticated user
- API validation: Backend ensures user can only access their own tasks

## Frontend-Specific Considerations

### Loading States
- Each major operation should have corresponding loading indicators
- Implement skeleton screens for better perceived performance
- Show appropriate loading states during API calls

### Error States
- Handle API errors gracefully with user-friendly messages
- Implement retry mechanisms for failed operations
- Show global error notifications for important failures

### Form States
- Track form validation states separately
- Implement real-time validation where appropriate
- Handle form submission states (idle, submitting, success, error)

## Type Definitions (TypeScript)

```typescript
type AuthStatus = 'unauthenticated' | 'authenticating' | 'authenticated' | 'error';

interface User {
  id: string;
  email: string;
  authStatus: AuthStatus;
  token?: string;
  isLoading: boolean;
  error?: string;
}

interface Task {
  id: string;
  title: string;
  description?: string;
  isCompleted: boolean;
  createdAt: string; // ISO date string
  updatedAt: string; // ISO date string
  dueDate?: string; // ISO date string
  priority: 'low' | 'medium' | 'high';
  userId: string;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  isAuthenticated: boolean;
}

interface TaskState {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  currentTask: Task | null;
}
```

## Security Considerations

### Data Access
- Frontend must only display tasks that belong to the authenticated user
- JWT token must be validated before making API requests
- Sensitive user information should not be stored unnecessarily in frontend state

### Token Handling
- JWT tokens should be stored securely (consider httpOnly cookies vs localStorage)
- Token expiration should be handled gracefully
- Automatic token refresh mechanisms should be implemented
- Tokens should be cleared on logout