# app/utils/audit_logger.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.models.audit_log import AuditLogCreate, AuditAction
from app.crud.audit_log import create_audit_log

class AuditLogger:
    """
    Utility class for logging audit events throughout the application
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def log_user_login(self, user_id: str, ip_address: Optional[str] = None, 
                            user_agent: Optional[str] = None):
        """Log user login event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.USER_LOGIN,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_user_register(self, user_id: str, ip_address: Optional[str] = None, 
                               user_agent: Optional[str] = None):
        """Log user registration event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.USER_REGISTER,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_journey_start(self, user_id: str, journey_id: str, 
                               ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log journey start event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.JOURNEY_START,
            resource_id=journey_id,
            resource_type="journey",
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_journey_update(self, user_id: str, journey_id: str, 
                                details: Optional[Dict[str, Any]] = None,
                                ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log journey update event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.JOURNEY_UPDATE,
            resource_id=journey_id,
            resource_type="journey",
            details=details,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_journey_end(self, user_id: str, journey_id: str,
                             ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log journey end event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.JOURNEY_END,
            resource_id=journey_id,
            resource_type="journey",
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_risk_assessment(self, user_id: str, journey_id: str, risk_level: str,
                                 factors: list, confidence: float,
                                 ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log risk assessment event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.RISK_ASSESSMENT,
            resource_id=journey_id,
            resource_type="journey",
            details={
                "risk_level": risk_level,
                "factors": factors,
                "confidence": confidence
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_alert_created(self, user_id: str, alert_id: str, alert_type: str,
                               priority: str, message: str,
                               ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log alert creation event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.ALERT_CREATED,
            resource_id=alert_id,
            resource_type="alert",
            details={
                "alert_type": alert_type,
                "priority": priority,
                "message": message
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_alert_resolved(self, user_id: str, alert_id: str,
                                ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log alert resolution event"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.ALERT_RESOLVED,
            resource_id=alert_id,
            resource_type="alert",
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)
    
    async def log_decision_made(self, user_id: str, journey_id: str, action: str,
                               risk_level: str, confidence: float,
                               ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log decision engine action"""
        audit_data = AuditLogCreate(
            user_id=user_id,
            action=AuditAction.DECISION_MADE,
            resource_id=journey_id,
            resource_type="journey",
            details={
                "decision_action": action,
                "risk_level": risk_level,
                "confidence": confidence
            },
            ip_address=ip_address,
            user_agent=user_agent
        )
        return await create_audit_log(self.db, audit_data)

# Global audit logger instance
audit_logger: Optional[AuditLogger] = None

async def init_audit_logger(db: AsyncIOMotorDatabase):
    """Initialize the global audit logger"""
    global audit_logger
    audit_logger = AuditLogger(db)

def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance"""
    if audit_logger is None:
        raise RuntimeError("Audit logger not initialized")
    return audit_logger
