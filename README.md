# Hackathon Backend API

> ⚠️ **Python 3.11.x is required. Other versions are unsupported.**

This is a FastAPI backend for the PDPU Hackathon Flutter application.

## Features

- User authentication with JWT tokens
- User registration and login
- MongoDB integration with Motor (async)
- CORS enabled for frontend communication
- Health check endpoints
- Docker-ready setup

## Requirements

- Python 3.11.x (**Python 3.12+ and 3.13 are NOT supported**)
- MongoDB (local or remote)

## Quick Start (Docker) - Recommended for Hackathon

For quick setup and ngrok exposure, use Docker:

```bash
cd backend

# Create .env file (if not exists)
cp .env.example .env  # Edit with your MongoDB URL and secrets

# One-command start
./docker-start.sh

# Or manually
docker-compose up --build
```

The backend will be available at `http://localhost:8000`

**For ngrok exposure**, see `ngrok-setup.md`

---

## Setup Instructions (Local Development)

1. **Install Python 3.11**:
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.11 python3.11-venv python3.11-dev
   
   # Arch Linux
   sudo pacman -S python311
   
   # macOS with Homebrew
   brew install python@3.11
   ```

2. **Run the application**:
   ```bash
   ./run.sh
   ```

   This script will:
   - Create a virtual environment with Python 3.11
   - Install dependencies
   - Start the application

3. **Alternative manual setup**:
   ```bash
   # Create virtual environment with Python 3.11
   python3.11 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python main.py
   ```

4. **Configure environment variables in `.env`**:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DATABASE_NAME=hackathon_db
   SECRET_KEY=your_secret_key_here_for_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

## API Endpoints

### Authentication
- `POST /api/users/register` - Register a new user
- `POST /api/users/login` - Login and get JWT token

### User Management
- `GET /api/users/me` - Get current user info (requires authentication)

### Health Check
- `GET /health` - Application health status
- `GET /` - Basic alive check

## Development

The application follows a modular structure:
- `main.py` - Entry point and app initialization
- `app/api/routes/` - API route definitions
- `app/core/` - Core functionality (database, security)
- `app/crud/` - Database operations
- `app/models/` - Data models and schemas
- `app/schemas/` - Pydantic validation schemas

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URL | MongoDB connection string | mongodb://localhost:27017 |
| DATABASE_NAME | MongoDB database name | hackathon_db |
| SECRET_KEY | JWT secret key | your_secret_key_here_for_jwt |
| ALGORITHM | JWT algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Token expiration time | 30 |

## Notes for Demo Day

- Ensure MongoDB is running before starting the application
- For cloud MongoDB, update `MONGODB_URL` in `.env`
- The application handles database connection failures gracefully
- All API responses follow a consistent format with `success`, `data`, and `error` fields

## Python Version Enforcement

This project strictly requires Python 3.11.x:
- Runtime version checking prevents execution on other versions
- All dependencies are pinned for Python 3.11 compatibility
- Virtual environment creation enforces Python 3.11 usage

## Frontend Integration

For Flutter developers integrating with this backend:

- **Frontend Integration Guide**: See [Frontend Integration Guide](FRONTEND_INTEGRATION_GUIDE.md)
 for comprehensive integration documentation
- All APIs are JSON-only (no form-data or multipart)
- Backend makes autonomous safety decisions based on telemetry
- Frontend sends data and receives decisions/actions
- JWT authentication required for all protected endpoints

Quick links:
- Authentication: JSON-only register/login endpoints
- Journey lifecycle: Start → Telemetry → End
- Risk analysis: Backend evaluates and returns risk assessments
- Decision engine: Backend automatically escalates alerts when needed

## Extending the API

To add new features:
1. Create new models in `app/models/`
2. Add CRUD operations in `app/crud/`
3. Define routes in `app/api/routes/`
4. Follow the existing patterns for consistency
