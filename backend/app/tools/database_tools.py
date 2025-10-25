# backend/app/tools/database_tools.py

from crewai_tools import tool
from supabase import create_client, Client
import os
from app.models.health_entries import DietReport, MedicationAdherence, WellnessReport, SymptomReport
from app.models.cognitive_entries import CognitiveTestReport
from app.models.service_entries import RideshareTask, DeliveryTask

# Initialize Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@tool("Insert Diet Report")
def insert_diet_report(report: dict) -> str:
    """
    Insert a diet report entry into the database during a call.
    
    Args:
        report: Dictionary matching DietReport model
    
    Returns:
        Confirmation message with entry ID
    """
    try:
        diet_report = DietReport(**report)
        
        result = supabase.table("diet_reports").insert({
            "user_id": str(diet_report.user_id),
            "call_id": str(diet_report.call_id) if diet_report.call_id else None,
            "date": diet_report.date.isoformat(),
            "macronutrients": diet_report.macronutrients.dict(),
            "calories": diet_report.calories,
            "meals_count": diet_report.meals_count,
            "vitamins": diet_report.vitamins,
            "recommendations": diet_report.recommendations,
            "diet_quality_score": diet_report.diet_quality_score
        }).execute()
        
        return f"✅ Diet report saved successfully (ID: {result.data[0]['id']})"
    
    except Exception as e:
        return f"❌ Error saving diet report: {str(e)}"

@tool("Insert Medication Adherence")
def insert_medication_adherence(adherence: dict) -> str:
    """
    Record medication adherence during a check-in call.
    
    Args:
        adherence: Dictionary matching MedicationAdherence model
    """
    try:
        med_adherence = MedicationAdherence(**adherence)
        
        result = supabase.table("medication_adherence").insert({
            "user_id": str(med_adherence.user_id),
            "call_id": str(med_adherence.call_id) if med_adherence.call_id else None,
            "date": med_adherence.date.isoformat(),
            "medicines_prescribed": [m.dict() for m in med_adherence.medicines_prescribed],
            "medicines_taken": [m.dict() for m in med_adherence.medicines_taken],
            "adherence_rate": med_adherence.adherence_rate,
            "medications_missed": med_adherence.medications_missed
        }).execute()
        
        return f"✅ Medication adherence recorded (Adherence: {med_adherence.adherence_rate}%)"
    
    except Exception as e:
        return f"❌ Error recording medication: {str(e)}"

@tool("Insert Wellness Report")
def insert_wellness_report(report: dict) -> str:
    """
    Save physical/mental wellness report from daily check-in.
    """
    try:
        wellness = WellnessReport(**report)
        
        result = supabase.table("wellness_reports").insert({
            "user_id": str(wellness.user_id),
            "call_id": str(wellness.call_id) if wellness.call_id else None,
            "date": wellness.date.isoformat(),
            "exercise_completed": wellness.exercise_completed,
            "steps": wellness.steps,
            "calories_burned": wellness.calories_burned,
            "sleep_duration": wellness.sleep_duration,
            "recommendations": wellness.recommendations,
            "exercise_quality_score": wellness.exercise_quality_score
        }).execute()
        
        return f"✅ Wellness report saved (Exercise Quality: {wellness.exercise_quality_score}/100)"
    
    except Exception as e:
        return f"❌ Error saving wellness report: {str(e)}"

@tool("Insert Cognitive Test Report")
def insert_cognitive_test_report(report: dict) -> str:
    """
    Save TICS cognitive test results.
    """
    try:
        cognitive_report = CognitiveTestReport(**report)
        
        result = supabase.table("cognitive_test_reports").insert({
            "user_id": str(cognitive_report.user_id),
            "call_id": str(cognitive_report.call_id) if cognitive_report.call_id else None,
            "test_date": cognitive_report.test_date.isoformat(),
            "tics_score": cognitive_report.tics_score.dict(),
            "mmse_equivalent": cognitive_report.mmse_equivalent,
            "orientation_score": cognitive_report.orientation_score,
            "memory_score": cognitive_report.memory_score,
            "attention_score": cognitive_report.attention_score,
            "language_score": cognitive_report.language_score,
            "cognitive_quality_score": cognitive_report.cognitive_quality_score,
            "risk_level": cognitive_report.risk_level,
            "recommendations": cognitive_report.recommendations,
            "baseline_comparison": cognitive_report.baseline_comparison
        }).execute()
        
        return f"✅ Cognitive test saved (TICS: {cognitive_report.tics_score.total}/41, Risk: {cognitive_report.risk_level})"
    
    except Exception as e:
        return f"❌ Error saving cognitive test: {str(e)}"

@tool("Insert Rideshare Task")
def insert_rideshare_task(task: dict) -> str:
    """
    Record a rideshare booking made during the call.
    """
    try:
        rideshare = RideshareTask(**task)
        
        result = supabase.table("rideshare_tasks").insert({
            "user_id": str(rideshare.user_id),
            "call_id": str(rideshare.call_id) if rideshare.call_id else None,
            "company": rideshare.company,
            "pickup_location": rideshare.pickup_location,
            "dropoff_location": rideshare.dropoff_location,
            "time_booked": rideshare.time_booked.isoformat(),
            "scheduled_for": rideshare.scheduled_for.isoformat(),
            "status": rideshare.status,
            "external_ride_id": rideshare.external_ride_id
        }).execute()
        
        return f"✅ Rideshare booked: {rideshare.company} from {rideshare.pickup_location} to {rideshare.dropoff_location}"
    
    except Exception as e:
        return f"❌ Error booking rideshare: {str(e)}"

@tool("Insert Delivery Task")
def insert_delivery_task(task: dict) -> str:
    """
    Record a delivery order placed during the call.
    """
    try:
        delivery = DeliveryTask(**task)
        
        result = supabase.table("delivery_tasks").insert({
            "user_id": str(delivery.user_id),
            "call_id": str(delivery.call_id) if delivery.call_id else None,
            "item": delivery.item,
            "service_provider": delivery.service_provider,
            "time_booked": delivery.time_booked.isoformat(),
            "scheduled_for": delivery.scheduled_for.isoformat() if delivery.scheduled_for else None,
            "items_ordered": delivery.items_ordered,
            "status": delivery.status,
            "external_order_id": delivery.external_order_id
        }).execute()
        
        return f"✅ Delivery ordered: {delivery.item} via {delivery.service_provider}"
    
    except Exception as e:
        return f"❌ Error ordering delivery: {str(e)}"

@tool("Get User Medical Profile")
def get_user_medical_profile(user_id: str) -> dict:
    """
    Fetch user's medical profile for personalized recommendations.
    """
    try:
        result = supabase.table("medical_profiles")\
            .select("*")\
            .eq("user_id", user_id)\
            .single()\
            .execute()
        
        return result.data
    
    except Exception as e:
        return {"error": str(e)}

@tool("Get Latest Vitals")
def get_latest_vitals(user_id: str, hours: int = 24) -> dict:
    """
    Fetch recent wearable vitals for health assessment.
    """
    try:
        from datetime import datetime, timedelta
        cutoff = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        result = supabase.table("vitals_timeseries")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("timestamp", cutoff)\
            .order("timestamp", desc=True)\
            .execute()
        
        # Group by metric type
        vitals = {}
        for reading in result.data:
            metric = reading['metric_type']
            if metric not in vitals:
                vitals[metric] = []
            vitals[metric].append({
                "value": reading['value'],
                "unit": reading['unit'],
                "timestamp": reading['timestamp']
            })
        
        return vitals
    
    except Exception as e:
        return {"error": str(e)}


@tool("Log Call Start")
def log_call_start(patient_id: str, call_sid: str, call_direction: str) -> str:
    """
    Create call log entry when call begins.
    
    Returns:
        call_id (UUID) to link all entries created during this call
    """
    try:
        call_data = {
            "patient_id": patient_id,
            "call_sid": call_sid,
            "call_direction": call_direction,
            "started_at": datetime.now().isoformat(),
            "agents_involved": [],
            "tasks_completed": [],
            "service_requests_mentioned": []
        }
        
        result = supabase.table("call_logs").insert(call_data).execute()
        call_id = result.data[0]['id']
        
        return call_id
    
    except Exception as e:
        return f"Error: {str(e)}"

@tool("Update Call Agents Involved")
def update_call_agents(call_id: str, agent_name: str) -> str:
    """
    Add agent to the list of agents involved in this call.
    """
    try:
        # Use PostgreSQL array_append function
        supabase.rpc('append_agent_to_call', {
            'call_log_id': call_id,
            'agent': agent_name
        }).execute()
        
        return f"✅ Agent {agent_name} logged for call {call_id}"
    
    except Exception as e:
        return f"❌ Error updating call log: {str(e)}"

@tool("Log Call End")
def log_call_end(call_id: str, transcript: str, patient_mood: str) -> str:
    """
    Finalize call log when call ends.
    """
    try:
        from datetime import datetime
        
        # Get call start time to calculate duration
        call = supabase.table("call_logs").select("started_at").eq("id", call_id).single().execute()
        started_at = datetime.fromisoformat(call.data['started_at'])
        ended_at = datetime.now()
        duration = int((ended_at - started_at).total_seconds())
        
        supabase.table("call_logs").update({
            "ended_at": ended_at.isoformat(),
            "duration_seconds": duration,
            "transcript": transcript,
            "patient_mood": patient_mood,
            "call_status": "completed"
        }).eq("id", call_id).execute()
        
        return f"✅ Call logged (Duration: {duration}s, Mood: {patient_mood})"
    
    except Exception as e:
        return f"❌ Error finalizing call log: {str(e)}"
