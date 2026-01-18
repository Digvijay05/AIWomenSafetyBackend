# app/crud/alert.py
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
from app.models.alert import AlertInDB, AlertCreation, AlertUpdate, AlertStatus

async def create_alert(db: AsyncIOMotorDatabase, user_id: str, alert_data: AlertCreation) -> AlertInDB:
    """Create a new alert"""
    alert_dict = {
        "_id": str(ObjectId()),
        "journey_id": alert_data.journey_id,
        "user_id": user_id,
        "alert_type": alert_data.alert_type,
        "message": alert_data.message,
        "location": alert_data.location.dict(),
        "priority": alert_data.priority,
        "status": AlertStatus.ACTIVE,
        "created_at": datetime.utcnow()
    }
    
    # Insert into database
    await db.alerts.insert_one(alert_dict)
    
    return AlertInDB(**alert_dict)

async def get_alert(db: AsyncIOMotorDatabase, alert_id: str) -> Optional[AlertInDB]:
    """Get an alert by ID"""
    alert_doc = await db.alerts.find_one({"_id": alert_id})
    if alert_doc:
        return AlertInDB(**alert_doc)
    return None

async def get_user_alerts(db: AsyncIOMotorDatabase, user_id: str, limit: int = 50) -> List[AlertInDB]:
    """Get all alerts for a user"""
    alerts_cursor = db.alerts.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    
    alerts = []
    async for alert_doc in alerts_cursor:
        alerts.append(AlertInDB(**alert_doc))
    
    return alerts

async def get_police_dashboard_alerts(db: AsyncIOMotorDatabase, limit: int = 50) -> List[AlertInDB]:
    """Get alerts for police dashboard (high priority and unresolved)"""
    alerts_cursor = db.alerts.find({
        "$or": [
            {"priority": "HIGH"},
            {"priority": "CRITICAL"}
        ],
        "status": {"$ne": "RESOLVED"}
    }).sort("created_at", -1).limit(limit)
    
    alerts = []
    async for alert_doc in alerts_cursor:
        alerts.append(AlertInDB(**alert_doc))
    
    return alerts

async def update_alert(db: AsyncIOMotorDatabase, alert_id: str, alert_update: AlertUpdate) -> bool:
    """Update an alert"""
    update_fields = alert_update.dict(exclude_unset=True)
    
    # Handle timestamp fields
    if alert_update.status == AlertStatus.RESOLVED and alert_update.resolved_at is None:
        update_fields["resolved_at"] = datetime.utcnow()
    elif alert_update.status == AlertStatus.ESCALATED and alert_update.escalated_at is None:
        update_fields["escalated_at"] = datetime.utcnow()
    
    result = await db.alerts.update_one(
        {"_id": alert_id},
        {"$set": update_fields}
    )
    
    return result.modified_count > 0

async def delete_alert(db: AsyncIOMotorDatabase, alert_id: str) -> bool:
    """Delete an alert"""
    result = await db.alerts.delete_one({"_id": alert_id})
    return result.deleted_count > 0
