# app/crud/user.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from app.models.user import UserCreate, UserInDB, UserResponse
from app.core.security import get_password_hash

async def get_user(db: AsyncIOMotorDatabase, email: str) -> Optional[UserInDB]:
    """Get a user by email"""
    user_doc = await db.users.find_one({"email": email})
    if user_doc:
        return UserInDB(**user_doc)
    return None

async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[UserInDB]:
    """Get a user by ID"""
    user_doc = await db.users.find_one({"_id": ObjectId(user_id)})
    if user_doc:
        return UserInDB(**user_doc)
    return None

async def create_user(db: AsyncIOMotorDatabase, user: UserCreate) -> UserResponse:
    """Create a new user"""
    # Check if user already exists
    existing_user = await get_user(db, user.email)
    if existing_user:
        raise ValueError("User with this email already exists")
    
    # Hash the password
    hashed_password = get_password_hash(user.password)
    
    # Create user document
    user_dict = user.dict()
    user_dict.pop("password")
    user_dict["hashed_password"] = hashed_password
    
    # Insert into database
    result = await db.users.insert_one(user_dict)
    
    # Return user response
    user_dict["_id"] = str(result.inserted_id)
    return UserResponse(**user_dict)

async def update_user(db: AsyncIOMotorDatabase, user_id: str, user_update: dict) -> Optional[UserResponse]:
    """Update a user"""
    # Remove password from update if present
    if "password" in user_update:
        user_update.pop("password")
    
    # Update the user
    result = await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user_update}
    )
    
    if result.modified_count > 0:
        updated_user = await get_user_by_id(db, user_id)
        return UserResponse(**updated_user.dict())
    
    return None

async def delete_user(db: AsyncIOMotorDatabase, user_id: str) -> bool:
    """Delete a user"""
    result = await db.users.delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0
