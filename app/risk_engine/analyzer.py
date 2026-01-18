# app/risk_engine/analyzer.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from datetime import datetime, time
from typing import List, Tuple
import math
from app.models.journey import (
    JourneyTelemetry, RiskAssessment, RiskFactor, RiskLevel
)

class RiskAnalyzer:
    """
    Server-side risk analysis engine that evaluates telemetry data
    and produces structured risk assessments
    """
    
    def __init__(self):
        # Define safe zones (lat, lng, radius in meters)
        self.safe_zones = [
            # Example safe zones - in a real system, this would come from a database
            (23.02, 72.57, 1000),  # University area
            (23.03, 72.58, 500),   # Shopping mall
        ]
        
        # Define unsafe zones 
        self.unsafe_zones = [
            # Example unsafe zones
            (23.05, 72.60, 800),   # Industrial area
        ]
    
    def analyze_telemetry(self, telemetry: JourneyTelemetry) -> RiskAssessment:
        """
        Analyze telemetry data and produce a risk assessment
        """
        risk_factors = []
        risk_score = 0.0
        
        # 1. Time-based risk analysis
        time_risk = self._analyze_time_risk(telemetry.timestamp)
        if time_risk:
            risk_factors.append(time_risk)
            risk_score += 0.3
            
        # 2. Location-based risk analysis
        location_risk = self._analyze_location_risk(telemetry.location)
        if location_risk:
            risk_factors.extend(location_risk)
            risk_score += len(location_risk) * 0.2
            
        # 3. Movement state analysis
        movement_risk = self._analyze_movement_state(telemetry.movement_state)
        if movement_risk:
            risk_factors.append(movement_risk)
            risk_score += 0.15
            
        # 4. Speed anomaly detection
        speed_risk = self._analyze_speed_anomaly(telemetry.speed)
        if speed_risk:
            risk_factors.append(speed_risk)
            risk_score += 0.2
            
        # 5. Battery level analysis
        battery_risk = self._analyze_battery_level(telemetry.battery_level)
        if battery_risk:
            risk_factors.append(battery_risk)
            risk_score += 0.15
            
        # Determine overall risk level based on accumulated score
        risk_level = self._determine_risk_level(risk_score)
        
        # Cap confidence at 1.0
        confidence = min(risk_score, 1.0)
        
        return RiskAssessment(
            risk_level=risk_level,
            confidence=confidence,
            factors=risk_factors
        )
    
    def _analyze_time_risk(self, timestamp: datetime) -> RiskFactor | None:
        """
        Analyze time-based risk (night time, etc.)
        """
        # High risk during night hours (9 PM to 6 AM)
        night_hours = [21, 22, 23, 0, 1, 2, 3, 4, 5, 6]
        if timestamp.hour in night_hours:
            return RiskFactor.NIGHT_TIME
        return None
    
    def _analyze_location_risk(self, location: 'Location') -> List[RiskFactor]:
        """
        Analyze location-based risks (isolated areas, unsafe zones)
        """
        risk_factors = []
        
        # Check if in isolated area (simplified implementation)
        # In a real system, this would use actual geographic/isolation data
        if self._is_isolated_area(location.lat, location.lng):
            risk_factors.append(RiskFactor.ISOLATED_AREA)
            
        # Check if near unsafe zones
        for unsafe_lat, unsafe_lng, radius in self.unsafe_zones:
            if self._calculate_distance(location.lat, location.lng, unsafe_lat, unsafe_lng) <= radius:
                risk_factors.append(RiskFactor.ISOLATED_AREA)
                break
                
        return risk_factors
    
    def _analyze_movement_state(self, movement_state: str) -> RiskFactor | None:
        """
        Analyze movement state for potential risks
        """
        # Stationary for extended periods might indicate an issue
        # This would require historical data, simplified here
        return None  # Placeholder for more complex logic
    
    def _analyze_speed_anomaly(self, speed: float) -> RiskFactor | None:
        """
        Detect unusual speed patterns that might indicate distress
        """
        # Extremely slow movement (possible distress) or extremely fast (unsafe)
        if speed < 0.1:  # Nearly stationary
            return RiskFactor.SPEED_ANOMALY
        elif speed > 15:  # Running or possibly vehicle issues (>54 km/h walking)
            return RiskFactor.SPEED_ANOMALY
        return None
    
    def _analyze_battery_level(self, battery_level: int) -> RiskFactor | None:
        """
        Low battery could prevent communication
        """
        if battery_level < 10:
            return RiskFactor.LOW_BATTERY
        return None
    
    def _is_isolated_area(self, lat: float, lng: float) -> bool:
        """
        Determine if an area is isolated based on distance from known safe zones
        """
        min_safe_distance = 2000  # meters, considered isolated if no safe zone within 2km
        for safe_lat, safe_lng, _ in self.safe_zones:
            distance = self._calculate_distance(lat, lng, safe_lat, safe_lng)
            if distance <= min_safe_distance:
                return False
        return True
    
    def _calculate_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """
        Calculate approximate distance between two points in meters
        Uses simplified Euclidean distance for demonstration purposes
        """
        # Earth's radius in meters
        R = 6371000
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        # Haversine formula
        a = (math.sin(delta_lat/2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2) ** 2)
        c = 2 * math.atan2(a ** 0.5, (1-a) ** 0.5)
        
        return R * c
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """
        Determine overall risk level based on accumulated score
        """
        if risk_score >= 0.7:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.5:
            return RiskLevel.HIGH
        elif risk_score >= 0.3:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

# Create a singleton instance for use throughout the application
risk_analyzer = RiskAnalyzer()
