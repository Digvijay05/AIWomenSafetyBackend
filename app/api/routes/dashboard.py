# app/api/routes/dashboard.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

from app.core.database import get_database
from app.models.user import UserResponse, UserRole
from app.api.routes.users import get_current_user
from app.crud.alert import get_police_dashboard_alerts
from app.crud.journey import get_recent_journeys

load_dotenv()

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

async def require_police_or_admin(current_user: UserResponse = Depends(get_current_user)):
    """
    Dependency to ensure only police or admin users can access dashboard
    """
    if current_user.role not in [UserRole.POLICE, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Police or admin privileges required."
        )
    return current_user

@router.get("/stats", response_model=dict)
async def get_dashboard_stats(
    current_user: UserResponse = Depends(require_police_or_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get dashboard statistics for police officers
    """
    try:
        # Get alert statistics
        critical_alerts = await db.alerts.count_documents({
            "priority": "CRITICAL",
            "status": {"$ne": "RESOLVED"}
        })
        
        high_alerts = await db.alerts.count_documents({
            "priority": "HIGH",
            "status": {"$ne": "RESOLVED"}
        })
        
        total_active_alerts = await db.alerts.count_documents({
            "status": {"$ne": "RESOLVED"}
        })
        
        # Get recent user activity (last 24 hours)
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        active_users = await db.journeys.count_documents({
            "last_updated": {"$gte": twenty_four_hours_ago}
        })
        
        # Get resolved alerts in last 24 hours
        resolved_alerts = await db.alerts.count_documents({
            "resolved_at": {"$gte": twenty_four_hours_ago}
        })
        
        stats = {
            "total_active_alerts": total_active_alerts,
            "critical_alerts": critical_alerts,
            "high_alerts": high_alerts,
            "active_users": active_users,
            "resolved_alerts_24h": resolved_alerts
        }
        
        return {
            "success": True,
            "data": {
                "statistics": stats
            },
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard statistics: {str(e)}"
        )

@router.get("/alerts", response_model=dict)
async def get_dashboard_alerts(
    limit: int = 50,
    current_user: UserResponse = Depends(require_police_or_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get alerts for police dashboard
    """
    try:
        alerts = await get_police_dashboard_alerts(db, limit)
        
        return {
            "success": True,
            "data": {
                "alerts": alerts
            },
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard alerts: {str(e)}"
        )

@router.get("/recent-activity", response_model=dict)
async def get_recent_activity(
    limit: int = 20,
    current_user: UserResponse = Depends(require_police_or_admin),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get recent user activity for situational awareness
    """
    try:
        # Get recent journeys
        recent_journeys = []
        # This is a simplified implementation - in reality you'd implement
        # a more sophisticated query to get recent activity across all users
        
        # For demonstration, we'll get recent journeys from a few sample users
        # In a real app, this would be optimized with proper indexing
        
        return {
            "success": True,
            "data": {
                "recent_activity": recent_journeys
            },
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve recent activity: {str(e)}"
        )
