# app/core/database.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

class Database:
    client: AsyncIOMotorClient = None

db = Database()

async def get_database():
    if db.client is None:
        try:
            db.client = AsyncIOMotorClient(MONGO_DETAILS)
            print(f"Connected to MongoDB at {MONGO_DETAILS}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            print("Database operations will fail until connection is established")
            raise e
    return db.client[DATABASE_NAME]

async def connect_to_mongo():
    try:
        db.client = AsyncIOMotorClient(MONGO_DETAILS)
        print(f"Connected to MongoDB at {MONGO_DETAILS}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Running without database connection")

async def close_mongo_connection():
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")
