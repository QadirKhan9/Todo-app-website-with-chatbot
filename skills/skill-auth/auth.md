---
name: auth-skill
description: Handle user authentication flows including signup, signin, password hashing, JWT token generation, and Better Auth integration.
---

# Auth Skill – User Authentication

## Instructions

1. **Signup**
   - Collect user email and password
   - Hash passwords securely before storing
   - Validate email format and password strength
   - Save user in database or Better Auth service

2. **Signin**
   - Verify email exists
   - Compare hashed password with input
   - Generate JWT token on successful login
   - Return token to the client for authentication

3. **Password Hashing**
   - Use secure hashing algorithm (e.g., bcrypt)
   - Apply proper salt rounds (recommended 10–12)
   - Never store plaintext passwords

4. **JWT Tokens**
   - Generate tokens with user ID payload
   - Sign with secret key from environment
   - Set expiration for token validity
   - Verify tokens on protected routes

5. **Better Auth Integration**
   - Connect to Better Auth using API keys
   - Sync user signup/signin flows
   - Use Better Auth for session management
   - Handle errors and edge cases

## Best Practices
- Never log sensitive data
- Use HTTPS for all requests
- Keep JWT secrets safe in `.env`
- Validate input and sanitize user data
- Modularize auth functions for reusability

## Example Structure (Node.js / Express)
```javascript
// signup.js
import bcrypt from "bcrypt";
import { addUser } from "./betterAuth.js";

export async function signup(req, res) {
  const { email, password } = req.body;
  const hashed = await bcrypt.hash(password, 10);
  const user = await addUser({ email, password: hashed });
  res.json({ message: "User created", userId: user.id });
}

// signin.js
import bcrypt from "bcrypt";
import jwt from "jsonwebtoken";
import { getUser } from "./betterAuth.js";

export async function signin(req, res) {
  const { email, password } = req.body;
  const user = await getUser(email);
  if (!user) return res.status(404).json({ error: "User not found" });

  const match = await bcrypt.compare(password, user.password);
  if (!match) return res.status(401).json({ error: "Invalid credentials" });

  const token = jwt.sign({ id: user.id }, process.env.JWT_SECRET, { expiresIn: "1h" });
  res.json({ message: "Logged in", token });
}
