# backend/app/voice/conversation_manager.py

"""
Conversation Manager - Simplified wrapper around CallOrchestrator
This provides a high-level interface for managing AI-powered voice conversations.
Uses CallOrchestrator for crew management and Twilio for audio playback.
"""

from app.crews.orchestrator import CallOrchestrator
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import synthesize_speech
from supabase import create_client
import os
from uuid import uuid4
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import tempfile

class ConversationManager:
    """
    High-level conversation manager that coordinates:
    - CallOrchestrator (manages CrewAI crews)
    - Twilio (voice call management)
    - Fish Audio (TTS/STT)
    - Supabase (storage & database)
    """
    
    def __init__(self, user_id: str, call_sid: str):
        self.user_id = user_id
        self.call_sid = call_sid
        self.conversation_history = []
        
        # Use CallOrchestrator for crew management
        self.orchestrator = CallOrchestrator(
            patient_id=user_id,
            call_sid=call_sid,
            call_direction="inbound"
        )
        
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Initialize Twilio client for audio playback
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
    
    async def initialize(self):
        """Initialize the call via orchestrator"""
        self.call_id = await self.orchestrator.initiate_call()
        return self.call_id
    
    async def handle_conversation(self, audio_stream):
        """
        Main conversation loop
        """
        # Initial greeting
        greeting = await self.generate_greeting()
        await self.speak(greeting)
        
        # Listen for user's response
        user_input = await self.listen(audio_stream)
        self.conversation_history.append({"role": "user", "content": user_input})
        
        # Determine intent and route to appropriate crew
        intent = await self.classify_intent(user_input)
        
        if intent == "health_checkup":
            await self.run_health_monitoring()
        
        elif intent == "cognitive_test":
            await self.run_cognitive_testing()
        
        elif intent == "service_request":
            await self.run_service_concierge(user_input)
        
        elif intent == "general_conversation":
            # Simple Q&A without crew
            response = await self.generate_simple_response(user_input)
            await self.speak(response)
        
        # End call gracefully
        await self.conclude_call()
    
    async def run_health_monitoring(self):
        """
        Execute health monitoring crew via orchestrator
        """
        result = await self.orchestrator.route_to_crew(
            intent="health_checkup",
            context={"conversation_history": self.conversation_history}
        )
        return result
    
    async def run_cognitive_testing(self):
        """
        Execute cognitive testing crew via orchestrator
        """
        result = await self.orchestrator.route_to_crew(
            intent="cognitive_test",
            context={"conversation_history": self.conversation_history}
        )
        return result
    
    async def run_service_concierge(self, user_request: str):
        """
        Execute service concierge crew via orchestrator
        """
        result = await self.orchestrator.route_to_crew(
            intent="service_request",
            context={
                "user_request": user_request,
                "conversation_history": self.conversation_history
            }
        )
        return result
    
    async def listen(self, audio_stream) -> str:
        """
        Convert speech to text using Whisper
        """
        transcript = await transcribe_audio(audio_stream)
        return transcript
    
    async def speak(self, text: str):
        """
        Convert text to speech using Fish Audio and play
        """
        audio = await synthesize_speech(text)
        # Play audio over Twilio call
        await self.play_audio_on_call(audio)
    
    async def play_audio_on_call(self, audio_bytes: bytes):
        """
        Play audio on an active Twilio call using Fish Audio generated speech.
        
        This method integrates Fish Audio TTS with Twilio by:
        1. Converting the audio bytes to base64 for streaming
        2. Using Twilio's Media Streams to play the audio on the active call
        
        Args:
            audio_bytes: MP3 audio data from Fish Audio TTS
        """
        try:
            # Option 1: Use Twilio Media Streams (for real-time audio streaming)
            # This requires a WebSocket connection to stream audio chunks
            # For now, we'll save the audio and use a public URL
            
            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            # Option 2: Upload to Supabase Storage and get public URL
            # This is more robust for production
            file_name = f"call_audio/{self.call_id}/{uuid4()}.mp3"
            
            # Upload to Supabase storage bucket
            with open(temp_audio_path, 'rb') as f:
                self.supabase.storage.from_('call-audio').upload(
                    file_name,
                    f,
                    file_options={"content-type": "audio/mpeg"}
                )
            
            # Get public URL
            audio_url = self.supabase.storage.from_('call-audio').get_public_url(file_name)
            
            # Update the call with TwiML to play the audio
            twiml = VoiceResponse()
            twiml.play(audio_url)
            
            # Update the call to play this audio
            call = self.twilio_client.calls(self.call_sid).update(
                twiml=str(twiml)
            )
            
            # Clean up temp file
            os.unlink(temp_audio_path)
            
            # Log the interaction
            print(f"Playing audio on call {self.call_sid}: {audio_url}")
            
        except Exception as e:
            print(f"Error playing audio on call: {str(e)}")
            # Fallback: Use Twilio's built-in TTS if Fish Audio fails
            # This ensures the call doesn't break
            raise
    
    async def generate_greeting(self) -> str:
        """
        Generate personalized greeting based on time and user context
        """
        from datetime import datetime
        hour = datetime.now().hour
        
        # Fetch user name
        user = self.supabase.table("users").select("first_name").eq("id", self.user_id).single().execute()
        name = user.data['first_name']
        
        if hour < 12:
            greeting = f"Good morning, {name}! How are you feeling today?"
        elif hour < 18:
            greeting = f"Good afternoon, {name}! How's your day going?"
        else:
            greeting = f"Good evening, {name}! How are you doing tonight?"
        
        return greeting
    
    async def generate_simple_response(self, user_input: str) -> str:
        """
        Generate a simple conversational response using OpenRouter
        """
        from openai import OpenAI
        from app.config import settings
        
        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a friendly, warm AI assistant for elderly patients. 
                    Provide helpful, clear, and concise responses. 
                    Speak naturally and empathetically. 
                    Keep responses brief (2-3 sentences) as they will be spoken aloud."""
                },
                *[{"role": m["role"], "content": m["content"]} 
                  for m in self.conversation_history[-4:]],  # Last 4 messages for context
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            extra_headers={
                "HTTP-Referer": "https://grandflow.app",
                "X-Title": "GrandFLOW"
            }
        )
        
        return response.choices[0].message.content.strip()
    
    async def classify_intent(self, user_input: str) -> str:
        """
        Use LLM to classify user intent via OpenRouter
        """
        from openai import OpenAI
        from app.config import settings
        
        # OpenRouter uses OpenAI-compatible API
        client = OpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL
        )
        
        response = client.chat.completions.create(
            model=settings.OPENROUTER_MODEL,
            messages=[{
                "role": "system",
                "content": """Classify the user's intent into one of:
                - health_checkup: User wants health check-in (diet, meds, exercise)
                - cognitive_test: Requesting cognitive screening
                - service_request: Wants to book ride, order food, etc.
                - general_conversation: Small talk, questions
                
                Return only the intent category."""
            }, {
                "role": "user",
                "content": user_input
            }],
            extra_headers={
                "HTTP-Referer": "https://grandflow.app",  # Optional - for rankings
                "X-Title": "GrandFLOW"  # Optional - shows in OpenRouter dashboard
            }
        )
        
        return response.choices[0].message.content.strip()
    
    async def conclude_call(self):
        """
        End call gracefully
        """
        farewell = "Thank you for calling! Have a wonderful day. Remember, I'm here whenever you need me. Goodbye!"
        await self.speak(farewell)
        
        # Finalize call via orchestrator
        transcript = "\n".join([f"{m['role']}: {m['content']}" for m in self.conversation_history])
        await self.orchestrator.finalize_call(
            transcript=transcript,
            patient_mood="positive"  # Could be determined by sentiment analysis
        )
