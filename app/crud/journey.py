# app/crud/journey.py
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
from datetime import datetime
from app.models.journey import (
    JourneyStart, JourneyTelemetry, JourneyInDB, JourneyResponse,
    JourneyStatus, Location
)

async def create_journey(db: AsyncIOMotorDatabase, user_id: str, journey_start: JourneyStart) -> JourneyResponse:
    """Create a new journey"""
    journey_dict = {
        "_id": str(ObjectId()),
        "user_id": user_id,
        "start_time": journey_start.start_time,
        "start_location": journey_start.start_location.dict(),
        "status": JourneyStatus.ACTIVE,
        "destination": journey_start.destination.dict() if journey_start.destination else None,
        "expected_duration": journey_start.expected_duration,
        "last_updated": datetime.utcnow(),
        "telemetry_points": []
    }
    
    # Insert into database
    await db.journeys.insert_one(journey_dict)
    
    return JourneyResponse(**journey_dict)

async def get_journey(db: AsyncIOMotorDatabase, journey_id: str) -> Optional[JourneyInDB]:
    """Get a journey by ID"""
    journey_doc = await db.journeys.find_one({"_id": journey_id})
    if journey_doc:
        return JourneyInDB(**journey_doc)
    return None

async def add_telemetry_point(db: AsyncIOMotorDatabase, journey_id: str, telemetry: JourneyTelemetry) -> bool:
    """Add a telemetry point to a journey"""
    # Add telemetry point to the journey
    result = await db.journeys.update_one(
        {"_id": journey_id},
        {
            "$push": {"telemetry_points": telemetry.dict()},
            "$set": {"last_updated": datetime.utcnow()}
        }
    )
    
    return result.modified_count > 0

async def update_journey_status(db: AsyncIOMotorDatabase, journey_id: str, status: JourneyStatus, 
                               end_location: Optional[Location] = None, end_time: Optional[datetime] = None) -> bool:
    """Update journey status"""
    update_fields = {
        "status": status,
        "last_updated": datetime.utcnow()
    }
    
    if end_location:
        update_fields["end_location"] = end_location.dict()
        
    if end_time:
        update_fields["end_time"] = end_time
    
    result = await db.journeys.update_one(
        {"_id": journey_id},
        {"$set": update_fields}
    )
    
    return result.modified_count > 0

async def get_active_journeys_for_user(db: AsyncIOMotorDatabase, user_id: str) -> List[JourneyInDB]:
    """Get all active journeys for a user"""
    journeys_cursor = db.journeys.find({
        "user_id": user_id,
        "status": JourneyStatus.ACTIVE
    })
    
    journeys = []
    async for journey_doc in journeys_cursor:
        journeys.append(JourneyInDB(**journey_doc))
    
    return journeys

async def get_recent_journeys(db: AsyncIOMotorDatabase, user_id: str, limit: int = 10) -> List[JourneyInDB]:
    """Get recent journeys for a user"""
    journeys_cursor = db.journeys.find({"user_id": user_id}).sort("start_time", -1).limit(limit)
    
    journeys = []
    async for journey_doc in journeys_cursor:
        journeys.append(JourneyInDB(**journey_doc))
    
    return journeys
