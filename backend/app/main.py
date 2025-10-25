# backend/app/main.py

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from app.voice.voice_handler import voice_handler
import os

app = FastAPI(title="GrandFLOW AI API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# Voice Call Endpoints (Twilio Webhooks)
# ========================================

@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """
    Twilio webhook for incoming calls
    Uses VoiceCallHandler which manages CallOrchestrator
    """
    return await voice_handler.handle_incoming_call(request)


@app.post("/voice/process-input")
async def process_user_input(request: Request):
    """
    Process transcribed user speech from Twilio
    Routes to appropriate CrewAI agents via CallOrchestrator
    """
    return await voice_handler.process_user_input(request)


@app.post("/voice/outbound")
async def initiate_outbound_call(patient_id: str, call_type: str = "scheduled"):
    """
    Initiate outbound call to patient
    
    Args:
        patient_id: Patient UUID
        call_type: "scheduled" (daily check-in) or "followup"
    """
    return await voice_handler.handle_outbound_call(patient_id, call_type)


@app.post("/voice/call-status")
async def handle_call_status(request: Request):
    """
    Twilio callback for call status updates
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    
    # Log call status change
    print(f"Call {call_sid} status: {call_status}")
    
    return Response(content="OK", media_type="text/plain")

# ========================================
# Dashboard API Endpoints
# ========================================

@app.get("/api/users/{user_id}/health-summary")
async def get_health_summary(user_id: str, days: int = 7):
    """
    Get aggregated health data for dashboard
    """
    from app.database import supabase
    from datetime import datetime, timedelta
    
    start_date = (datetime.now() - timedelta(days=days)).date()
    
    # Fetch all health entries
    diet_reports = supabase.table("diet_reports")\
        .select("*")\
        .eq("user_id", user_id)\
        .gte("date", start_date.isoformat())\
        .execute()
    
    medication = supabase.table("medication_adherence")\
        .select("*")\
        .eq("user_id", user_id)\
        .gte("date", start_date.isoformat())\
        .execute()
    
    wellness = supabase.table("wellness_reports")\
        .select("*")\
        .eq("user_id", user_id)\
        .gte("date", start_date.isoformat())\
        .execute()
    
    cognitive = supabase.table("cognitive_test_reports")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("test_date", desc=True)\
        .limit(1)\
        .execute()
    
    return {
        "diet_reports": diet_reports.data,
        "medication_adherence": medication.data,
        "wellness_reports": wellness.data,
        "latest_cognitive_test": cognitive.data[0] if cognitive.data else None
    }

@app.get("/api/users/{user_id}/vitals")
async def get_vitals_timeseries(user_id: str, hours: int = 24):
    """
    Get heart rate and other vitals for chart
    """
    from app.database import supabase
    from datetime import datetime, timedelta
    
    start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
    
    vitals = supabase.table("vitals_timeseries")\
        .select("*")\
        .eq("user_id", user_id)\
        .gte("timestamp", start_time)\
        .order("timestamp")\
        .execute()
    
    # Group by metric type for charting
    grouped = {}
    for reading in vitals.data:
        metric = reading['metric_type']
        if metric not in grouped:
            grouped[metric] = []
        grouped[metric].append({
            "timestamp": reading['timestamp'],
            "value": reading['value'],
            "unit": reading['unit']
        })
    
    return grouped

@app.get("/api/users/{user_id}/services")
async def get_service_history(user_id: str, days: int = 30):
    """
    Get ride and delivery history
    """
    from app.database import supabase
    from datetime import datetime, timedelta
    
    start_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    rides = supabase.table("rideshare_tasks")\
        .select("*")\
        .eq("user_id", user_id)\
        .gte("time_booked", start_date)\
        .order("time_booked", desc=True)\
        .execute()
    
    deliveries = supabase.table("delivery_tasks")\
        .select("*")\
        .eq("user_id", user_id)\
        .gte("time_booked", start_date)\
        .order("time_booked", desc=True)\
        .execute()
    
    return {
        "rides": rides.data,
        "deliveries": deliveries.data
    }

# ========================================
# Wearable Data Webhook
# ========================================

@app.post("/webhooks/wearable-data")
async def receive_wearable_data(request: Request):
    """
    Receive data from wearable API (Spike API, Terra, etc.)
    """
    payload = await request.json()
    
    # Insert into vitals_timeseries table
    from app.database import supabase
    
    user_id = payload['user_id']
    readings = payload['readings']
    
    for reading in readings:
        supabase.table("vitals_timeseries").insert({
            "user_id": user_id,
            "timestamp": reading['timestamp'],
            "metric_type": reading['metric_type'],
            "value": reading['value'],
            "unit": reading['unit'],
            "metadata": reading.get('metadata', {})
        }).execute()
    
    return {"status": "success", "readings_inserted": len(readings)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
