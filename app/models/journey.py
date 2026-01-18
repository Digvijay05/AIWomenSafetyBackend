# app/models/journey.py
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
from bson import ObjectId

class MovementState(str, Enum):
    WALKING = "walking"
    RUNNING = "running"
    DRIVING = "driving"
    CYCLING = "cycling"
    STATIONARY = "stationary"

class Location(BaseModel):
    lat: float = Field(..., example=23.02)
    lng: float = Field(..., example=72.57)

class JourneyStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class JourneyStart(BaseModel):
    start_location: Location
    start_time: datetime = Field(default_factory=datetime.utcnow)
    destination: Optional[Location] = None
    expected_duration: Optional[int] = None  # in minutes

class JourneyTelemetry(BaseModel):
    journey_id: str
    timestamp: datetime
    location: Location
    speed: float = Field(..., ge=0)  # meters per second
    movement_state: MovementState
    battery_level: int = Field(..., ge=0, le=100)  # percentage
    altitude: Optional[float] = None
    accuracy: Optional[float] = None

class JourneyUpdate(BaseModel):
    journey_id: str
    timestamp: datetime
    location: Location
    speed: float = Field(..., ge=0)
    movement_state: MovementState
    battery_level: int = Field(..., ge=0, le=100)
    altitude: Optional[float] = None
    accuracy: Optional[float] = None

class JourneyEnd(BaseModel):
    journey_id: str
    end_time: datetime
    end_location: Location

class JourneyResume(BaseModel):
    journey_id: str
    resume_time: datetime
    current_location: Location

class JourneyInDB(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    start_time: datetime
    start_location: Location
    status: JourneyStatus = JourneyStatus.ACTIVE
    destination: Optional[Location] = None
    expected_duration: Optional[int] = None
    end_time: Optional[datetime] = None
    end_location: Optional[Location] = None
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    telemetry_points: List[JourneyTelemetry] = []

    class Config:
        populate_by_name = True

class JourneyResponse(JourneyInDB):
    pass

class RiskFactor(str, Enum):
    ISOLATED_AREA = "isolated_area"
    NIGHT_TIME = "night_time"
    ROUTE_DEVIATION = "route_deviation"
    SPEED_ANOMALY = "speed_anomaly"
    LOW_BATTERY = "low_battery"

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    confidence: float = Field(..., ge=0, le=1)  # confidence score between 0 and 1
    factors: List[RiskFactor]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class RiskAnalysisRequest(BaseModel):
    journey_id: str
    telemetry: JourneyTelemetry

class DecisionAction(str, Enum):
    SILENT_MONITORING = "silent_monitoring"
    WARNING_NOTIFICATION = "warning_notification"
    SAFE_ROUTE_SUGGESTION = "safe_route_suggestion"
    ALERT_ESCALATION = "alert_escalation"
    POLICE_DASHBOARD_EVENT = "police_dashboard_event"

class DecisionOutput(BaseModel):
    action: DecisionAction
    risk_assessment: RiskAssessment
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AlertType(str, Enum):
    SOS = "sos"
    AUTOMATED_ALERT = "automated_alert"
    MANUAL_ALERT = "manual_alert"

class AlertCreation(BaseModel):
    journey_id: str
    alert_type: AlertType
    message: str
    location: Location
    risk_level: RiskLevel

class AlertInDB(BaseModel):
    id: str = Field(..., alias="_id")
    journey_id: str
    user_id: str
    alert_type: AlertType
    message: str
    location: Location
    risk_level: RiskLevel
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolved_at: Optional[datetime] = None

    class Config:
        populate_by_name = True

class AlertResponse(AlertInDB):
    pass

