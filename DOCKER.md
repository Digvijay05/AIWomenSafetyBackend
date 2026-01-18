# Docker Setup Guide

## Quick Start

### Prerequisites

- Docker installed (https://docs.docker.com/get-docker/)
- Docker Compose installed (usually bundled with Docker Desktop)
- Environment variables configured (see below)

### 1. Environment Variables

Create `.env` file in `backend/` directory:

```env
# MongoDB (adjust if your MongoDB is remote)
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hackathon_db

# JWT Configuration (CHANGE THESE IN PRODUCTION)
SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Environment
APP_ENV=production
```

**⚠️ IMPORTANT**: Never commit `.env` file to version control!

### 2. Build and Run

**Option A: Using Docker Compose (Recommended)**

```bash
cd backend
docker-compose up --build
```

**Option B: Using Docker directly**

```bash
cd backend

# Build image
docker build -t hackathon-backend .

# Run container
docker run -p 8000:8000 --env-file .env hackathon-backend
```

### 3. Verify

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs
```

## Docker Commands

### Build Image

```bash
docker build -t hackathon-backend .
```

### Run Container

```bash
docker run -p 8000:8000 --env-file .env hackathon-backend
```

### Run in Detached Mode

```bash
docker run -d -p 8000:8000 --name hackathon-backend --env-file .env hackathon-backend
```

### View Logs

```bash
# Docker Compose
docker-compose logs -f backend

# Docker directly
docker logs -f hackathon-backend
```

### Stop Container

```bash
# Docker Compose
docker-compose down

# Docker directly
docker stop hackathon-backend
docker rm hackathon-backend
```

### Execute Commands in Container

```bash
docker exec -it hackathon-backend /bin/bash
```

## Docker Compose Commands

```bash
# Start services
docker-compose up

# Start in detached mode
docker-compose up -d

# Rebuild and start
docker-compose up --build

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View logs
docker-compose logs -f

# Restart service
docker-compose restart backend
```

## Environment Variables

All environment variables are passed from `.env` file or directly via `-e` flag:

```bash
docker run -p 8000:8000 \
  -e MONGODB_URL=mongodb://localhost:27017 \
  -e SECRET_KEY=your-secret-key \
  hackathon-backend
```

### Required Variables

- `MONGODB_URL`: MongoDB connection string (e.g., `mongodb://localhost:27017` or remote MongoDB URI)
- `DATABASE_NAME`: Database name (default: `hackathon_db`)
- `SECRET_KEY`: JWT secret key (generate with: `openssl rand -hex 32`)

### Optional Variables

- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `APP_ENV`: Environment (default: production)

## Health Check

The container includes a health check that pings `/health` endpoint:

```bash
# Check health status
docker ps
# Look for "healthy" status in STATUS column

# Manual health check
curl http://localhost:8000/health
```

Expected response:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected"
  },
  "error": null
}
```

## Troubleshooting

### Issue: "Port 8000 already in use"

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Use different port
docker run -p 8001:8000 --env-file .env hackathon-backend
```

### Issue: "MongoDB connection failed"

- Verify MongoDB is running and accessible
- Check `MONGODB_URL` in `.env`
- If MongoDB is in another container, use Docker network

### Issue: "Container exits immediately"

```bash
# Check logs
docker logs hackathon-backend

# Common causes:
# - Missing environment variables
# - Python syntax errors
# - Import errors
```

### Issue: "Module not found"

- Verify `app/` directory is copied correctly
- Check Dockerfile COPY commands
- Rebuild image: `docker-compose build --no-cache`

## Production Considerations

1. **Use specific Python version**: Already locked to `python:3.11-slim`
2. **Multi-stage builds**: Not implemented (not needed for hackathon)
3. **Non-root user**: Consider for production
4. **Resource limits**: Set in docker-compose.yml if needed
5. **Health checks**: Already implemented

## Integration with Ngrok

See `ngrok-setup.md` for exposing the container via ngrok for Flutter testing.
