# backend/app/main.py

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from twilio.twiml.voice_response import VoiceResponse, Gather
from app.voice.conversation_manager import ConversationManager
import os

app = FastAPI(title="CareCompanion AI API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/voice/incoming")
async def handle_incoming_call(request: Request):
    """
    Twilio webhook for incoming calls
    """
    form_data = await request.form()
    caller_number = form_data.get("From")
    call_sid = form_data.get("CallSid")
    
    # Lookup user by phone number
    from app.database import supabase
    user = supabase.table("users").select("id").eq("phone_number", caller_number).single().execute()
    
    if not user.data:
        # Unknown caller
        response = VoiceResponse()
        response.say("Sorry, we don't recognize your phone number. Please contact support.", voice="Polly.Joanna")
        response.hangup()
        return Response(content=str(response), media_type="application/xml")
    
    user_id = user.data['id']
    
    # Initialize conversation manager
    conversation_manager = ConversationManager(user_id, call_sid)
    
    # Start conversation
    response = VoiceResponse()
    response.say("Hello! Connecting you to CareCompanion AI.", voice="Polly.Joanna")
    response.redirect("/voice/conversation")
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/voice/conversation")
async def handle_conversation(request: Request):
    """
    Main conversation handler (streams audio)
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    
    # Retrieve conversation manager from session
    # (In production, use Redis for session storage)
    
    response = VoiceResponse()
    
    # Use Gather to collect speech input
    gather = Gather(
        input='speech',
        action='/voice/process-input',
        method='POST',
        timeout=5,
        speechTimeout='auto'
    )
    gather.say("How can I help you today?", voice="Polly.Joanna")
    
    response.append(gather)
    response.redirect("/voice/conversation")  # Loop back if no input
    
    return Response(content=str(response), media_type="application/xml")

@app.post("/voice/process-input")
async def process_user_input(request: Request):
    """
    Process transcribed user speech
    """
    form_data = await request.form()
    user_speech = form_data.get("SpeechResult")
    call_sid = form_data.get("CallSid")
    
    # Pass to conversation manager
    # (Retrieve from session, process with CrewAI agents)
    
    # For now, simple echo
    response = VoiceResponse()
    response.say(f"You said: {user_speech}", voice="Polly.Joanna")
    response.redirect("/voice/conversation")
    
    return Response(content=str(response), media_type="application/xml")

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
