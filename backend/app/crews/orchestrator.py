# backend/app/crews/orchestrator.py

from crewai import Agent, Task, Crew, Process
from app.crews.health_monitoring import create_health_monitoring_crew
from app.crews.cognitive_testing import create_cognitive_testing_crew
from app.crews.service_concierge import create_service_concierge_crew
from app.tools.database_tools import (
    log_call_start, log_call_end, update_call_agents
)
from typing import Dict, List
from datetime import datetime, date

class CallOrchestrator:
    """
    Master orchestrator that coordinates all agent crews during a call
    """
    
    def __init__(self, patient_id: str, call_sid: str, call_direction: str):
        self.patient_id = patient_id
        self.call_sid = call_sid
        self.call_direction = call_direction
        self.call_id = None
        self.conversation_history = []
        self.agents_involved = []
        
    async def initiate_call(self) -> str:
        """
        Initialize call and create call log entry
        """
        # Log call start
        self.call_id = log_call_start(
            patient_id=self.patient_id,
            call_sid=self.call_sid,
            call_direction=self.call_direction
        )
        
        return self.call_id
    
    async def route_to_crew(self, intent: str, context: Dict = None) -> Dict:
        """
        Route conversation to appropriate crew based on intent
        
        Args:
            intent: Detected intent (health_checkup, cognitive_test, service_request)
            context: Additional context for the crew
            
        Returns:
            Crew execution result
        """
        result = {}
        
        if intent == "health_checkup":
            result = await self._run_health_monitoring(context)
        
        elif intent == "cognitive_test":
            result = await self._run_cognitive_testing(context)
        
        elif intent == "service_request":
            result = await self._run_service_concierge(context)
        
        return result
    
    async def _run_health_monitoring(self, context: Dict) -> Dict:
        """
        Execute health monitoring crew
        """
        # Create crew
        crew = create_health_monitoring_crew(
            patient_id=self.patient_id,
            call_id=self.call_id
        )
        
        # Update call log
        update_call_agents(self.call_id, "health_monitoring")
        self.agents_involved.append("health_monitoring")
        
        # Execute crew
        result = crew.kickoff(inputs={
            "patient_id": self.patient_id,
            "call_id": self.call_id,
            "context": context or {}
        })
        
        return {
            "crew": "health_monitoring",
            "status": "completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _run_cognitive_testing(self, context: Dict) -> Dict:
        """
        Execute cognitive testing crew
        """
        crew = create_cognitive_testing_crew(
            patient_id=self.patient_id,
            call_id=self.call_id
        )
        
        update_call_agents(self.call_id, "cognitive_testing")
        self.agents_involved.append("cognitive_testing")
        
        result = crew.kickoff(inputs={
            "patient_id": self.patient_id,
            "call_id": self.call_id,
            "context": context or {}
        })
        
        return {
            "crew": "cognitive_testing",
            "status": "completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _run_service_concierge(self, context: Dict) -> Dict:
        """
        Execute service concierge crew
        """
        crew = create_service_concierge_crew(
            patient_id=self.patient_id,
            call_id=self.call_id
        )
        
        update_call_agents(self.call_id, "service_concierge")
        self.agents_involved.append("service_concierge")
        
        result = crew.kickoff(inputs={
            "patient_id": self.patient_id,
            "call_id": self.call_id,
            "user_request": context.get("user_request", ""),
            "context": context or {}
        })
        
        return {
            "crew": "service_concierge",
            "status": "completed",
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    async def finalize_call(self, transcript: str, patient_mood: str) -> Dict:
        """
        Finalize call and update call log
        """
        log_call_end(
            call_id=self.call_id,
            transcript=transcript,
            patient_mood=patient_mood
        )
        
        return {
            "call_id": self.call_id,
            "agents_involved": self.agents_involved,
            "status": "completed",
            "ended_at": datetime.now().isoformat()
        }
    
    def should_run_cognitive_test(self, patient: Dict) -> bool:
        """
        Determine if cognitive test should be run this call
        
        Rules:
        - Weekly on specified day (e.g., every Monday)
        - Or if 7+ days since last test
        """
        from app.database import supabase
        
        # Get last cognitive test
        result = supabase.table("cognitive_test_reports")\
            .select("test_date")\
            .eq("patient_id", self.patient_id)\
            .order("test_date", desc=True)\
            .limit(1)\
            .execute()
        
        if not result.data:
            return True  # No previous test
        
        last_test_date = date.fromisoformat(result.data[0]['test_date'])
        days_since = (date.today() - last_test_date).days
        
        return days_since >= 7
