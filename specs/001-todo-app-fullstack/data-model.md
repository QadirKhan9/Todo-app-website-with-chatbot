# Data Model: Todo Full-Stack Web Application

## Overview
This document defines the data models for the Todo Full-Stack Web Application, including entity definitions, relationships, and validation rules.

## Entity Definitions

### User
Represents a registered user with authentication credentials and account metadata.

**Fields**:
- `id` (UUID/Integer): Unique identifier for the user (Primary Key)
- `email` (String): User's email address (Required, Unique, Valid email format)
- `password_hash` (String): Hashed password for authentication (Required, Secure hash)
- `created_at` (DateTime): Timestamp when the account was created (Required, Auto-generated)
- `updated_at` (DateTime): Timestamp when the account was last updated (Required, Auto-updated)
- `is_active` (Boolean): Whether the account is active (Default: True)
- `last_login` (DateTime): Timestamp of last login (Optional)

**Validation Rules**:
- Email must be a valid email format
- Email must be unique across all users
- Password must meet security requirements (minimum length, complexity)
- Created_at and updated_at must be valid timestamps

**State Transitions**:
- Account created → Active
- Active → Suspended (admin action)
- Suspended → Active (admin action)

### Task
Represents a user's task with title, description, completion status, and ownership information.

**Fields**:
- `id` (UUID/Integer): Unique identifier for the task (Primary Key)
- `title` (String): Task title or subject (Required, Max 200 characters)
- `description` (Text): Detailed description of the task (Optional, Max 1000 characters)
- `is_completed` (Boolean): Whether the task is completed (Default: False)
- `created_at` (DateTime): Timestamp when the task was created (Required, Auto-generated)
- `updated_at` (DateTime): Timestamp when the task was last updated (Required, Auto-updated)
- `due_date` (DateTime): Optional deadline for the task (Optional)
- `priority` (Enum): Priority level (Low, Medium, High) (Default: Medium)
- `user_id` (UUID/Integer): Foreign key linking to the owning user (Required, Foreign Key)

**Validation Rules**:
- Title must be provided and not exceed 200 characters
- Description, if provided, must not exceed 1000 characters
- User_id must reference an existing, active user
- Due date, if set, must be a future date
- Priority must be one of the allowed values (Low, Medium, High)

**State Transitions**:
- Created → Active
- Active → Completed (when is_completed is set to True)
- Completed → Active (when is_completed is set to False)

## Relationships

### User → Task (One-to-Many)
- A User can own many Tasks
- A Task belongs to exactly one User
- Foreign Key: Task.user_id references User.id
- When a User is deleted, all their Tasks should also be deleted (Cascade Delete)

## Indexes

### User Entity
- Index on `email` (unique index for fast lookup during authentication)
- Index on `created_at` (for sorting and filtering by creation date)

### Task Entity
- Index on `user_id` (for efficient filtering by user)
- Index on `is_completed` (for filtering completed/incomplete tasks)
- Index on `created_at` (for chronological ordering)
- Index on `due_date` (for sorting by deadline)
- Composite index on `(user_id, is_completed)` (for efficient user-specific queries with completion status)

## Data Integrity Constraints

### Referential Integrity
- Task.user_id must reference an existing User.id
- Prevent orphaned tasks by implementing cascade delete

### Domain Constraints
- User.email must follow valid email format
- Task.priority must be one of the predefined values
- Task.due_date must be a future date when set

## Security Considerations

### Data Access
- Each user can only access their own tasks
- Backend must filter all queries by authenticated user ID
- API responses must only include tasks owned by the authenticated user

### Data Privacy
- User passwords must be stored as secure hashes (never plain text)
- Personal information should be encrypted at rest if required
- Audit trail for sensitive operations (deletions, updates)