#fake service tools for the MVP

from crewai_tools import tool
from datetime import datetime
from app.database import supabase
import uuid

@tool("Book Ride (Mock)")
def mock_book_ride(patient_id: str, call_id: str, destination: str, provider: str = "uber") -> str:
    """
    Simulate booking a ride. In production, this would call Uber/Lyft API.
    For MVP, just log the request to database.
    
    Args:
        patient_id: Patient UUID
        call_id: Current call UUID
        destination: Where patient needs to go
        provider: "uber" or "lyft"
    """
    try:
        # Mock ride details
        ride_data = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "call_id": call_id,
            "company": provider,
            "pickup_location": "Patient's home",
            "dropoff_location": destination,
            "time_booked": datetime.now().isoformat(),
            "scheduled_for": None,  # Would calculate based on conversation
            "status": "mock_booked",
            "external_ride_id": f"MOCK_{uuid.uuid4().hex[:8]}"
        }
        
        # Insert to rideshare_tasks table
        result = supabase.table("rideshare_tasks").insert(ride_data).execute()
        
        # Also log in call_logs.service_requests_mentioned
        supabase.rpc('append_service_request', {
            'call_log_id': call_id,
            'service_data': {
                'type': 'ride',
                'provider': provider,
                'destination': destination,
                'status': 'mentioned'
            }
        }).execute()
        
        return f"✅ {provider.capitalize()} ride to {destination} has been noted. " \
               f"In production, this would be confirmed with driver details."
    
    except Exception as e:
        return f"❌ Error logging ride request: {str(e)}"

@tool("Order Food (Mock)")
def mock_order_food(patient_id: str, call_id: str, restaurant: str, items: list) -> str:
    """
    Simulate ordering food delivery. In production, would call DoorDash API.
    """
    try:
        order_data = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "call_id": call_id,
            "item": f"Meal from {restaurant}",
            "service_provider": "doordash",
            "time_booked": datetime.now().isoformat(),
            "items_ordered": [{"name": item, "quantity": 1} for item in items],
            "status": "mock_ordered",
            "external_order_id": f"MOCK_{uuid.uuid4().hex[:8]}"
        }
        
        result = supabase.table("delivery_tasks").insert(order_data).execute()
        
        # Log in call
        supabase.rpc('append_service_request', {
            'call_log_id': call_id,
            'service_data': {
                'type': 'food_delivery',
                'restaurant': restaurant,
                'items': items,
                'status': 'mentioned'
            }
        }).execute()
        
        return f"✅ Food order from {restaurant} has been noted. " \
               f"In production, order would be placed and delivery tracked."
    
    except Exception as e:
        return f"❌ Error logging food order: {str(e)}"

@tool("Order Groceries (Mock)")
def mock_order_groceries(patient_id: str, call_id: str, grocery_list: list) -> str:
    """
    Simulate grocery order via Instacart.
    """
    try:
        order_data = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "call_id": call_id,
            "item": "Groceries via Instacart",
            "service_provider": "instacart",
            "time_booked": datetime.now().isoformat(),
            "items_ordered": [{"name": item, "quantity": 1} for item in grocery_list],
            "status": "mock_ordered"
        }
        
        result = supabase.table("delivery_tasks").insert(order_data).execute()
        
        return f"✅ Grocery order noted ({len(grocery_list)} items). " \
               f"In production, Instacart shopper would be assigned."
    
    except Exception as e:
        return f"❌ Error logging grocery order: {str(e)}"

@tool("Schedule Home Service (Mock)")
def mock_schedule_home_service(patient_id: str, call_id: str, service_type: str, date: str) -> str:
    """
    Simulate booking home service (cleaning, repairs, etc.)
    """
    try:
        service_data = {
            "id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "call_id": call_id,
            "item": f"{service_type.capitalize()} service",
            "service_provider": "taskrabbit",
            "time_booked": datetime.now().isoformat(),
            "scheduled_for": date,
            "status": "mock_scheduled"
        }
        
        result = supabase.table("delivery_tasks").insert(service_data).execute()
        
        return f"✅ {service_type.capitalize()} service scheduled for {date}. " \
               f"In production, service provider would be confirmed."
    
    except Exception as e:
        return f"❌ Error logging service request: {str(e)}"
