# backend/app/voice/call_session.py

"""
Call Session Management for Multi-Turn CrewAI Conversations

Manages the state of ongoing calls, tracking crew instances,
accumulated data, and conversation progress.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum

from app.models.health_entries import DietReport, MedicationAdherence, WellnessReport
from app.models.cognitive_entries import CognitiveTestReport


class CallSessionState(Enum):
    """States for call session lifecycle"""
    INITIATED = "initiated"
    IN_CONVERSATION = "in_conversation"
    DATA_COLLECTION = "data_collection"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class CallSession:
    """
    Maintains state for an active call conversation
    
    This tracks:
    - The active crew instance (with memory)
    - Data accumulated during conversation
    - Conversation turn count
    - Session state
    """
    call_sid: str
    patient_id: str
    call_direction: str
    call_id: str
    call_type: str  # "health_checkup", "cognitive_test", etc.
    
    # Crew instance with memory
    active_crew: Any = None
    
    # Accumulated data models (gradually filled)
    diet_data: Optional[Dict[str, Any]] = None
    medication_data: Optional[Dict[str, Any]] = None
    wellness_data: Optional[Dict[str, Any]] = None
    cognitive_data: Optional[Dict[str, Any]] = None
    
    # Conversation tracking
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    turn_count: int = 0
    state: CallSessionState = CallSessionState.INITIATED
    
    # Metadata
    started_at: datetime = field(default_factory=datetime.now)
    last_interaction: datetime = field(default_factory=datetime.now)
    
    def add_turn(self, user_input: str, agent_response: str):
        """Add a conversation turn"""
        self.conversation_history.append({
            "turn": self.turn_count,
            "user": user_input,
            "agent": agent_response,
            "timestamp": datetime.now().isoformat()
        })
        self.turn_count += 1
        self.last_interaction = datetime.now()
    
    def update_diet_data(self, field: str, value: Any):
        """Update diet data field"""
        if self.diet_data is None:
            self.diet_data = {}
        self.diet_data[field] = value
    
    def update_medication_data(self, field: str, value: Any):
        """Update medication data field"""
        if self.medication_data is None:
            self.medication_data = {}
        self.medication_data[field] = value
    
    def update_wellness_data(self, field: str, value: Any):
        """Update wellness data field"""
        if self.wellness_data is None:
            self.wellness_data = {}
        self.wellness_data[field] = value
    
    def update_cognitive_data(self, field: str, value: Any):
        """Update cognitive data field"""
        if self.cognitive_data is None:
            self.cognitive_data = {}
        self.cognitive_data[field] = value
    
    def is_data_complete(self) -> bool:
        """Check if enough data has been collected"""
        if self.call_type == "health_checkup":
            # Need minimum data for diet, medications, and wellness
            return (
                self.diet_data is not None and 
                len(self.diet_data) >= 3 and  # At least meals
                self.medication_data is not None and
                self.wellness_data is not None
            )
        elif self.call_type == "cognitive_test":
            return (
                self.cognitive_data is not None and
                len(self.cognitive_data) >= 5  # Need TICS scores
            )
        return False


class CallSessionManager:
    """
    Manages all active call sessions
    
    Provides access to session state across webhook calls
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, CallSession] = {}
    
    def create_session(
        self,
        call_sid: str,
        patient_id: str,
        call_direction: str,
        call_id: str,
        call_type: str
    ) -> CallSession:
        """Create a new call session"""
        session = CallSession(
            call_sid=call_sid,
            patient_id=patient_id,
            call_direction=call_direction,
            call_id=call_id,
            call_type=call_type
        )
        self.active_sessions[call_sid] = session
        return session
    
    def get_session(self, call_sid: str) -> Optional[CallSession]:
        """Get an active session by call SID"""
        return self.active_sessions.get(call_sid)
    
    def end_session(self, call_sid: str) -> Optional[CallSession]:
        """End a session and return it"""
        return self.active_sessions.pop(call_sid, None)
    
    def cleanup_old_sessions(self, max_age_minutes: int = 60):
        """Clean up sessions older than max_age_minutes"""
        now = datetime.now()
        to_remove = []
        
        for call_sid, session in self.active_sessions.items():
            age = (now - session.last_interaction).total_seconds() / 60
            if age > max_age_minutes:
                to_remove.append(call_sid)
        
        for call_sid in to_remove:
            self.active_sessions.pop(call_sid, None)


# Global session manager instance
session_manager = CallSessionManager()

