# backend/app/voice/conversation_manager.py

from crewai import Crew
from app.crews.health_monitoring import create_health_monitoring_crew
from app.crews.cognitive_testing import create_cognitive_testing_crew
from app.crews.service_concierge import create_service_concierge_crew
from app.voice.speech_to_text import transcribe_audio
from app.voice.text_to_speech import synthesize_speech
from supabase import create_client
import os
from uuid import uuid4

class ConversationManager:
    def __init__(self, user_id: str, call_sid: str):
        self.user_id = user_id
        self.call_sid = call_sid
        self.call_id = str(uuid4())
        self.conversation_history = []
        self.current_crew = None
        
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Log call start
        self.log_call_start()
    
    def log_call_start(self):
        """Create call log entry"""
        self.supabase.table("call_logs").insert({
            "id": self.call_id,
            "user_id": self.user_id,
            "call_sid": self.call_sid,
            "started_at": "NOW()",
            "agents_involved": []
        }).execute()
    
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
        Execute health monitoring crew
        """
        crew = create_health_monitoring_crew(self.user_id, self.call_id)
        self.current_crew = crew
        
        # Run crew (it will conduct the check-in conversation)
        result = crew.kickoff()
        
        # Log crew activity
        self.log_agent_activity("health_monitoring", result)
    
    async def run_cognitive_testing(self):
        """
        Execute cognitive testing crew (weekly)
        """
        crew = create_cognitive_testing_crew(self.user_id, self.call_id)
        self.current_crew = crew
        
        result = crew.kickoff()
        self.log_agent_activity("cognitive_testing", result)
    
    async def run_service_concierge(self, user_request: str):
        """
        Execute service concierge crew
        """
        crew = create_service_concierge_crew(self.user_id, self.call_id)
        self.current_crew = crew
        
        # Pass user request to crew
        result = crew.kickoff(inputs={"user_request": user_request})
        self.log_agent_activity("service_concierge", result)
    
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
    
    async def classify_intent(self, user_input: str) -> str:
        """
        Use LLM to classify user intent
        """
        from openai import OpenAI
        client = OpenAI()
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
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
            }]
        )
        
        return response.choices[0].message.content.strip()
    
    def log_agent_activity(self, agent_type: str, result):
        """
        Log which agents were involved and what tasks completed
        """
        self.supabase.table("call_logs").update({
            "agents_involved": self.supabase.raw("array_append(agents_involved, %s)", agent_type),
            "tasks_completed": self.supabase.raw("array_append(tasks_completed, %s)", {
                "agent": agent_type,
                "timestamp": "NOW()",
                "result": str(result)
            })
        }).eq("id", self.call_id).execute()
    
    async def conclude_call(self):
        """
        End call gracefully
        """
        farewell = "Thank you for calling! Have a wonderful day. Remember, I'm here whenever you need me. Goodbye!"
        await self.speak(farewell)
        
        # Update call log
        self.supabase.table("call_logs").update({
            "ended_at": "NOW()",
            "transcript": "\n".join([f"{m['role']}: {m['content']}" for m in self.conversation_history])
        }).eq("id", self.call_id).execute()
