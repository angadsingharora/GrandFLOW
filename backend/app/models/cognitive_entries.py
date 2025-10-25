from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
from uuid import UUID

class TICSScore(BaseModel):
    # TICS test components (max 41 points)
    orientation: int  # Max 5 (date, day, month, year, season)
    registration: int  # Max 3 (immediate recall of 3 words)
    attention_calculation: int  # Max 5 (serial 7s)
    recall: int  # Max 3 (delayed recall)
    naming: int  # Max 2 (name objects)
    repetition: int  # Max 1 (repeat phrase)
    comprehension: int  # Max 3 (3-step command)
    total: int  # Sum of all

class CognitiveTestReport(BaseModel):
    user_id: UUID
    call_id: Optional[UUID] = None
    test_date: date = Field(default_factory=date.today)
    
    tics_score: TICSScore
    mmse_equivalent: int  # TICS to MMSE conversion
    
    # Domain scores
    orientation_score: int
    memory_score: int
    attention_score: int
    language_score: int
    
    cognitive_quality_score: int = Field(ge=0, le=100)
    risk_level: str  # "normal", "mild_impairment", "moderate", "severe"
    recommendations: List[str]
    
    baseline_comparison: Optional[dict] = None
python