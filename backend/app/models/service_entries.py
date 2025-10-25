from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from uuid import UUID

class RideshareTask(BaseModel):
    user_id: UUID
    call_id: Optional[UUID] = None
    
    company: str  # "uber" or "lyft"
    pickup_location: str
    dropoff_location: str
    time_booked: datetime
    scheduled_for: datetime
    
    status: str = "pending"
    external_ride_id: Optional[str] = None

class DeliveryTask(BaseModel):
    user_id: UUID
    call_id: Optional[UUID] = None
    
    item: str
    service_provider: str  # "doordash", "instacart", "pharmacy"
    time_booked: datetime
    scheduled_for: Optional[datetime] = None
    
    items_ordered: List[dict]
    status: str = "pending"
    external_order_id: Optional[str] = None
