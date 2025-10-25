from supabase import create_client, Client
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase_url: str = os.getenv("SUPABASE_URL")
supabase_key: str = os.getenv("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")

supabase: Client = create_client(supabase_url, supabase_key)

def get_supabase_client() -> Client:
    """
    Get Supabase client instance
    """
    return supabase

# Helper functions for common database operations

async def get_patient_by_id(patient_id: str) -> Optional[dict]:
    """
    Fetch patient by ID
    """
    try:
        result = supabase.table("patients")\
            .select("*")\
            .eq("id", patient_id)\
            .single()\
            .execute()
        return result.data
    except Exception as e:
        print(f"Error fetching patient: {e}")
        return None

async def get_patient_by_phone(phone_number: str) -> Optional[dict]:
    """
    Fetch patient by phone number (for incoming calls)
    """
    try:
        result = supabase.table("patients")\
            .select("*")\
            .eq("phone_number", phone_number)\
            .single()\
            .execute()
        return result.data
    except Exception as e:
        print(f"Error fetching patient by phone: {e}")
        return None

async def get_user_by_id(user_id: str) -> Optional[dict]:
    """
    Fetch user (caregiver) by ID
    """
    try:
        result = supabase.table("users")\
            .select("*")\
            .eq("id", user_id)\
            .single()\
            .execute()
        return result.data
    except Exception as e:
        print(f"Error fetching user: {e}")
        return None

async def get_caregiver_patients(caregiver_id: str) -> list:
    """
    Get all patients assigned to a caregiver
    """
    try:
        result = supabase.table("patient_caregivers")\
            .select("*, patients(*)")\
            .eq("caregiver_id", caregiver_id)\
            .execute()
        return result.data
    except Exception as e:
        print(f"Error fetching caregiver patients: {e}")
        return []

async def insert_record(table: str, data: dict) -> Optional[dict]:
    """
    Generic insert function
    """
    try:
        result = supabase.table(table).insert(data).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error inserting into {table}: {e}")
        return None

async def update_record(table: str, record_id: str, data: dict) -> Optional[dict]:
    """
    Generic update function
    """
    try:
        result = supabase.table(table).update(data).eq("id", record_id).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating {table}: {e}")
        return None

async def query_records(table: str, filters: dict, order_by: str = "created_at", 
                       limit: int = 100, descending: bool = True) -> list:
    """
    Generic query function with filters
    """
    try:
        query = supabase.table(table).select("*")
        
        for key, value in filters.items():
            query = query.eq(key, value)
        
        query = query.order(order_by, desc=descending).limit(limit)
        
        result = query.execute()
        return result.data
    except Exception as e:
        print(f"Error querying {table}: {e}")
        return []