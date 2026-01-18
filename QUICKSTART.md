# Quick Start Guide - Docker + Ngrok

## One-Command Setup

```bash
cd backend
./docker-start.sh
```

This will:
1. Create `.env` file if missing
2. Build Docker image
3. Start container
4. Verify health check

## Manual Docker Setup

### 1. Create `.env` file

```bash
cat > .env << EOF
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hackathon_db
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_ENV=production
EOF
```

### 2. Start with Docker Compose

```bash
docker-compose up --build
```

### 3. Verify

```bash
curl http://localhost:8000/health
```

## Expose with Ngrok

### 1. Install Ngrok

```bash
# macOS
brew install ngrok/ngrok/ngrok

# Linux (download from https://ngrok.com/download)
```

### 2. Get Auth Token

1. Sign up at https://ngrok.com/
2. Get token from https://dashboard.ngrok.com/get-started/your-authtoken

### 3. Expose Backend

```bash
# Set token (one time)
ngrok config add-authtoken YOUR_TOKEN

# Expose port 8000
ngrok http 8000
```

### 4. Use Ngrok URL in Flutter

Copy the HTTPS URL from ngrok output (e.g., `https://abc123.ngrok-free.app`) and use it in your Flutter app.

## Common Commands

```bash
# Start container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop container
docker-compose down

# Restart container
docker-compose restart

# Rebuild and restart
docker-compose up --build -d
```

## URLs

- **Local API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Ngrok Dashboard** (if using ngrok web): http://localhost:4040

## Troubleshooting

**Port already in use?**
```bash
# Use different port
docker run -p 8001:8000 --env-file .env hackathon-backend
```

**MongoDB not connecting?**
- Verify MongoDB is running: `mongosh` or check MongoDB service
- Check `MONGODB_URL` in `.env`
- For remote MongoDB, ensure network access

**Container keeps restarting?**
```bash
# Check logs
docker-compose logs backend
```

## Full Documentation

- **Docker Setup**: See `DOCKER.md`
- **Ngrok Setup**: See `ngrok-setup.md`
- **API Documentation**: http://localhost:8000/docs (when running)
