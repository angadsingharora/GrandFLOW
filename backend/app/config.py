# backend/app/config.py

import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings:
    """
    Application configuration settings
    """
    
    # Application
    APP_NAME: str = "GranFlow"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-turbo")
    
    # Fish Audio (TTS)
    FISH_AUDIO_API_KEY: str = os.getenv("FISH_AUDIO_API_KEY", "")
    FISH_AUDIO_VOICE_ID: str = os.getenv("FISH_AUDIO_VOICE_ID", "")
    
    # Twilio (Voice)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # API Keys (Mock for hackathon)
    UBER_API_KEY: str = os.getenv("UBER_API_KEY", "MOCK_KEY")
    LYFT_API_KEY: str = os.getenv("LYFT_API_KEY", "MOCK_KEY")
    DOORDASH_API_KEY: str = os.getenv("DOORDASH_API_KEY", "MOCK_KEY")
    INSTACART_API_KEY: str = os.getenv("INSTACART_API_KEY", "MOCK_KEY")
    
    # Wearable Data API
    SPIKE_API_KEY: str = os.getenv("SPIKE_API_KEY", "")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://*.vercel.app",
    ]
    
    # Scheduled Calls
    DAILY_CALL_TIME: str = os.getenv("DAILY_CALL_TIME", "09:00")  # 9 AM
    WEEKLY_COGNITIVE_TEST_DAY: int = int(os.getenv("WEEKLY_COGNITIVE_TEST_DAY", "1"))  # Monday
    
    # Call Settings
    MAX_CALL_DURATION_SECONDS: int = int(os.getenv("MAX_CALL_DURATION_SECONDS", "600"))  # 10 min
    RECORDING_ENABLED: bool = os.getenv("RECORDING_ENABLED", "True").lower() == "true"
    
    @classmethod
    def validate(cls):
        """
        Validate required settings
        """
        required = [
            ("SUPABASE_URL", cls.SUPABASE_URL),
            ("SUPABASE_KEY", cls.SUPABASE_KEY),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing = [name for name, value in required if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

settings = Settings()

# Validate on import
settings.validate()
