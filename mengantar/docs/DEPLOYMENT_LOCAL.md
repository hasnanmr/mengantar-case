# Deployment Guide - Local Docker Setup

## Quick Start

### Prerequisites
- Docker installed (`docker --version`)
- Docker Compose installed (`docker-compose --version`)
- OpenRouter API key

### Step 1: Configure Environment

Copy `.env.example` and fill in your API keys:

```bash
cd backend
cp .env.example .env
# Edit .env with your API keys
```

Required values in `.env`:
```env
OPENROUTER_API_KEY=your_key_here
HF_TOKEN=your_token_here
```

Optional (for tracing):
```env
LANGFUSE_SECRET_KEY=your_secret_key
LANGFUSE_PUBLIC_KEY=your_public_key
```

### Step 2: Start Services

From the project root directory:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

### Step 3: Verify Services

```bash
# Check all services are running
docker-compose ps

# View backend logs
docker-compose logs -f backend

# Test backend health
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/

# Test frontend (should return HTML)
curl http://localhost:3000
```

## Available Services

| Service | Container Name | Port | Description |
|---------|---------------|------|-------------|
| PostgreSQL | mengantar-postgres | 5432 | Database |
| Backend | acne-care-backend | 8000 | FastAPI API |
| Frontend | acne-care-frontend | 3000 | Next.js App |

## Environment Configuration

### API URL Configuration

The frontend is configured to connect to the backend:

**Default (Docker):** `http://localhost:8000`

This is set in `docker-compose.yaml`:
```yaml
frontend:
  environment:
    - NEXT_PUBLIC_API_URL=http://localhost:8000
```

### CORS Configuration

CORS origins are configured via the `cors_origins` setting in `.env`:

```env
cors_origins=["http://localhost:3000","http://127.0.0.1:3000","http://frontend:3000"]
```

For production, update this to include your production domain:
```env
cors_origins=["http://localhost:3000","https://yourdomain.com","https://www.yourdomain.com"]
```

### Logging Configuration

Set log level via `.env`:

```env
LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Environment Type

Set the environment type:

```env
APP_ENVIRONMENT=staging  # Options: development, staging, production
```

## Common Commands

### Start Services
```bash
docker-compose up
docker-compose up -d  # Detached mode
docker-compose up --build  # Rebuild images
```

### Stop Services
```bash
docker-compose down          # Stop and remove containers
docker-compose down -v       # Also remove volumes (data lost!)
docker-compose stop          # Stop without removing
docker-compose start         # Start stopped containers
```

### View Logs
```bash
docker-compose logs          # All services
docker-compose logs -f       # Follow logs
docker-compose logs backend  # Specific service
```

### Execute Commands in Container
```bash
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres -d postgres
```

### Run Migrations
```bash
# Migrations run automatically on startup
# To run manually:
docker-compose exec backend uv run alembic upgrade head
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Missing .env file - create from .env.example
# 2. Invalid API keys - verify in .env
# 3. Port already in use - stop other services on port 8000/3000/5432
```

### Database Connection Failed

```bash
# Check postgres is healthy
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify DATABASE_URL in .env for Docker:
# DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
# Note: use 'postgres' as hostname (Docker service name)
```

### Frontend Can't Connect to Backend

```bash
# Verify backend is running
docker-compose ps backend

# Check API URL in frontend is correct:
# NEXT_PUBLIC_API_URL=http://localhost:8000

# Check backend is accessible:
curl http://localhost:8000/health
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Clear Everything and Start Fresh

```bash
docker-compose down -v
docker-compose up --build
```

## Production Notes

For production deployment, consider:

1. **Use production API URLs** in frontend config
2. **Add production CORS origins** to your domain
3. **Set up secrets management** (AWS Secrets Manager, Vault, etc.)
4. **Configure HTTPS** (use a reverse proxy like Nginx or Traefik)
5. **Set up monitoring and alerting**
6. **Configure database backups**
7. **Add rate limiting** to API endpoints
8. **Set up proper logging aggregation** (ELK stack, Datadog, etc.)

## Development Tips

### Hot Reloading for Backend

For development, you can mount the backend directory as a volume:

```yaml
# docker-compose.override.yaml
backend:
  volumes:
    - ./backend:/app
    - ./backend/.env:/app/.env
  command: uv run fastapi dev /app/main.py
```

### Access Database Directly

```bash
docker exec -it mengantar-postgres psql -U postgres -d postgres
psql -h localhost -U postgres -d postgres
```

### Reset Database

```bash
docker-compose down -v
docker-compose up
```
