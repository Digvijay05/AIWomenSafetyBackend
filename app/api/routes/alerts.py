# app/api/routes/alerts.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
import os
from dotenv import load_dotenv

from app.core.database import get_database
from app.models.alert import AlertCreation, AlertResponse, AlertUpdate, AlertInDB
from app.crud.alert import create_alert, get_alert, get_user_alerts, get_police_dashboard_alerts, update_alert
from app.api.routes.users import get_current_user
from app.models.user import UserResponse, UserRole

load_dotenv()

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.post("/", response_model=dict)
async def create_new_alert(
    alert_data: AlertCreation,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create a new alert
    """
    try:
        alert = await create_alert(db, current_user.id, alert_data)
        return {
            "success": True,
            "data": {
                "alert": alert,
                "message": "Alert created successfully"
            },
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )

@router.get("/", response_model=dict)
async def get_alerts(
    limit: int = 50,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get alerts for the current user
    Police users can access dashboard alerts
    """
    try:
        if current_user.role == UserRole.POLICE or current_user.role == UserRole.ADMIN:
            # Police and admin get dashboard alerts
            alerts = await get_police_dashboard_alerts(db, limit)
        else:
            # Regular users get their own alerts
            alerts = await get_user_alerts(db, current_user.id, limit)
        
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
            detail=f"Failed to retrieve alerts: {str(e)}"
        )

@router.get("/{alert_id}", response_model=dict)
async def get_alert_details(
    alert_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed information for a specific alert
    """
    try:
        alert = await get_alert(db, alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
            
        # Users can only see their own alerts unless they're police/admin
        if current_user.role not in [UserRole.ADMIN, UserRole.POLICE] and alert.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this alert"
            )
            
        return {
            "success": True,
            "data": {
                "alert": alert
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alert: {str(e)}"
        )

@router.put("/{alert_id}", response_model=dict)
async def update_alert_status(
    alert_id: str,
    alert_update: AlertUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update an alert status (resolve, escalate, assign)
    Police and admin can update any alert
    Users can only update their own alerts
    """
    try:
        # Verify alert exists
        alert = await get_alert(db, alert_id)
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
            
        # Check authorization
        if current_user.role not in [UserRole.ADMIN, UserRole.POLICE] and alert.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this alert"
            )
        
        # Update alert
        success = await update_alert(db, alert_id, alert_update)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update alert"
            )
            
        # Get updated alert
        updated_alert = await get_alert(db, alert_id)
        
        return {
            "success": True,
            "data": {
                "alert": updated_alert,
                "message": "Alert updated successfully"
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert: {str(e)}"
        )
