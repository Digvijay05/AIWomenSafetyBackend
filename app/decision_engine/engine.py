# app/decision_engine/engine.py
import sys

# Python version guard - terminate execution if not Python 3.11
if not (sys.version_info.major == 3 and sys.version_info.minor == 11):
    raise RuntimeError(
        f"Unsupported Python version: {sys.version}. "
        "This project requires Python 3.11.x."
    )

from typing import Dict, Any
from app.models.journey import (
    RiskAssessment, DecisionAction, DecisionOutput, RiskLevel, RiskFactor
)
from app.risk_engine.analyzer import risk_analyzer

class DecisionEngine:
    """
    Agentic decision engine that determines appropriate actions based on risk assessments
    """
    
    def __init__(self):
        # Configuration thresholds for decision making
        self.decision_thresholds = {
            RiskLevel.LOW: 0.3,
            RiskLevel.MEDIUM: 0.5,
            RiskLevel.HIGH: 0.7,
            RiskLevel.CRITICAL: 0.9
        }
    
    def make_decision(self, risk_assessment: RiskAssessment) -> DecisionOutput:
        """
        Make a decision based on risk assessment
        """
        action = self._determine_action(risk_assessment)
        message = self._generate_message(risk_assessment, action)
        
        return DecisionOutput(
            action=action,
            risk_assessment=risk_assessment,
            message=message
        )
    
    def _determine_action(self, risk_assessment: RiskAssessment) -> DecisionAction:
        """
        Determine the appropriate action based on risk level and factors
        """
        risk_level = risk_assessment.risk_level
        factors = risk_assessment.factors
        confidence = risk_assessment.confidence
        
        # Critical risk - immediate action required
        if risk_level == RiskLevel.CRITICAL:
            # If it's critical with high confidence, escalate alert
            if confidence > 0.8:
                return DecisionAction.ALERT_ESCALATION
            else:
                return DecisionAction.WARNING_NOTIFICATION
        
        # High risk - notify and monitor closely
        elif risk_level == RiskLevel.HIGH:
            if confidence > 0.7:
                return DecisionAction.WARNING_NOTIFICATION
            else:
                return DecisionAction.SILENT_MONITORING
        
        # Medium risk - cautious monitoring
        elif risk_level == RiskLevel.MEDIUM:
            # Check specific factors for targeted actions
            factor_values = [f.value for f in factors]
            if RiskFactor.ISOLATED_AREA.value in factor_values:
                return DecisionAction.SAFE_ROUTE_SUGGESTION
            elif RiskFactor.NIGHT_TIME.value in factor_values:
                return DecisionAction.WARNING_NOTIFICATION
            else:
                return DecisionAction.SILENT_MONITORING
        
        # Low risk - normal monitoring
        else:
            return DecisionAction.SILENT_MONITORING
    
    def _generate_message(self, risk_assessment: RiskAssessment, action: DecisionAction) -> str:
        """
        Generate a human-readable message explaining the decision
        """
        risk_level = risk_assessment.risk_level
        factors = [f.value for f in risk_assessment.factors]
        factors_str = ", ".join(factors) if factors else "none"
        
        if action == DecisionAction.ALERT_ESCALATION:
            return f"Critical risk detected ({risk_level.value}) with factors: {factors_str}. Immediate assistance requested."
        elif action == DecisionAction.WARNING_NOTIFICATION:
            return f"Elevated risk ({risk_level.value}) detected with factors: {factors_str}. User notified."
        elif action == DecisionAction.SAFE_ROUTE_SUGGESTION:
            return f"Medium risk ({risk_level.value}) detected in isolated area. Safe route suggested to user."
        elif action == DecisionAction.POLICE_DASHBOARD_EVENT:
            return f"Safety event reported for user journey. Risk level: {risk_level.value}. Factors: {factors_str}."
        else:  # SILENT_MONITORING
            return f"Normal monitoring continuing. Current risk level: {risk_level.value}."

# Create a singleton instance for use throughout the application
decision_engine = DecisionEngine()
