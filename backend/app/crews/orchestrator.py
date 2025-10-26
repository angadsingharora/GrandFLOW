# backend/app/crews/orchestrator.py

"""
Call Orchestrator for CrewAI Conversational Loops

Manages call initiation, crew selection, and conversation routing
for multi-turn conversations with CrewAI agents.
"""

from typing import Dict, Any
from datetime import datetime

from app.tools.database_tools import log_call_start, update_call_agents
from app.voice.conversation_loop import conversation_loop


class CallOrchestrator:
    """
    Orchestrates calls and manages CrewAI conversation loops
    
    This class:
    - Initiates calls and creates call logs
    - Routes calls to appropriate crews based on type
    - Delegates to ConversationLoopHandler for multi-turn conversations
    - Manages conversation state across webhook calls
    """
    
    def __init__(self, patient_id: str, call_sid: str, call_direction: str):
        self.patient_id = patient_id
        self.call_sid = call_sid
        self.call_direction = call_direction
        self.call_id = None
        self.call_type = None
    
    async def initiate_call(self, call_type: str = "health_checkup") -> Dict[str, Any]:
        """
        Initialize call and start conversation with appropriate crew
        
        Args:
            call_type: Type of call (health_checkup, cognitive_test, etc.)
        
        Returns:
            Dict with call_id and initial agent response
        """
        self.call_type = call_type
        
        # Log call start in database
        self.call_id = log_call_start(
            patient_id=self.patient_id,
            call_sid=self.call_sid,
            call_direction=self.call_direction
        )
        
        # Update call log with agent type
        agent_type = self._get_agent_type_from_call_type(call_type)
        update_call_agents(self.call_id, agent_type)
        
        # Start conversation loop with appropriate crew
        result = await conversation_loop.initiate_conversation(
            call_sid=self.call_sid,
            patient_id=self.patient_id,
            call_id=self.call_id,
            call_type=call_type,
            call_direction=self.call_direction
        )
        
        return {
            "call_id": self.call_id,
            "success": result.get("success", False),
            "agent_response": result.get("agent_response", ""),
            "error": result.get("error")
        }
    
    async def process_user_response(self, user_input: str) -> Dict[str, Any]:
        """
        Process user response and continue conversation
        
        Args:
            user_input: User's spoken response (transcribed)
        
        Returns:
            Dict with agent response and conversation status
        """
        result = await conversation_loop.continue_conversation(
            call_sid=self.call_sid,
            user_input=user_input
        )
        
        return result
    
    async def finalize_call(self) -> Dict[str, Any]:
        """
        Finalize call and save all data
        
        Returns:
            Dict with finalization status
        """
        result = await conversation_loop.finalize_conversation(
            call_sid=self.call_sid
        )
        
        return result
    
    def _get_agent_type_from_call_type(self, call_type: str) -> str:
        """Map call type to agent type for logging"""
        mapping = {
            "health_checkup": "health_monitoring",
            "cognitive_test": "cognitive_testing",
            "service_request": "service_concierge"
        }
        return mapping.get(call_type, "unknown")
