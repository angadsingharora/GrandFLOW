# backend/app/voice/conversation_loop.py

"""
Conversational Loop Handler for Multi-Turn CrewAI Conversations

This module manages the conversational loop where:
1. User speaks → STT → Text
2. Text fed to CrewAI crew with memory
3. Crew processes, may call tools, generates response
4. Response → TTS → Played to user
5. Loop continues until crew indicates completion
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from app.voice.call_session import CallSession, CallSessionState, session_manager
from app.crews.health_monitoring import create_health_monitoring_crew
from app.crews.cognitive_testing import create_cognitive_testing_crew
from app.tools.database_tools import log_call_end


class ConversationLoopHandler:
    """
    Handles the multi-turn conversation loop with CrewAI
    
    Key responsibilities:
    - Maintain crew instances with memory across turns
    - Feed user input back to crew for continued conversation
    - Extract data from crew's tool calls and conversation
    - Detect when conversation is complete
    - Finalize and save all data to database
    """
    
    def __init__(self):
        pass
    
    async def initiate_conversation(
        self,
        call_sid: str,
        patient_id: str,
        call_id: str,
        call_type: str,
        call_direction: str
    ) -> Dict[str, Any]:
        """
        Start a new conversation with appropriate crew
        
        Args:
            call_sid: Twilio call SID
            patient_id: Patient UUID
            call_id: Call log UUID
            call_type: Type of call (health_checkup, cognitive_test)
            call_direction: Direction (outbound_scheduled, inbound_patient)
        
        Returns:
            Dict with initial agent response
        """
        
        # Create session
        session = session_manager.create_session(
            call_sid=call_sid,
            patient_id=patient_id,
            call_direction=call_direction,
            call_id=call_id,
            call_type=call_type
        )
        
        # Create appropriate crew with memory
        if call_type == "health_checkup":
            crew = create_health_monitoring_crew(patient_id, call_id, session)
        elif call_type == "cognitive_test":
            crew = create_cognitive_testing_crew(patient_id, call_id, session)
        else:
            raise ValueError(f"Unknown call type: {call_type}")
        
        # Store crew in session
        session.active_crew = crew
        session.state = CallSessionState.IN_CONVERSATION
        
        # Get initial greeting from crew
        initial_input = "Hello, I'm here for my call."
        
        try:
            result = crew.kickoff(inputs={"user_input": initial_input})
            
            # Extract agent's response
            agent_response = self._extract_response(result)
            
            # Track conversation
            session.add_turn(initial_input, agent_response)
            
            return {
                "success": True,
                "agent_response": agent_response,
                "turn_count": session.turn_count,
                "completed": False
            }
            
        except Exception as e:
            print(f"Error initiating conversation: {str(e)}")
            session.state = CallSessionState.FAILED
            return {
                "success": False,
                "error": str(e),
                "agent_response": "I'm sorry, I'm having trouble starting our conversation. Let me try again."
            }
    
    async def continue_conversation(
        self,
        call_sid: str,
        user_input: str
    ) -> Dict[str, Any]:
        """
        Continue an ongoing conversation with user input
        
        Args:
            call_sid: Twilio call SID
            user_input: User's spoken response (transcribed)
        
        Returns:
            Dict with agent response and completion status
        """
        
        # Get session
        session = session_manager.get_session(call_sid)
        if not session:
            return {
                "success": False,
                "error": "Session not found",
                "agent_response": "I'm sorry, I lost track of our conversation. Could we start over?"
            }
        
        # Check if crew exists
        if not session.active_crew:
            return {
                "success": False,
                "error": "No active crew",
                "agent_response": "I'm having trouble continuing our conversation."
            }
        
        try:
            # Feed user input back to crew
            # The crew's memory will maintain context
            result = session.active_crew.kickoff(inputs={"user_input": user_input})
            
            # Extract agent's response
            agent_response = self._extract_response(result)
            
            # Track conversation
            session.add_turn(user_input, agent_response)
            
            # Check for completion signals
            is_complete = self._detect_completion(agent_response, session)
            
            if is_complete:
                session.state = CallSessionState.FINALIZING
                # Finalize will happen in separate call
                return {
                    "success": True,
                    "agent_response": agent_response,
                    "turn_count": session.turn_count,
                    "completed": True,
                    "message": "Conversation complete, ready to finalize"
                }
            
            return {
                "success": True,
                "agent_response": agent_response,
                "turn_count": session.turn_count,
                "completed": False
            }
            
        except Exception as e:
            print(f"Error continuing conversation: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e),
                "agent_response": "I'm sorry, I didn't quite catch that. Could you repeat?"
            }
    
    async def finalize_conversation(
        self,
        call_sid: str
    ) -> Dict[str, Any]:
        """
        Finalize conversation and save all data to database
        
        Args:
            call_sid: Twilio call SID
        
        Returns:
            Dict with finalization status and summary
        """
        
        # Get and end session
        session = session_manager.end_session(call_sid)
        if not session:
            return {
                "success": False,
                "error": "Session not found"
            }
        
        try:
            # Update call log
            transcript = self._generate_transcript(session)
            patient_mood = self._assess_mood(session)
            
            log_call_end(
                call_id=session.call_id,
                transcript=transcript,
                patient_mood=patient_mood
            )
            
            session.state = CallSessionState.COMPLETED
            
            return {
                "success": True,
                "call_id": session.call_id,
                "turn_count": session.turn_count,
                "transcript": transcript,
                "patient_mood": patient_mood,
                "message": "Conversation finalized and data saved"
            }
            
        except Exception as e:
            print(f"Error finalizing conversation: {str(e)}")
            session.state = CallSessionState.FAILED
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_response(self, crew_result: Any) -> str:
        """
        Extract agent's conversational response from crew result
        
        CrewAI returns different formats, need to handle them
        """
        # If result is a string, return it
        if isinstance(crew_result, str):
            return crew_result
        
        # If result has output attribute
        if hasattr(crew_result, 'output'):
            return str(crew_result.output)
        
        # If result has raw_output
        if hasattr(crew_result, 'raw_output'):
            return str(crew_result.raw_output)
        
        # If result is a dict with output key
        if isinstance(crew_result, dict):
            if 'output' in crew_result:
                return crew_result['output']
            if 'result' in crew_result:
                return crew_result['result']
        
        # Fallback
        return str(crew_result)
    
    def _detect_completion(self, agent_response: str, session: CallSession) -> bool:
        """
        Detect if conversation should be completed
        
        Looks for completion signals in agent's response or session state
        """
        # Check for explicit completion phrases
        completion_phrases = [
            "thank you for sharing",
            "that completes our",
            "i've recorded everything",
            "we're all done",
            "that's all for today",
            "thank you for your time"
        ]
        
        response_lower = agent_response.lower()
        has_completion_phrase = any(phrase in response_lower for phrase in completion_phrases)
        
        # Check if enough turns have passed (safety limit)
        max_turns = 25 if session.call_type == "cognitive_test" else 15
        too_many_turns = session.turn_count >= max_turns
        
        # Check if session indicates data is complete
        data_complete = session.is_data_complete()
        
        return has_completion_phrase or too_many_turns or data_complete
    
    def _generate_transcript(self, session: CallSession) -> str:
        """Generate conversation transcript"""
        lines = []
        for turn in session.conversation_history:
            lines.append(f"Turn {turn['turn']}:")
            lines.append(f"Patient: {turn['user']}")
            lines.append(f"Agent: {turn['agent']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _assess_mood(self, session: CallSession) -> str:
        """
        Assess patient mood from conversation
        Simple heuristic based on responses
        """
        # Look for positive/negative indicators in patient responses
        positive_words = ["good", "great", "fine", "well", "better", "yes"]
        negative_words = ["bad", "not good", "pain", "tired", "difficult", "no"]
        
        positive_count = 0
        negative_count = 0
        
        for turn in session.conversation_history:
            user_response = turn['user'].lower()
            positive_count += sum(1 for word in positive_words if word in user_response)
            negative_count += sum(1 for word in negative_words if word in user_response)
        
        if positive_count > negative_count * 1.5:
            return "positive"
        elif negative_count > positive_count * 1.5:
            return "concerned"
        else:
            return "neutral"


# Global conversation loop handler
conversation_loop = ConversationLoopHandler()

