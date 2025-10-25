# backend/app/voice/text_to_speech.py

import aiohttp
import os

async def synthesize_speech(text: str) -> bytes:
    """
    Convert text to speech using Fish Audio API
    
    Fish Audio API: https://fish.audio/docs/api
    """
    FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")
    FISH_AUDIO_VOICE_ID = os.getenv("FISH_AUDIO_VOICE_ID")  # Senior-friendly voice
    
    url = "https://api.fish.audio/v1/tts"
    
    headers = {
        "Authorization": f"Bearer {FISH_AUDIO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "text": text,
        "voice_id": FISH_AUDIO_VOICE_ID,  # Use warm, mature voice
        "format": "mp3",
        "sample_rate": 24000,
        "speed": 0.9  # Slightly slower for clarity
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as response:
            if response.status == 200:
                audio_data = await response.read()
                return audio_data
            else:
                raise Exception(f"Fish Audio API error: {response.status}")

