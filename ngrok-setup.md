# Ngrok Setup Guide

## Prerequisites

1. **Ngrok Account** (free tier sufficient): https://ngrok.com/
2. **Ngrok Auth Token**: Get from https://dashboard.ngrok.com/get-started/your-authtoken

## Installation

### Option 1: Download Binary (Recommended)

```bash
# Linux/macOS
curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok

# macOS (via Homebrew)
brew install ngrok/ngrok/ngrok

# Or download directly from: https://ngrok.com/download
```

### Option 2: Docker (Optional)

```bash
docker pull ngrok/ngrok:latest
```

## Configuration

### 1. Set Ngrok Auth Token

```bash
# Set as environment variable (recommended)
export NGROK_AUTHTOKEN="your_ngrok_token_here"

# Or add to .env file (do NOT commit)
echo "NGROK_AUTHTOKEN=your_ngrok_token_here" >> .env
```

### 2. Create ngrok Configuration File (Optional)

Create `ngrok.yml` in backend directory:

```yaml
version: "2"
authtoken: ${NGROK_AUTHTOKEN}
tunnels:
  backend:
    addr: 8000
    proto: http
    bind_tls: true
```

## Usage

### Option A: Docker Container + Local Ngrok (Recommended)

**Step 1: Start Docker Container**

```bash
cd backend
docker-compose up -d
# Or manually: docker build -t hackathon-backend . && docker run -p 8000:8000 --env-file .env hackathon-backend
```

**Step 2: Expose via Ngrok**

```bash
# Simple command
ngrok http 8000

# Or with auth token
ngrok http 8000 --authtoken=${NGROK_AUTHTOKEN}
```

**Step 3: Get Public URL**

Ngrok will output:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:8000
```

Use `https://abc123.ngrok-free.app` in your Flutter app.

### Option B: Docker Compose + Ngrok Container (Advanced)

Add to `docker-compose.yml`:

```yaml
  ngrok:
    image: ngrok/ngrok:latest
    command: http backend:8000 --authtoken=${NGROK_AUTHTOKEN}
    depends_on:
      - backend
    ports:
      - "4040:4040"  # Ngrok web interface
    environment:
      - NGROK_AUTHTOKEN=${NGROK_AUTHTOKEN}
```

Then:
```bash
docker-compose up
# Access ngrok dashboard at http://localhost:4040
```

## Verification

### 1. Health Check

```bash
curl https://your-ngrok-url.ngrok-free.app/health
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

### 2. API Docs

Open in browser:
```
https://your-ngrok-url.ngrok-free.app/docs
```

### 3. Test API Endpoint

```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

## Flutter Integration

Update your Flutter app's base URL:

```dart
// lib/config/api_config.dart
class ApiConfig {
  // Development (local)
  static const String localBaseUrl = 'http://localhost:8000';
  
  // Ngrok (demo/testing)
  static const String ngrokBaseUrl = 'https://abc123.ngrok-free.app';
  
  // Use this for easy switching
  static const String baseUrl = kDebugMode 
    ? localBaseUrl 
    : ngrokBaseUrl;
}
```

## Security Notes

⚠️ **IMPORTANT**:

1. **Never commit `.env` file** with secrets
2. **Never share ngrok URLs publicly** (they expose your local backend)
3. **Use ngrok only for demos/testing** - not production
4. **Rotate ngrok tokens** if accidentally exposed
5. **Free ngrok URLs change on restart** - use ngrok agent for persistent URLs (paid)

## Troubleshooting

### Issue: "Ngrok tunnel not accessible"

- Verify Docker container is running: `docker ps`
- Check container logs: `docker logs hackathon-backend`
- Verify port 8000 is exposed: `curl http://localhost:8000/health`

### Issue: "Authentication failed"

- Verify `NGROK_AUTHTOKEN` is set: `echo $NGROK_AUTHTOKEN`
- Re-authenticate: `ngrok config add-authtoken YOUR_TOKEN`

### Issue: "CORS errors in Flutter"

- Ngrok URL must match CORS settings (currently `allow_origins=["*"]` in main.py)
- For production, configure specific origins

## Quick Reference

```bash
# Start Docker container
docker-compose up -d

# Start ngrok tunnel
ngrok http 8000

# View ngrok dashboard (if using ngrok web interface)
open http://localhost:4040

# Stop container
docker-compose down

# View logs
docker-compose logs -f backend
```
