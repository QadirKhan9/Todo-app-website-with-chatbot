# Quickstart Guide: Todo Full-Stack Web Application

## Overview
This guide provides instructions for setting up, developing, and running the Todo Full-Stack Web Application with secure authentication, persistent storage, and responsive frontend.

## Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- PostgreSQL-compatible database (Neon Serverless PostgreSQL recommended)
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
SECRET_KEY=your-super-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours (can be adjusted)
NEON_DATABASE_URL=your-neon-database-url
BETTER_AUTH_SECRET=your-better-auth-secret
```

**Frontend (.env.local):**
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000/api/auth
```

## Database Setup

### 1. Database Migration
Run the following command to set up your database schema:

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
alembic upgrade head
```

### 2. Initial Data (Optional)
If you need to seed the database with initial data:

```bash
python src/scripts/seed_data.py
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
1. Users register/login via the frontend
2. Better Auth handles credential validation and JWT token issuance
3. Frontend stores JWT token securely
4. All API requests include the JWT token in the Authorization header
5. Backend verifies the token and extracts user information
6. Backend filters data based on the authenticated user ID

## Troubleshooting

### Common Issues
- **Port already in use**: Change the port in the startup commands
- **Database connection errors**: Verify DATABASE_URL in the .env file
- **Authentication not working**: Check that BETTER_AUTH_SECRET matches between frontend and backend
- **CORS errors**: Ensure frontend and backend URLs are properly configured

### Resetting the Database
To reset the database to a clean state:
```bash
cd backend
alembic downgrade base
alembic upgrade head
```

## Deployment
For production deployment:
1. Set up SSL certificates
2. Configure environment variables for production
3. Set up a reverse proxy (e.g., Nginx)
4. Use a process manager (e.g., PM2 for Node.js, systemd for Python)
5. Set up monitoring and logging