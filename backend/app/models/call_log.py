# backend/app/models/call_log.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from enum import Enum

class CallDirection(str, Enum):
    OUTBOUND_SCHEDULED = "outbound_scheduled"  # Scheduled daily check-in
    OUTBOUND_FOLLOWUP = "outbound_followup"    # Follow-up from concern
    INBOUND_PATIENT = "inbound_patient"        # Patient called in

class CallStatus(str, Enum):
    COMPLETED = "completed"
    MISSED = "missed"
    FAILED = "failed"

class ServiceRequestMentioned(BaseModel):
    type: str  # "ride", "food_delivery", "groceries", "home_service"
    details: dict
    timestamp: datetime
    status: str = "mentioned"  # mentioned, mock_completed

class CallLog(BaseModel):
    id: Optional[UUID] = None
    patient_id: UUID
    
    call_sid: str
    call_direction: CallDirection
    call_status: CallStatus = CallStatus.COMPLETED
    
    scheduled_at: Optional[datetime] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    transcript: Optional[str] = None
    audio_recording_url: Optional[str] = None
    
    agents_involved: List[str] = []
    tasks_completed: List[dict] = []
    
    # Linked entry IDs
    diet_report_id: Optional[UUID] = None
    medication_adherence_id: Optional[UUID] = None
    wellness_report_id: Optional[UUID] = None
    cognitive_test_id: Optional[UUID] = None
    
    service_requests_mentioned: List[ServiceRequestMentioned] = []
    
    patient_mood: Optional[str] = None
