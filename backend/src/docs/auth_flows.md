"""
Authentication System Documentation
===============================

SIGNUP FLOW
-----------

1. User sends POST request to /api/v1/auth/signup with:
   - email (valid email format)
   - password (min 8 chars, with uppercase, lowercase, digit, special char)

2. System validates input using Pydantic schema

3. System checks if user with email already exists

4. If email is unique, password is hashed using bcrypt

5. New user record is created in database with:
   - Unique UUID identifier
   - Hashed password
   - is_active = True
   - email_verified = False
   - Timestamps

6. Returns 201 Created with user info (excluding password)


LOGIN FLOW
----------

1. User sends POST request to /api/v1/auth/login with:
   - email
   - password

2. System retrieves user by email from database

3. System verifies password using bcrypt comparison

4. If credentials are valid:
   - Creates JWT access token (expires in 30 minutes)
   - Creates JWT refresh token (expires in 7 days)
   - Both tokens contain user ID and email

5. Returns tokens to client

6. If credentials invalid, returns 401 Unauthorized


ERROR HANDLING
--------------

- Duplicate email during signup → 409 Conflict
- Invalid credentials during login → 401 Unauthorized
- Invalid token → 401 Unauthorized
- Expired token → 401 Unauthorized
- Malformed request → 422 Unprocessable Entity
- Server errors → 500 Internal Server Error
"""