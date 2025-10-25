# backend/app/api/auth.py

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import supabase
from app.models.user import UserCreate, UserResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()

class SignInRequest(BaseModel):
    email: str
    password: str

class SignInResponse(BaseModel):
    access_token: str
    refresh_token: str
    user: UserResponse

class SignUpRequest(BaseModel):
    email: str
    password: str
    full_name: str
    phone_number: Optional[str] = None

@router.post("/signup", response_model=SignInResponse)
async def sign_up(request: SignUpRequest):
    """
    Register new user (caregiver)
    """
    try:
        # Create auth user in Supabase
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user:
            # Create user record in users table
            user_data = {
                "id": auth_response.user.id,
                "email": request.email,
                "full_name": request.full_name,
                "phone_number": request.phone_number
            }
            
            supabase.table("users").insert(user_data).execute()
            
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "user": {
                    "id": auth_response.user.id,
                    "email": request.email,
                    "full_name": request.full_name,
                    "phone_number": request.phone_number,
                    "created_at": auth_response.user.created_at
                }
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/signin", response_model=SignInResponse)
async def sign_in(request: SignInRequest):
    """
    Sign in existing user
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        
        if auth_response.user:
            # Get user data
            user_data = supabase.table("users")\
                .select("*")\
                .eq("id", auth_response.user.id)\
                .single()\
                .execute()
            
            return {
                "access_token": auth_response.session.access_token,
                "refresh_token": auth_response.session.refresh_token,
                "user": user_data.data
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

@router.post("/signout")
async def sign_out(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Sign out user
    """
    try:
        supabase.auth.sign_out()
        return {"message": "Signed out successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Dependency to get current authenticated user
    """
    try:
        # Verify token
        user = supabase.auth.get_user(credentials.credentials)
        
        if user:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
