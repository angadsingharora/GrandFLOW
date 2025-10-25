# backend/app/models/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class User(BaseModel):
    """
    User model (caregiver/family member)
    """
    id: Optional[UUID] = Field(default_factory=uuid4)
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "sarah.johnson@email.com",
                "full_name": "Sarah Johnson",
                "phone_number": "+1234567890"
            }
        }

class UserCreate(BaseModel):
    """
    User creation schema
    """
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    """
    User response schema (no password)
    """
    id: UUID
    email: EmailStr
    full_name: str
    phone_number: Optional[str] = None
    created_at: datetime
    
class PatientCaregiver(BaseModel):
    """
    Many-to-many relationship between patients and caregivers
    """
    id: Optional[UUID] = Field(default_factory=uuid4)
    patient_id: UUID
    caregiver_id: UUID
    relationship: str  # "daughter", "son", "spouse", "professional_caregiver"
    access_level: str = "full"  # "full", "limited"
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": "123e4567-e89b-12d3-a456-426614174000",
                "caregiver_id": "123e4567-e89b-12d3-a456-426614174001",
                "relationship": "daughter",
                "access_level": "full"
            }
        }
