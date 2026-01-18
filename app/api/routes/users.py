# app/api/routes/users.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional
from datetime import timedelta
import os
from dotenv import load_dotenv
from jose import jwt

from app.core.database import get_database
from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.core.security import verify_password, create_access_token
from app.crud.user import create_user, get_user, get_user_by_id

load_dotenv()

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Validate token and return current user
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id: str = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=dict)
async def register_user(user: UserCreate, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Register a new user
    """
    try:
        user_response = await create_user(db, user)
        return {
            "success": True,
            "data": {
                "user": user_response,
                "message": "User registered successfully"
            },
            "error": None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while registering the user"
        )

@router.post("/login", response_model=dict)
async def login_user(user_login: UserLogin, db: AsyncIOMotorDatabase = Depends(get_database)):
    """
    Authenticate user and return JWT token using JSON instead of form data
    """
    # Get user by email
    user = await get_user(db, user_login.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify password
    if not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    access_token = create_access_token(
        data={"user_id": str(user.id), "role": user.role}, 
        expires_delta=access_token_expires
    )
    
    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role
            }
        },
        "error": None
    }

@router.get("/me", response_model=dict)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current user profile
    """
    return {
        "success": True,
        "data": current_user,
        "error": None
    }
