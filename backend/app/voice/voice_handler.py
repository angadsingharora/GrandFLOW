# backend/app/voice/voice_handler.py

"""
Voice Handler for CrewAI Conversational Loops

Handles Twilio webhooks and manages multi-turn conversations
with CrewAI agents that have memory.
"""

from fastapi import Request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client as TwilioClient
from app.database import get_patient_by_phone, supabase
from app.crews.orchestrator import CallOrchestrator
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import synthesize_speech
from typing import Dict, Optional
from datetime import datetime
from uuid import uuid4
import tempfile
import os


class VoiceCallHandler:
    """
    Handles Twilio voice call webhooks and manages CrewAI conversations
    
    Flow:
    1. Call initiated → Create orchestrator → Start crew conversation
    2. Agent asks question → TTS → Play to user
    3. User responds → STT → Back to crew
    4. Crew processes with memory → Asks follow-up or calls tools
    5. Loop continues until crew completes conversation
    6. Finalize and save all data to database
    """
    
    def __init__(self):
        # Active orchestrators mapped by call_sid
        self.active_orchestrators: Dict[str, CallOrchestrator] = {}
        
        # Initialize Twilio client
        from app.config import settings
        self.twilio_client = TwilioClient(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
    
    async def handle_outbound_call(
        self,
        patient_id: str,
        call_type: str = "health_checkup"
    ) -> Dict:
        """
        Initiate outbound call to patient
        
        Args:
            patient_id: Patient UUID
            call_type: Type of call (health_checkup, cognitive_test)
        
        Returns:
            Dict with call initiation result
        """
        from app.config import settings
        
        # Get patient info
        patient = await supabase.table("patients").select("*").eq("id", patient_id).single().execute()
        patient_data = patient.data
        
        # Make call with Twilio
        call = self.twilio_client.calls.create(
            to=patient_data['phone_number'],
            from_=settings.TWILIO_PHONE_NUMBER,
            url=f"{settings.API_BASE_URL}/voice/outbound-start?patient_id={patient_id}&call_type={call_type}",
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
    
    async def handle_outbound_start(self, request: Request) -> Response:
        """
        Handle outbound call connection and start CrewAI conversation
        
        This is called when Twilio connects the outbound call
        """
        from urllib.parse import parse_qs
        
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        
        # Get parameters from URL
        query_string = str(request.url).split('?')[1] if '?' in str(request.url) else ""
        params = parse_qs(query_string)
        patient_id = params.get('patient_id', [None])[0]
        call_type = params.get('call_type', ['health_checkup'])[0]
        
        if not patient_id:
            response = VoiceResponse()
            response.say("Error: Patient information not found.", voice="Polly.Joanna")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        # Get patient for greeting
        patient = await supabase.table("patients").select("*").eq("id", patient_id).single().execute()
        patient_data = patient.data
        
        # Create orchestrator and start conversation
        orchestrator = CallOrchestrator(
            patient_id=patient_id,
            call_sid=call_sid,
            call_direction=f"outbound_{call_type}"
        )
        
        # Store orchestrator
        self.active_orchestrators[call_sid] = orchestrator
        
        # Initialize call and get first agent response
        init_result = await orchestrator.initiate_call(call_type=call_type)
        
        if not init_result.get("success"):
            response = VoiceResponse()
            response.say("I'm having trouble starting the conversation. Let me try again.", voice="Polly.Joanna")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        # Generate greeting
        greeting = self._generate_greeting(patient_data)
        agent_first_message = init_result.get("agent_response", "")
        
        # Create TwiML response
        response = VoiceResponse()
        response.say(greeting, voice="Polly.Joanna")
        response.pause(length=1)
        response.say(agent_first_message, voice="Polly.Joanna")
        
        # Gather user response
        gather = Gather(
            input='speech',
            action='/voice/conversation',
            method='POST',
            timeout=10,
            speechTimeout='auto',
            language='en-US'
        )
        gather.say("", voice="Polly.Joanna")  # Pause for response
        response.append(gather)
        
        # Fallback if no response
        response.say("I didn't hear that. Let me ask again.", voice="Polly.Joanna")
        response.redirect('/voice/conversation')
        
        return Response(content=str(response), media_type="application/xml")
    
    async def handle_conversation(self, request: Request) -> Response:
        """
        Main conversation loop handler
        
        Receives user response, feeds to CrewAI, gets agent response, continues loop
        """
        form_data = await request.form()
        user_speech = form_data.get("SpeechResult", "")
        call_sid = form_data.get("CallSid")
        
        # Get orchestrator
        orchestrator = self.active_orchestrators.get(call_sid)
        if not orchestrator:
            response = VoiceResponse()
            response.say("I'm sorry, I lost track of our conversation.", voice="Polly.Joanna")
            response.hangup()
            return Response(content=str(response), media_type="application/xml")
        
        # Process user response through crew
        result = await orchestrator.process_user_response(user_speech)
        
        if not result.get("success"):
            # Error - retry
            response = VoiceResponse()
            response.say("I'm sorry, I didn't quite get that. Could you repeat?", voice="Polly.Joanna")
            
            gather = Gather(
                input='speech',
                action='/voice/conversation',
                method='POST',
                timeout=10,
                speechTimeout='auto',
                language='en-US'
            )
            gather.say("", voice="Polly.Joanna")
            response.append(gather)
            
            return Response(content=str(response), media_type="application/xml")
        
        # Get agent's response
        agent_response = result.get("agent_response", "")
        is_complete = result.get("completed", False)
        
        # Create TwiML response
        response = VoiceResponse()
        response.say(agent_response, voice="Polly.Joanna")
        
        if is_complete:
            # Conversation is complete
            response.pause(length=1)
            response.say("Thank you for your time today. Take care!", voice="Polly.Joanna")
            
            # Finalize call
            await orchestrator.finalize_call()
            
            # Clean up
            if call_sid in self.active_orchestrators:
                del self.active_orchestrators[call_sid]
            
            response.hangup()
        else:
            # Continue conversation
            gather = Gather(
                input='speech',
                action='/voice/conversation',
                method='POST',
                timeout=10,
                speechTimeout='auto',
                language='en-US'
            )
            gather.say("", voice="Polly.Joanna")
            response.append(gather)
            
            # Fallback
            response.say("Are you still there?", voice="Polly.Joanna")
            response.redirect('/voice/conversation')
        
        return Response(content=str(response), media_type="application/xml")
    
    async def handle_call_status(self, request: Request) -> Response:
        """Handle call status updates from Twilio"""
        form_data = await request.form()
        call_sid = form_data.get("CallSid")
        call_status = form_data.get("CallStatus")
        
        print(f"Call {call_sid} status: {call_status}")
        
        # Clean up if call ended
        if call_status in ["completed", "busy", "no-answer", "failed", "canceled"]:
            if call_sid in self.active_orchestrators:
                orchestrator = self.active_orchestrators.pop(call_sid)
                # Try to finalize if not already done
                try:
                    await orchestrator.finalize_call()
                except:
                    pass
        
        return Response(content="OK", media_type="text/plain")
    
    def _generate_greeting(self, patient: Dict) -> str:
        """Generate personalized greeting"""
        hour = datetime.now().hour
        first_name = patient.get('first_name', 'there')
        
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        return f"{time_greeting}, {first_name}! This is your GrandFLOW health assistant."


# Global handler instance
voice_handler = VoiceCallHandler()
