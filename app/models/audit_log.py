# app/models/audit_log.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AuditAction(str, Enum):
    USER_LOGIN = "user_login"
    USER_REGISTER = "user_register"
    JOURNEY_START = "journey_start"
    JOURNEY_UPDATE = "journey_update"
    JOURNEY_END = "journey_end"
    RISK_ASSESSMENT = "risk_assessment"
    ALERT_CREATED = "alert_created"
    ALERT_RESOLVED = "alert_resolved"
    ALERT_ESCALATED = "alert_escalated"
    DECISION_MADE = "decision_made"
    SOS_TRIGGERED = "sos_triggered"

class AuditLogEntry(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    action: AuditAction
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    resource_id: Optional[str] = None  # ID of the resource affected (journey, alert, etc.)
    resource_type: Optional[str] = None  # Type of resource (journey, alert, etc.)
    details: Optional[Dict[str, Any]] = None  # Additional details about the action
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        populate_by_name = True

class AuditLogCreate(BaseModel):
    user_id: str
    action: AuditAction
    resource_id: Optional[str] = None
    resource_type: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
