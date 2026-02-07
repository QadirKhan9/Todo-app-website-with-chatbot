# Data Model: Authentication & Authorization

## Overview
This document defines the data models for the authentication and authorization system of the Todo Full-Stack Web Application, including entity definitions and relationships.

## Entity Definitions

### User
Represents a registered user with authentication credentials and account metadata.

**Fields**:
- `id` (UUID/String): Unique identifier for the user (Primary Key)
- `email` (String): User's email address (Required, Unique, Valid email format)
- `password_hash` (String): Hashed password for authentication (Required, Secure hash)
- `created_at` (DateTime): Timestamp when the account was created (Required, Auto-generated)
- `updated_at` (DateTime): Timestamp when the account was last updated (Required, Auto-updated)
- `is_active` (Boolean): Whether the account is active (Default: True)
- `last_login` (DateTime): Timestamp of last login (Optional)
- `email_verified` (Boolean): Whether the email has been verified (Default: False)

**Validation Rules**:
- Email must be a valid email format
- Email must be unique across all users
- Password must meet security requirements (minimum length, complexity)
- Created_at and updated_at must be valid timestamps

**State Transitions**:
- Account created → Active
- Active → Suspended (admin action)
- Suspended → Active (admin action)

### JWT Token (Conceptual)
Represents the JWT token structure containing user identity information and authentication claims.

**Claims**:
- `sub` (Subject): User identifier (user_id)
- `exp` (Expiration): Token expiration timestamp
- `iat` (Issued At): Token creation timestamp
- `jti` (JWT ID): Unique identifier for the token (optional, for revocation)
- `user_id` (Custom Claim): User identifier (redundant with sub but explicit)
- `email` (Custom Claim): User's email address
- `permissions` (Custom Claim): User permissions (if needed)

**Validation Rules**:
- Token must not be expired at time of verification
- Signature must be valid using shared secret
- User referenced in token must exist and be active
- Token must not be in revocation list (if implemented)

## Relationships

### User → Sessions (One-to-Many - Conceptual)
- A User can have multiple concurrent sessions (tokens)
- Each JWT token represents a session
- When a user logs out, tokens may be added to a blacklist (optional)

## Security Considerations

### Data Access
- User passwords must be stored as secure hashes (never plain text)
- JWT tokens should not contain sensitive information beyond identification
- Token payloads should be kept minimal to reduce exposure

### Token Security
- Use strong signing algorithm (HS256 or RS256)
- Set appropriate expiration times (7 days as specified)
- Implement token refresh mechanisms for extended sessions
- Consider implementing token blacklisting for enhanced security