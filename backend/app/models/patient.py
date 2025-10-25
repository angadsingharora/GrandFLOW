# backend/app/models/patient.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID, uuid4

class Patient(BaseModel):
    """
    Patient model (senior being monitored)
    """
    id: Optional[UUID] = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    date_of_birth: date
    phone_number: str
    address: Optional[dict] = None
    emergency_contacts: Optional[List[dict]] = []
    
    # Medical information
    conditions: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    medications: Optional[List[dict]] = []
    dietary_restrictions: Optional[List[str]] = []
    primary_care_physician: Optional[dict] = None
    
    # Call scheduling preferences
    preferred_call_times: Optional[List[time]] = []
    call_frequency: str = "daily"  # daily, weekly, on_demand
    
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "Margaret",
                "last_name": "Thompson",
                "date_of_birth": "1945-05-15",
                "phone_number": "+1234567890",
                "address": {
                    "street": "123 Oak Street",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94102"
                },
                "conditions": ["hypertension", "diabetes_type_2"],
                "allergies": ["penicillin"],
                "medications": [
                    {
                        "name": "Lisinopril",
                        "dosage": "10mg",
                        "frequency": "daily",
                        "times": ["08:00"]
                    }
                ],
                "dietary_restrictions": ["low_sodium", "diabetic_friendly"],
                "preferred_call_times": ["09:00", "14:00"],
                "call_frequency": "daily"
            }
        }

class PatientCreate(BaseModel):
    """
    Patient creation schema
    """
    first_name: str
    last_name: str
    date_of_birth: date
    phone_number: str
    address: Optional[dict] = None
    emergency_contacts: Optional[List[dict]] = []
    conditions: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    medications: Optional[List[dict]] = []
    dietary_restrictions: Optional[List[str]] = []

class PatientUpdate(BaseModel):
    """
    Patient update schema (all fields optional)
    """
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[dict] = None
    emergency_contacts: Optional[List[dict]] = None
    conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    medications: Optional[List[dict]] = None
    dietary_restrictions: Optional[List[str]] = None
    preferred_call_times: Optional[List[time]] = None
    call_frequency: Optional[str] = None

class PatientResponse(BaseModel):
    """
    Patient response schema
    """
    id: UUID
    first_name: str
    last_name: str
    date_of_birth: date
    phone_number: str
    conditions: List[str]
    medications: List[dict]
    created_at: datetime
