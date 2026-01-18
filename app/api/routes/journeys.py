# app/api/routes/journeys.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from fastapi import APIRouter, Depends, HTTPException, status, Request
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv

from app.core.database import get_database
from app.models.journey import (
    JourneyStart, JourneyTelemetry, JourneyEnd, JourneyResume,
    JourneyResponse, RiskAssessment, DecisionOutput, AlertCreation,
    RiskAnalysisRequest
)
from app.crud.journey import (
    create_journey, get_journey, add_telemetry_point, 
    update_journey_status, get_active_journeys_for_user, get_recent_journeys
)
from app.api.routes.users import get_current_user
from app.models.user import UserResponse, UserRole
from app.risk_engine.analyzer import risk_analyzer
from app.decision_engine.engine import decision_engine
from app.utils.audit_logger import get_audit_logger
from app.alerts.dispatcher import ActionDispatcher

load_dotenv()

router = APIRouter(prefix="/journeys", tags=["journeys"])

def get_client_ip(request: Request) -> str:
    """Extract client IP address from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host

@router.post("/start", response_model=dict)
async def start_journey(
    journey_start: JourneyStart,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Start a new journey
    """
    try:
        journey = await create_journey(db, current_user.id, journey_start)
        
        # Log audit event
        audit_logger = get_audit_logger()
        await audit_logger.log_journey_start(
            user_id=current_user.id,
            journey_id=journey.id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        return {
            "success": True,
            "data": {
                "journey": journey,
                "message": "Journey started successfully"
            },
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start journey: {str(e)}"
        )

@router.post("/telemetry", response_model=dict)
async def update_journey_telemetry(
    telemetry: JourneyTelemetry,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update journey with new telemetry data
    This will trigger risk analysis and decision engine
    """
    try:
        # Verify journey belongs to user
        journey = await get_journey(db, telemetry.journey_id)
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journey not found"
            )
            
        if journey.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this journey"
            )
            
        # Add telemetry point
        success = await add_telemetry_point(db, telemetry.journey_id, telemetry)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add telemetry point"
            )
            
        # Trigger risk analysis
        risk_assessment = risk_analyzer.analyze_telemetry(telemetry)
        
        # Trigger decision engine
        decision = decision_engine.make_decision(risk_assessment)
        
        # Execute decision action via dispatcher
        action_dispatcher = ActionDispatcher(db)
        action_result = await action_dispatcher.dispatch_action(
            decision=decision,
            user_id=current_user.id,
            journey_id=telemetry.journey_id,
            location=telemetry.location,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        # Log audit events
        audit_logger = get_audit_logger()
        await audit_logger.log_journey_update(
            user_id=current_user.id,
            journey_id=telemetry.journey_id,
            details={
                "location": telemetry.location.dict(),
                "speed": telemetry.speed,
                "movement_state": telemetry.movement_state
            },
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        await audit_logger.log_risk_assessment(
            user_id=current_user.id,
            journey_id=telemetry.journey_id,
            risk_level=risk_assessment.risk_level.value,
            factors=[f.value for f in risk_assessment.factors],
            confidence=risk_assessment.confidence,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        # Decision action already logged in dispatcher, skip duplicate log
        
        return {
            "success": True,
            "data": {
                "telemetry_added": True,
                "risk_assessment": {
                    "risk_level": risk_assessment.risk_level.value,
                    "confidence": risk_assessment.confidence,
                    "factors": [f.value for f in risk_assessment.factors],
                    "timestamp": risk_assessment.timestamp.isoformat()
                },
                "decision": {
                    "action": decision.action.value,
                    "message": decision.message,
                    "timestamp": decision.timestamp.isoformat()
                },
                "action_result": action_result
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update telemetry: {str(e)}"
        )

@router.post("/analyze-risk", response_model=dict)
async def analyze_risk(
    risk_request: RiskAnalysisRequest,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Analyze risk for a specific telemetry point
    """
    try:
        # Verify journey belongs to user
        journey = await get_journey(db, risk_request.journey_id)
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journey not found"
            )
            
        if journey.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to analyze this journey"
            )
            
        # Perform risk analysis
        risk_assessment = risk_analyzer.analyze_telemetry(risk_request.telemetry)
        
        # Log audit event
        audit_logger = get_audit_logger()
        await audit_logger.log_risk_assessment(
            user_id=current_user.id,
            journey_id=risk_request.journey_id,
            risk_level=risk_assessment.risk_level.value,
            factors=[f.value for f in risk_assessment.factors],
            confidence=risk_assessment.confidence,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        return {
            "success": True,
            "data": {
                "risk_assessment": {
                    "risk_level": risk_assessment.risk_level.value,
                    "confidence": risk_assessment.confidence,
                    "factors": [f.value for f in risk_assessment.factors],
                    "timestamp": risk_assessment.timestamp.isoformat()
                }
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze risk: {str(e)}"
        )

@router.post("/end", response_model=dict)
async def end_journey(
    journey_end: JourneyEnd,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    End a journey
    """
    try:
        # Verify journey belongs to user
        journey = await get_journey(db, journey_end.journey_id)
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journey not found"
            )
            
        if journey.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to end this journey"
            )
        
        # Update journey status to completed
        success = await update_journey_status(
            db, 
            journey_end.journey_id, 
            "COMPLETED", 
            journey_end.end_location, 
            journey_end.end_time
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to end journey"
            )
            
        # Log audit event
        audit_logger = get_audit_logger()
        await audit_logger.log_journey_end(
            user_id=current_user.id,
            journey_id=journey_end.journey_id,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
            
        return {
            "success": True,
            "data": {
                "journey_id": journey_end.journey_id,
                "message": "Journey ended successfully"
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end journey: {str(e)}"
        )

@router.post("/resume", response_model=dict)
async def resume_journey(
    journey_resume: JourneyResume,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Resume a paused journey
    """
    try:
        # Verify journey belongs to user
        journey = await get_journey(db, journey_resume.journey_id)
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journey not found"
            )
            
        if journey.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to resume this journey"
            )
        
        # Update journey status to active
        success = await update_journey_status(
            db, 
            journey_resume.journey_id, 
            "ACTIVE"
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to resume journey"
            )
            
        # Log audit event
        audit_logger = get_audit_logger()
        await audit_logger.log_journey_update(
            user_id=current_user.id,
            journey_id=journey_resume.journey_id,
            details={"action": "resume"},
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
            
        return {
            "success": True,
            "data": {
                "journey_id": journey_resume.journey_id,
                "message": "Journey resumed successfully"
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume journey: {str(e)}"
        )

@router.get("/", response_model=dict)
async def get_user_journeys(
    limit: int = 10,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get recent journeys for the current user
    """
    try:
        journeys = await get_recent_journeys(db, current_user.id, limit)
        return {
            "success": True,
            "data": {
                "journeys": journeys
            },
            "error": None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve journeys: {str(e)}"
        )

@router.get("/{journey_id}", response_model=dict)
async def get_journey_details(
    journey_id: str,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get detailed information for a specific journey
    """
    try:
        journey = await get_journey(db, journey_id)
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journey not found"
            )
            
        # Non-admin users can only see their own journeys
        if current_user.role != UserRole.ADMIN and journey.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this journey"
            )
            
        return {
            "success": True,
            "data": {
                "journey": journey
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve journey: {str(e)}"
        )

@router.post("/alerts", response_model=dict)
async def create_alert(
    alert_data: AlertCreation,
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Create an alert for a journey
    """
    try:
        # Verify journey belongs to user or user is admin/police
        journey = await get_journey(db, alert_data.journey_id)
        if not journey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Journey not found"
            )
            
        if current_user.role not in [UserRole.ADMIN, UserRole.POLICE] and journey.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create alert for this journey"
            )
        
        # Create alert in database (stub implementation)
        from bson import ObjectId
        
        alert_dict = {
            "_id": str(ObjectId()),
            "journey_id": alert_data.journey_id,
            "user_id": journey.user_id,
            "alert_type": alert_data.alert_type,
            "message": alert_data.message,
            "location": alert_data.location.dict(),
            "risk_level": "HIGH",  # Fixed this issue
            "created_at": datetime.utcnow(),  # Fixed this issue
            "resolved": False
        }
        
        # Insert into database
        await db.alerts.insert_one(alert_dict)
        
        # Log audit event
        audit_logger = get_audit_logger()
        await audit_logger.log_alert_created(
            user_id=current_user.id,
            alert_id=alert_dict["_id"],
            alert_type=alert_data.alert_type,
            priority="HIGH",  # This is a simplification
            message=alert_data.message,
            ip_address=get_client_ip(request),
            user_agent=request.headers.get("User-Agent")
        )
        
        return {
            "success": True,
            "data": {
                "alert_id": alert_dict["_id"],
                "message": "Alert created successfully"
            },
            "error": None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create alert: {str(e)}"
        )
