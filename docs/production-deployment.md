# Production Deployment Documentation: Todo AI Chatbot

## Overview
This document provides instructions for deploying the Todo AI Chatbot application to a production environment.

## Architecture
The Todo AI Chatbot consists of:
- **Backend**: FastAPI application with OpenAI integration
- **Frontend**: Next.js application with ChatKit integration
- **Database**: PostgreSQL (recommended: Neon Serverless)
- **Cache**: Redis (for caching frequently accessed data)
- **AI Service**: OpenAI API for natural language processing

## Prerequisites

### Infrastructure Requirements
- Container orchestration platform (Docker Compose, Kubernetes, etc.)
- PostgreSQL database instance
- Redis instance
- Domain name and SSL certificate
- Reverse proxy (nginx, Traefik, etc.)

### Environment Variables
Prepare the following environment variables for production:

#### Backend (.env)
```
DATABASE_URL=postgresql://username:password@host:port/dbname
SECRET_KEY=your-super-secret-and-long-key-change-this
OPENAI_API_KEY=your-openai-api-key
COHERE_API_KEY=your-cohere-api-key-if-using
REDIS_HOST=redis-hostname
REDIS_PORT=6379
REDIS_PASSWORD=redis-password-if-set
REDIS_DB=0
REDIS_CACHE_TTL=3600
DEBUG=false
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

#### Frontend (.env)
```
NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
NEXT_PUBLIC_APP_NAME="Todo AI Chatbot"
```

## Deployment Steps

### 1. Prepare the Codebase
```bash
# Clone the repository
git clone <repository-url>
cd todo-app-phase-3

# Ensure all dependencies are up-to-date
cd backend
pip install -r requirements.txt
cd ../frontend_new
npm install
```

### 2. Build Docker Images
```bash
# Build backend image
docker build -t todo-ai-chatbot-backend:latest -f backend/Dockerfile .

# Build frontend image (assuming you have a frontend Dockerfile)
docker build -t todo-ai-chatbot-frontend:latest -f frontend_new/Dockerfile .
```

### 3. Set Up Infrastructure
#### Option A: Using Docker Compose (Staging/Small Production)
```bash
# Create a production docker-compose.prod.yml
docker-compose -f docker-compose.prod.yml up -d
```

#### Option B: Using Kubernetes (Recommended for Production)
```bash
# Apply the production configuration
kubectl apply -f deploy/prod.yml

# Verify all pods are running
kubectl get pods -n todo-app
```

### 4. Database Setup
```bash
# Run database migrations
docker exec -it <backend-container> alembic upgrade head

# Or if using kubernetes:
kubectl exec -it <backend-pod> -n todo-app -- alembic upgrade head
```

### 5. SSL/HTTPS Configuration
Configure your reverse proxy or cloud provider to terminate SSL connections:
- Route `https://yourdomain.com` to the frontend
- Route `https://api.yourdomain.com` to the backend

### 6. Environment-Specific Configurations

#### For AWS ECS/Fargate:
- Use AWS Secrets Manager for sensitive data
- Use RDS for PostgreSQL
- Use ElastiCache for Redis
- Use Application Load Balancer with SSL termination

#### For Google Cloud Run:
- Use Secret Manager for sensitive data
- Use Cloud SQL for PostgreSQL
- Use Memorystore for Redis

#### For Azure Container Apps:
- Use Key Vault for sensitive data
- Use Azure Database for PostgreSQL
- Use Azure Cache for Redis

## Monitoring and Logging

### Health Checks
- `/health` - Basic health check
- `/status` - Detailed status information
- `/metrics` - System metrics (CPU, memory, etc.)

### Logging
- Application logs are written to stdout/stderr
- Configure your orchestrator to collect and forward logs
- Recommended: Centralized logging with ELK stack or similar

### Performance Monitoring
- Monitor response times for AI API calls
- Track database query performance
- Monitor cache hit rates
- Watch for rate limiting issues with AI providers

## Scaling Recommendations

### Horizontal Scaling
- Backend: Scale based on API request volume
- Frontend: Scale based on concurrent users
- Database: Scale read replicas based on read load
- Redis: Scale based on cache size and access patterns

### Vertical Scaling
- Backend: Increase CPU/memory for complex AI processing
- Database: Increase memory for better query performance
- Redis: Increase memory for larger cache capacity

## Security Considerations

### API Keys
- Store API keys in secrets management systems
- Rotate API keys regularly
- Use different keys for different environments

### Rate Limiting
- The application includes rate limiting (10 requests/minute per IP for chat)
- Monitor for abuse and adjust limits as needed

### Authentication
- JWT tokens with short expiration times
- Refresh token rotation
- Secure token storage on clients

### Network Security
- Restrict database access to application servers only
- Use private networks where possible
- Implement WAF if needed

## Backup and Recovery

### Database Backups
- Enable automated backups in your PostgreSQL provider
- Test backup restoration procedures regularly
- Consider point-in-time recovery options

### Application State
- The application is stateless (except for database)
- Code is stored in version control
- Configuration is managed via environment variables

## Maintenance Procedures

### Regular Tasks
- Monitor application logs for errors
- Check AI API usage and costs
- Review database performance metrics
- Update dependencies regularly

### Deployment Process
1. Deploy to staging environment first
2. Run integration tests
3. Perform manual QA if needed
4. Deploy to production
5. Monitor for issues post-deployment

### Rollback Procedure
1. Identify the problematic deployment
2. Revert to the previous stable version
3. Monitor application health
4. Investigate the issue in staging

## Troubleshooting

### Common Issues
- **AI API Timeout**: Check OpenAI API status, increase timeout values
- **Database Connection Issues**: Verify connection string, check connection pool settings
- **Cache Issues**: Restart Redis, clear cache if needed
- **High Memory Usage**: Check for memory leaks, tune garbage collection

### Diagnostic Commands
```bash
# Check application logs
docker logs <container-name>
kubectl logs <pod-name> -n todo-app

# Check system metrics
curl http://localhost:8000/metrics

# Check application health
curl http://localhost:8000/health
```

## Contact Information
- Development Team: [contact information]
- On-Call Support: [contact information]
- Issue Tracker: [link to issue tracker]

---

**Document Version**: 1.0  
**Last Updated**: January 2026  
**Next Review Date**: July 2026