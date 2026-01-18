# app/crud/audit_log.py
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
from datetime import datetime, timedelta
from app.models.audit_log import AuditLogEntry, AuditLogCreate

async def create_audit_log(db: AsyncIOMotorDatabase, audit_data: AuditLogCreate) -> AuditLogEntry:
    """Create a new audit log entry"""
    audit_dict = {
        "_id": str(ObjectId()),
        "user_id": audit_data.user_id,
        "action": audit_data.action,
        "timestamp": datetime.utcnow(),
        "resource_id": audit_data.resource_id,
        "resource_type": audit_data.resource_type,
        "details": audit_data.details,
        "ip_address": audit_data.ip_address,
        "user_agent": audit_data.user_agent
    }
    
    # Insert into database
    await db.audit_logs.insert_one(audit_dict)
    
    return AuditLogEntry(**audit_dict)

async def get_audit_logs(db: AsyncIOMotorDatabase, user_id: Optional[str] = None, 
                        action: Optional[str] = None, limit: int = 100) -> List[AuditLogEntry]:
    """Get audit logs with optional filtering"""
    query = {}
    if user_id:
        query["user_id"] = user_id
    if action:
        query["action"] = action
        
    logs_cursor = db.audit_logs.find(query).sort("timestamp", -1).limit(limit)
    
    logs = []
    async for log_doc in logs_cursor:
        logs.append(AuditLogEntry(**log_doc))
    
    return logs

async def get_recent_audit_logs(db: AsyncIOMotorDatabase, hours: int = 24) -> List[AuditLogEntry]:
    """Get audit logs from the last N hours"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    logs_cursor = db.audit_logs.find({
        "timestamp": {"$gte": cutoff_time}
    }).sort("timestamp", -1)
    
    logs = []
    async for log_doc in logs_cursor:
        logs.append(AuditLogEntry(**log_doc))
    
    return logs

async def get_user_audit_logs(db: AsyncIOMotorDatabase, user_id: str, limit: int = 50) -> List[AuditLogEntry]:
    """Get audit logs for a specific user"""
    return await get_audit_logs(db, user_id=user_id, limit=limit)
