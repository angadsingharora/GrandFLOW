# backend/app/voice/speech_to_text.py

import aiohttp
import os
from io import BytesIO

async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio using Fish Audio STT API
    
    Fish Audio provides speech-to-text capabilities using Whisper models
    API: https://fish.audio/docs/api
    """
    FISH_AUDIO_API_KEY = os.getenv("FISH_AUDIO_API_KEY")
    FISH_AUDIO_STT_MODEL = os.getenv("FISH_AUDIO_STT_MODEL", "whisper-large-v3")
    
    # Fish Audio STT endpoint
    url = "https://api.fish.audio/v1/asr"
    
    headers = {
        "Authorization": f"Bearer {FISH_AUDIO_API_KEY}"
    }
    
    # Prepare form data with audio file
    form_data = aiohttp.FormData()
    form_data.add_field(
        'audio',
        audio_bytes,
        filename='audio.wav',
        content_type='audio/wav'
    )
    form_data.add_field('model', FISH_AUDIO_STT_MODEL)
    form_data.add_field('language', 'en')
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=form_data) as response:
            if response.status == 200:
                result = await response.json()
                # Extract transcription text from response
                # Response format: {"text": "transcribed text", ...}
                return result.get("text", "")
            else:
                error_text = await response.text()
                raise Exception(f"Fish Audio STT API error: {response.status} - {error_text}")
