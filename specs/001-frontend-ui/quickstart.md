# Quickstart Guide: Todo Full-Stack Web Application

## Overview
This guide provides instructions for setting up, developing, and running the Todo Full-Stack Web Application with secure authentication, persistent storage, and responsive frontend.

## Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- Git
- Package managers: npm/yarn/pnpm for frontend, pip for backend

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Backend Setup
Navigate to the backend directory and install dependencies:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Frontend Setup
Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

### 4. Environment Variables
Create `.env` files in both backend and frontend directories:

**Backend (.env):**
```env
DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080  # 7 days (7 * 24 * 60 minutes)
BETTER_AUTH_SECRET=your-better-auth-secret
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000/api/auth
```

## Running the Application

### 1. Start the Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn src.main:app --reload --port 8000
```

The backend API will be available at `http://localhost:8000`.

### 2. Start the Frontend
In a new terminal window:
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## API Documentation
Once the backend is running, API documentation is available at:
- Interactive docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## Development Workflow

### Backend Development
1. Make changes to Python files in the `src/` directory
2. The server will automatically reload due to the `--reload` flag
3. Run tests: `pytest`

### Frontend Development
1. Make changes to React components in the `src/` directory
2. The development server will automatically reload
3. Run tests: `npm test`

### Running Tests

#### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

#### Frontend Tests
```bash
cd frontend
npm test
```

## Building for Production

### Backend
```bash
cd backend
# Ensure all dependencies are installed
pip install -r requirements.txt
# Run migrations
alembic upgrade head
# Deploy with a production WSGI server like Gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
cd frontend
npm run build
# Serve the build directory with a web server like Nginx
npm start  # For testing the production build locally
```

## Authentication Flow
1. Users register/login via the frontend using Better Auth
2. Better Auth handles credential validation and JWT token issuance
3. Frontend stores JWT token securely
4. All API requests include the JWT token in the Authorization header
5. Backend verifies the token and extracts user information
6. Backend enforces user-level access control to prevent cross-user access

## Troubleshooting

### Common Issues
- **Port already in use**: Change the port in the startup commands
- **Invalid token errors**: Check that BETTER_AUTH_SECRET matches between frontend and backend
- **CORS errors**: Ensure frontend and backend URLs are properly configured
- **Cross-user access errors**: Verify that the user_id in the JWT matches the user_id in the API path

### Token Verification Issues
- Ensure the JWT algorithm matches between frontend and backend (HS256)
- Verify that the secret key is identical in both environments
- Check that token expiration is handled correctly

### Authorization Issues
- Verify that the user_id in the JWT payload matches the user_id in the API path
- Check that all protected endpoints have proper authentication middleware
- Ensure that 401 and 403 responses are handled correctly in the frontend

## Security Best Practices

### Token Management
- Store JWT tokens securely (preferably in httpOnly cookies)
- Implement token refresh mechanisms for extended sessions
- Set appropriate expiration times (7 days as specified)
- Never log JWT tokens in application logs

### Input Validation
- Validate all user inputs on both frontend and backend
- Sanitize inputs to prevent injection attacks
- Validate JWT tokens on every protected endpoint

### Error Handling
- Don't expose sensitive information in error messages
- Log security events without storing sensitive data
- Implement rate limiting to prevent brute force attacks