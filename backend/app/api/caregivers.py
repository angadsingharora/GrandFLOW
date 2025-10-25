# backend/app/api/caregivers.py

from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase, get_caregiver_patients
from app.api.auth import get_current_user
from typing import List

router = APIRouter(prefix="/api/caregivers", tags=["caregivers"])

@router.get("/me/patients")
async def get_my_patients(current_user = Depends(get_current_user)):
    """
    Get all patients assigned to the authenticated caregiver
    """
    try:
        patients = await get_caregiver_patients(current_user.id)
        
        # Enrich with call summary
        enriched_patients = []
        for pc in patients:
            patient = pc['patients']
            
            # Get last call
            last_call = supabase.table("call_logs")\
                .select("started_at, patient_mood")\
                .eq("patient_id", patient['id'])\
                .order("started_at", desc=True)\
                .limit(1)\
                .execute()
            
            enriched_patients.append({
                **patient,
                "relationship": pc['relationship'],
                "last_call_at": last_call.data[0]['started_at'] if last_call.data else None,
                "last_mood": last_call.data[0]['patient_mood'] if last_call.data else None
            })
        
        return {"patients": enriched_patients}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
