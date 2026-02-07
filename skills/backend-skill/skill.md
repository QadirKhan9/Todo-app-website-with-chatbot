---
name: backend-skill
description: Generate backend routes, handle requests/responses, and connect to databases efficiently. Use for building server-side functionality.
---

# Backend Development Skill

## Instructions

1. **Route Creation**
   - Define RESTful endpoints
   - Use proper HTTP methods (GET, POST, PUT, DELETE)
   - Organize routes by feature/module

2. **Request & Response Handling**
   - Validate incoming requests
   - Send structured JSON responses
   - Handle errors with appropriate status codes

3. **Database Connectivity**
   - Establish secure connections
   - Perform CRUD operations
   - Use ORM/Query builder or raw SQL as needed

## Best Practices
- Keep route names clear and consistent
- Return meaningful error messages
- Use middleware for authentication/validation
- Separate concerns (routes, controllers, services, models)
- Sanitize inputs to prevent SQL injection

## Example Structure
```javascript
// routes/userRoutes.js
const express = require('express');
const { getUser, createUser } = require('../controllers/userController');
const router = express.Router();

router.get('/users/:id', getUser);
router.post('/users', createUser);

module.exports = router;
