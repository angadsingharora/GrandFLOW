# backend/app/voice/speech_to_text.py

import openai
import io

async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Transcribe audio using OpenAI Whisper
    """
    client = openai.OpenAI()
    
    # Convert bytes to file-like object
    audio_file = io.BytesIO(audio_bytes)
    audio_file.name = "audio.wav"
    
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        language="en"
    )
    
    return transcript.text
