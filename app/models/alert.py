# app/models/alert.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AlertType(str, Enum):
    SOS = "sos"
    AUTOMATED_ALERT = "automated_alert"
    MANUAL_ALERT = "manual_alert"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class AlertPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Location(BaseModel):
    lat: float = Field(..., example=23.02)
    lng: float = Field(..., example=72.57)

class AlertCreation(BaseModel):
    journey_id: str
    alert_type: AlertType
    message: str
    location: Location
    priority: AlertPriority = AlertPriority.MEDIUM

class AlertInDB(BaseModel):
    id: str = Field(..., alias="_id")
    journey_id: str
    user_id: str
    alert_type: AlertType
    message: str
    location: Location
    priority: AlertPriority
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    assigned_to: Optional[str] = None  # Police officer ID

    class Config:
        populate_by_name = True

class AlertResponse(AlertInDB):
    pass

class AlertUpdate(BaseModel):
    status: AlertStatus
    resolved_at: Optional[datetime] = None
    escalated_at: Optional[datetime] = None
    assigned_to: Optional[str] = None
