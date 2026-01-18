# backend/main.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from app.api.routes import router as api_router
from app.core.exception_handler import http_exception_handler, validation_exception_handler
from app.utils.audit_logger import init_audit_logger
from fastapi.exceptions import RequestValidationError
from fastapi import Request

# Create FastAPI app instance
app = FastAPI(
    title="Hackathon Backend API",
    description="Backend API for PDPU Hackathon Flutter App",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_DETAILS = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = None

@app.on_event("startup")
async def startup_db_client():
    global client
    try:
        client = AsyncIOMotorClient(MONGO_DETAILS)
        app.mongodb = client[DATABASE_NAME]
        print(f"Connected to MongoDB at {MONGO_DETAILS}")
        
        # Initialize audit logger
        await init_audit_logger(app.mongodb)
        print("Audit logger initialized")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Running in limited mode without database connection")

@app.on_event("shutdown")
async def shutdown_db_client():
    if client:
        client.close()
        print("Disconnected from MongoDB")

# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "Hackathon Backend API is running!"}

# Health check endpoint
@app.get("/health")
async def health_check():
    db_status = "connected" if client else "disconnected"
    if not client:
        db_status = "not configured - set MONGODB_URL in .env"
    
    return {
        "success": True,
        "data": {
            "status": "healthy",
            "database": db_status
        },
        "error": None
    }

# Register exception handlers for JSON envelope format
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Include API routes
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
