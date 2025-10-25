#this file will contain the specific health entry block scheme that should be used
# backend/app/models/health_entries.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID

class Macronutrients(BaseModel):
    protein: int  # grams
    carbs: int
    fats: int

class DietReport(BaseModel):
    user_id: UUID
    call_id: Optional[UUID] = None
    date: date = Field(default_factory=date.today)
    
    macronutrients: Macronutrients
    calories: int
    meals_count: int
    vitamins: List[str]
    recommendations: List[str]
    
    diet_quality_score: int = Field(ge=0, le=100)

class MedicinePrescribed(BaseModel):
    name: str
    dosage: str
    scheduled_time: str  # "08:00"

class MedicineTaken(BaseModel):
    name: str
    time_taken: str  # "08:15"

class MedicationAdherence(BaseModel):
    user_id: UUID
    call_id: Optional[UUID] = None
    date: date = Field(default_factory=date.today)
    
    medicines_prescribed: List[MedicinePrescribed]
    medicines_taken: List[MedicineTaken]
    
    adherence_rate: float = Field(ge=0, le=100)
    medications_missed: List[str]

class WellnessReport(BaseModel):
    user_id: UUID
    call_id: Optional[UUID] = None
    date: date = Field(default_factory=date.today)
    
    exercise_completed: bool
    steps: int
    calories_burned: int
    sleep_duration: int  # minutes
    recommendations: List[str]
    
    exercise_quality_score: int = Field(ge=0, le=100)

class SymptomReport(BaseModel):
    user_id: UUID
    call_id: Optional[UUID] = None
    date: date = Field(default_factory=date.today)
    
    symptoms_reported: List[str]
    severity_scores: dict  # {"pain": 5, "fatigue": 3}
    symptom_quality_score: int = Field(ge=0, le=100)
    recommendations: List[str]
