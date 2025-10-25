# backend/app/voice/voice_handler.py

from fastapi import Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Say
from twilio.rest import Client as TwilioClient
from app.database import get_patient_by_phone, supabase
from app.crews.orchestrator import CallOrchestrator
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import synthesize_speech
from typing import Dict, Optional
import asyncio
from datetime import datetime
from uuid import uuid4
import tempfile
import os

class VoiceCallHandler:
    """
    Handles Twilio voice call webhooks and manages conversation flow
    """
    
    def __init__(self):
        self.active_calls: Dict[str, CallOrchestrator] = {}
        
        # Initialize Twilio client for call management
        from app.config import settings
        self.twilio_client = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
    
    async def handle_incoming_call(self, request: Request) -> Response:
        """
        Handle incoming call from Twilio
        """
        form_data = await request.form()
        caller_number = form_data.get("From")
        call_sid = form_data.get("CallSid")
        
        # Lookup patient by phone number
        patient = await get_patient_by_phone(caller_number)
        
        if not patient:
            # Unknown caller
            response = VoiceResponse()
            response.say(
                "Sorry, we don't recognize your phone number. Please contact support.",
                voice="Polly.Joanna"
            )
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        # Create orchestrator for this call
        orchestrator = CallOrchestrator(
            patient_id=patient['id'],
            call_sid=call_sid,
            call_direction="inbound_patient"
        )
        
        await orchestrator.initiate_call()
        
        # Store in active calls
        self.active_calls[call_sid] = orchestrator
        
        # Generate greeting
        greeting = self._generate_greeting(patient)
        
        # Create Twilio response
        response = VoiceResponse()
        response.say(greeting, voice="Polly.Joanna")
        
        # Gather user input
        gather = Gather(
            input='speech',
            action='/voice/process-input',
            method='POST',
            timeout=5,
            speechTimeout='auto',
            language='en-US'
        )
        gather.say("How can I help you today?", voice="Polly.Joanna")
        response.append(gather)
        
        # If no input, prompt again
        response.redirect('/voice/conversation')
        
        return Response(content=str(response), media_type="application/xml")
    
    async def handle_outbound_call(self, patient_id: str, call_type: str = "scheduled") -> Dict:
        """
        Initiate outbound call to patient
        
        Args:
            patient_id: Patient UUID
            call_type: "scheduled", "followup"
            
        Returns:
            Call initiation result
        """
        from twilio.rest import Client
        from app.config import settings
        
        # Get patient info
        patient = await supabase.table("patients").select("*").eq("id", patient_id).single().execute()
        patient_data = patient.data
        
        # Initialize Twilio client
        twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        # Make call
        call = twilio_client.calls.create(
            to=patient_data['phone_number'],
            from_=settings.TWILIO_PHONE_NUMBER,
            url=f"{settings.API_BASE_URL}/voice/outbound-greeting?patient_id={patient_id}&call_type={call_type}",
            method='POST',
            status_callback=f"{settings.API_BASE_URL}/voice/call-status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        return {
            "call_sid": call.sid,
            "status": call.status,
            "patient_id": patient_id,
            "call_type": call_type
        }
    
    async def process_user_input(self, request: Request) -> Response:
        """
        Process transcribed user speech and route to appropriate crew
        """
        form_data = await request.form()
        user_speech = form_data.get("SpeechResult", "")
        call_sid = form_data.get("CallSid")
        
        # Get orchestrator for this call
        orchestrator = self.active_calls.get(call_sid)
        
        if not orchestrator:
            # Call not found, likely timed out
            response = VoiceResponse()
            response.say("Sorry, there was an error. Please call again.", voice="Polly.Joanna")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        # Classify intent
        intent = await self._classify_intent(user_speech)
        
        # Route to appropriate crew
        crew_result = await orchestrator.route_to_crew(
            intent=intent,
            context={"user_input": user_speech}
        )
        
        # Generate response (for now, simple acknowledgment)
        response = VoiceResponse()
        response.say(
            f"Thank you. I've recorded your {intent.replace('_', ' ')}.",
            voice="Polly.Joanna"
        )
        
        # Ask if anything else needed
        gather = Gather(
            input='speech',
            action='/voice/process-input',
            method='POST',
            timeout=5
        )
        gather.say("Is there anything else I can help with?", voice="Polly.Joanna")
        response.append(gather)
        
        # If no, end call
        response.say("Thank you for calling. Have a wonderful day!", voice="Polly.Joanna")
        response.hangup()
        
        return Response(content=str(response), media_type="application/xml")
    
    def _generate_greeting(self, patient: Dict) -> str:
        """
        Generate personalized greeting based on time and patient
        """
        from datetime import datetime
        
        hour = datetime.now().hour
        first_name = patient['first_name']
        
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        return f"{time_greeting}, {first_name}! This is GranFlow, your health companion."
    
    async def _classify_intent(self, user_input: str) -> str:
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
            messages=[
                {
                    "role": "system",
                    "content": """Classify the user's intent into one of:
                    - health_checkup: User wants health check-in (diet, meds, exercise, symptoms)
                    - cognitive_test: Requesting cognitive screening
                    - service_request: Wants to book ride, order food, groceries, etc.
                    - general_question: General questions or conversation
                    
                    Return only the intent category, nothing else."""
                },
                {
                    "role": "user",
                    "content": user_input
                }
            ],
            temperature=0,
            extra_headers={
                "HTTP-Referer": "https://grandflow.app",
                "X-Title": "GrandFLOW"
            }
        )
        
        intent = response.choices[0].message.content.strip()
        return intent
    
    async def speak_with_fish_audio(self, text: str, call_sid: str) -> str:
        """
        Generate speech with Fish Audio and play on Twilio call
        
        Args:
            text: Text to speak
            call_sid: Active Twilio call SID
            
        Returns:
            Public URL of the audio file
        """
        try:
            # Generate audio with Fish Audio
            audio_bytes = await synthesize_speech(text)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio:
                temp_audio.write(audio_bytes)
                temp_audio_path = temp_audio.name
            
            # Upload to Supabase storage
            call_id = self.active_calls.get(call_sid).call_id if call_sid in self.active_calls else str(uuid4())
            file_name = f"call_audio/{call_id}/{uuid4()}.mp3"
            
            with open(temp_audio_path, 'rb') as f:
                supabase.storage.from_('call-audio').upload(
                    file_name,
                    f,
                    file_options={"content-type": "audio/mpeg"}
                )
            
            # Get public URL
            audio_url = supabase.storage.from_('call-audio').get_public_url(file_name)
            
            # Update call to play audio
            twiml = VoiceResponse()
            twiml.play(audio_url)
            
            self.twilio_client.calls(call_sid).update(twiml=str(twiml))
            
            # Clean up temp file
            os.unlink(temp_audio_path)
            
            return audio_url
            
        except Exception as e:
            print(f"Error playing Fish Audio on call: {str(e)}")
            # Fallback to Twilio TTS
            twiml = VoiceResponse()
            twiml.say(text, voice="Polly.Joanna")
            self.twilio_client.calls(call_sid).update(twiml=str(twiml))
            return None

# Global handler instance
voice_handler = VoiceCallHandler()
