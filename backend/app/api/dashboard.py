# backend/app/api/dashboard_data.py

from fastapi import APIRouter, HTTPException, Depends, Query
from app.database import supabase
from app.api.auth import get_current_user
from datetime import datetime, timedelta
from typing import Optional

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("/patient/{patient_id}/summary")
async def get_patient_summary(
    patient_id: str,
    days: int = Query(7, ge=1, le=90),
    current_user = Depends(get_current_user)
):
    """
    Get comprehensive patient dashboard data
    """
    try:
        # Verify caregiver has access to this patient
        access = supabase.table("patient_caregivers")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .eq("caregiver_id", current_user.id)\
            .execute()
        
        if not access.data:
            raise HTTPException(status_code=403, detail="Access denied")
        
        start_date = (datetime.now() - timedelta(days=days)).date().isoformat()
        
        # Fetch patient info
        patient = supabase.table("patients").select("*").eq("id", patient_id).single().execute()
        
        # Health data
        diet_reports = supabase.table("diet_reports")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .gte("date", start_date)\
            .order("date", desc=True)\
            .execute()
        
        medication = supabase.table("medication_adherence")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .gte("date", start_date)\
            .execute()
        
        wellness = supabase.table("wellness_reports")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .gte("date", start_date)\
            .execute()
        
        cognitive = supabase.table("cognitive_test_reports")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .order("test_date", desc=True)\
            .limit(5)\
            .execute()
        
        # Call history
        calls = supabase.table("call_logs")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .order("started_at", desc=True)\
            .limit(20)\
            .execute()
        
        # Service requests
        rides = supabase.table("rideshare_tasks")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .order("time_booked", desc=True)\
            .limit(10)\
            .execute()
        
        deliveries = supabase.table("delivery_tasks")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .order("time_booked", desc=True)\
            .limit(10)\
            .execute()
        
        return {
            "patient": patient.data,
            "health": {
                "diet_reports": diet_reports.data,
                "medication_adherence": medication.data,
                "wellness_reports": wellness.data,
                "cognitive_tests": cognitive.data
            },
            "calls": calls.data,
            "services": {
                "rides": rides.data,
                "deliveries": deliveries.data
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}/vitals")
async def get_patient_vitals(
    patient_id: str,
    metric: str = Query("heart_rate"),
    hours: int = Query(24, ge=1, le=168),
    current_user = Depends(get_current_user)
):
    """
    Get vitals time-series for charting
    """
    try:
        # Verify access
        access = supabase.table("patient_caregivers")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .eq("caregiver_id", current_user.id)\
            .execute()
        
        if not access.data:
            raise HTTPException(status_code=403, detail="Access denied")
        
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        vitals = supabase.table("vitals_timeseries")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .eq("metric_type", metric)\
            .gte("timestamp", start_time)\
            .order("timestamp")\
            .execute()
        
        return {"vitals": vitals.data}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/patient/{patient_id}/calls")
async def get_call_history(
    patient_id: str,
    limit: int = Query(20, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """
    Get call history with stats
    """
    try:
        # Verify access
        access = supabase.table("patient_caregivers")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .eq("caregiver_id", current_user.id)\
            .execute()
        
        if not access.data:
            raise HTTPException(status_code=403, detail="Access denied")
        
        calls = supabase.table("call_logs")\
            .select("*")\
            .eq("patient_id", patient_id)\
            .order("started_at", desc=True)\
            .limit(limit)\
            .execute()
        
        # Calculate stats
        total_calls = len(calls.data)
        outbound_calls = len([c for c in calls.data if c['call_direction'].startswith('outbound')])
        inbound_calls = len([c for c in calls.data if c['call_direction'] == 'inbound_patient'])
        
        durations = [c['duration_seconds'] for c in calls.data if c.get('duration_seconds')]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "calls": calls.data,
            "stats": {
                "total_calls": total_calls,
                "outbound_calls": outbound_calls,
                "inbound_calls": inbound_calls,
                "avg_duration_seconds": int(avg_duration)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
