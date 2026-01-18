# app/alerts/dispatcher.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timedelta
from app.models.journey import DecisionAction, DecisionOutput, RiskAssessment, AlertType, RiskLevel, Location
from app.models.alert import AlertCreation, AlertPriority
from app.crud.alert import create_alert
from app.utils.audit_logger import get_audit_logger

class ActionDispatcher:
    """
    Dispatcher that executes decision engine actions
    All actions are idempotent, logged, and auditable
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def dispatch_action(
        self,
        decision: DecisionOutput,
        user_id: str,
        journey_id: str,
        location: Location,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict:
        """
        Execute a decision action and return execution result
        
        Returns a dictionary with execution details
        """
        action = decision.action
        risk_assessment = decision.risk_assessment
        
        result = {
            "action": action.value,
            "executed": False,
            "alert_id": None,
            "message": decision.message
        }
        
        try:
            if action == DecisionAction.ALERT_ESCALATION:
                # Create high-priority alert and escalate to police dashboard
                result = await self._create_alert(
                    user_id=user_id,
                    journey_id=journey_id,
                    location=location,
                    alert_type=AlertType.AUTOMATED_ALERT,
                    priority=AlertPriority.CRITICAL if risk_assessment.risk_level == RiskLevel.CRITICAL else AlertPriority.HIGH,
                    message=decision.message,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                result["executed"] = True
                
            elif action == DecisionAction.POLICE_DASHBOARD_EVENT:
                # Create police dashboard event (alert with medium/high priority)
                priority = AlertPriority.HIGH if risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else AlertPriority.MEDIUM
                result = await self._create_alert(
                    user_id=user_id,
                    journey_id=journey_id,
                    location=location,
                    alert_type=AlertType.AUTOMATED_ALERT,
                    priority=priority,
                    message=decision.message,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                result["executed"] = True
                
            elif action == DecisionAction.WARNING_NOTIFICATION:
                # Create warning alert (user notification)
                result = await self._create_alert(
                    user_id=user_id,
                    journey_id=journey_id,
                    location=location,
                    alert_type=AlertType.AUTOMATED_ALERT,
                    priority=AlertPriority.MEDIUM,
                    message=decision.message,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                result["executed"] = True
                
            elif action == DecisionAction.SAFE_ROUTE_SUGGESTION:
                # Log safe route suggestion (no alert, just monitoring)
                audit_logger = get_audit_logger()
                await audit_logger.log_decision_made(
                    user_id=user_id,
                    journey_id=journey_id,
                    action=action.value,
                    risk_level=risk_assessment.risk_level.value,
                    confidence=risk_assessment.confidence,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                result["executed"] = True
                
            elif action == DecisionAction.SILENT_MONITORING:
                # No action required, just log
                audit_logger = get_audit_logger()
                await audit_logger.log_decision_made(
                    user_id=user_id,
                    journey_id=journey_id,
                    action=action.value,
                    risk_level=risk_assessment.risk_level.value,
                    confidence=risk_assessment.confidence,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                result["executed"] = True
            
            return result
            
        except Exception as e:
            # Log error but don't fail the request
            result["error"] = str(e)
            result["executed"] = False
            return result
    
    async def _create_alert(
        self,
        user_id: str,
        journey_id: str,
        location: Location,
        alert_type: AlertType,
        priority: AlertPriority,
        message: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict:
        """
        Create an alert (idempotent operation)
        """
        # Check if similar alert already exists (prevent duplicates)
        existing_alerts = await self.db.alerts.find({
            "journey_id": journey_id,
            "user_id": user_id,
            "status": {"$ne": "RESOLVED"},
            "created_at": {"$gte": datetime.utcnow() - datetime.timedelta(minutes=5)}
        }).limit(1).to_list(length=1)
        
        if existing_alerts:
            # Alert already exists, return existing alert ID
            return {
                "action": "alert_creation",
                "executed": True,
                "alert_id": existing_alerts[0]["_id"],
                "message": message,
                "duplicate": True
            }
        
        # Create new alert
        alert_data = AlertCreation(
            journey_id=journey_id,
            alert_type=alert_type,
            message=message,
            location=location,
            priority=priority
        )
        
        alert = await create_alert(self.db, user_id, alert_data)
        
        # Log audit event
        audit_logger = get_audit_logger()
        await audit_logger.log_alert_created(
            user_id=user_id,
            alert_id=alert.id,
            alert_type=alert_type.value,
            priority=priority.value,
            message=message,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return {
            "action": "alert_creation",
            "executed": True,
            "alert_id": alert.id,
            "message": message,
            "duplicate": False
        }
