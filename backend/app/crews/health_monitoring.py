# backend/app/crews/health_monitoring.py

"""
Health Monitoring Crew with Memory for Multi-Turn Conversations

This crew uses CrewAI agents with memory=True to have natural
conversations with patients, gradually collecting health data.
"""

from crewai import Agent, Task, Crew, Process
from app.tools.database_tools import (
    insert_diet_report, insert_medication_adherence, 
    insert_wellness_report, get_user_medical_profile, get_latest_vitals
)
from app.tools.health_analysis_tools import (
    calculate_diet_quality_score, calculate_exercise_quality_score,
    calculate_medication_adherence_rate, generate_health_recommendations
)


def create_health_monitoring_crew(patient_id: str, call_id: str, session: any):
    """
    Creates a crew for conversational health check-ins
    
    Args:
        patient_id: Patient UUID
        call_id: Call log UUID
        session: CallSession object for tracking accumulated data
    
    Returns:
        Crew with agents that have memory enabled
    """
    
    # Agent: Health Conversation Coordinator
    health_coordinator = Agent(
        role="Health Conversation Coordinator",
        goal=f"""Have a natural, empathetic conversation with the patient to collect their daily health information.
        Gather information about:
        - What they ate today (breakfast, lunch, dinner)
        - Vitamins and supplements taken
        - Medication adherence
        - Physical activity and exercise
        - Sleep quality and duration
        - Any symptoms or concerns
        
        Ask questions naturally, one at a time, like a caring doctor would.
        Listen to responses and ask follow-up questions to get complete information.
        Use the tools available to calculate health scores and save data.""",
        
        backstory="""You are an experienced geriatric health coordinator who specializes 
        in phone-based health check-ins for seniors. You have a warm, patient demeanor and 
        know how to have natural conversations that put people at ease. You ask one question 
        at a time, listen carefully to responses, and gently probe for details when needed. 
        You never rush the conversation and make the patient feel heard and cared for.""",
        
        tools=[
            get_user_medical_profile,
            get_latest_vitals,
            calculate_diet_quality_score,
            calculate_exercise_quality_score,
            calculate_medication_adherence_rate,
            generate_health_recommendations,
            insert_diet_report,
            insert_medication_adherence,
            insert_wellness_report
        ],
        
        verbose=True,
        memory=True,  # Enable memory to remember conversation context
        allow_delegation=False
    )
    
    # Task: Conversational Health Data Collection
    health_conversation_task = Task(
        description=f"""Have a natural conversation with the patient to collect their daily health information.

Patient ID: {patient_id}
Call ID: {call_id}

CONVERSATION GUIDELINES:
1. Start by asking how they're feeling today
2. Then naturally transition to asking about their meals:
   - "What did you have for breakfast this morning?"
   - Listen to response, then ask about lunch
   - Then ask about dinner
   - Ask if they took any vitamins or supplements

3. Ask about medications:
   - "Did you take your medications today?"
   - If they have prescribed medications, confirm each one

4. Ask about physical activity:
   - "Did you do any exercise or physical activity today?"
   - Ask about steps or walking
   - Ask how they slept last night

5. Ask about symptoms:
   - "Are you experiencing any pain, discomfort, or concerning symptoms?"

IMPORTANT:
- Ask ONE question at a time
- Wait for the patient's response before moving to the next topic
- Use the conversation history to remember what you've already asked
- Call the appropriate tools as you gather information:
  * calculate_diet_quality_score after getting meal info
  * calculate_exercise_quality_score after getting activity info  
  * calculate_medication_adherence_rate after medication discussion
  * generate_health_recommendations once you have all data
  * insert_diet_report, insert_wellness_report, insert_medication_adherence to save to database

- When you've collected all necessary information, summarize what you learned
  and provide 2-3 personalized recommendations

The conversation should feel natural and caring, not like filling out a form.

User's last message: {{user_input}}
""",
        agent=health_coordinator,
        expected_output="""A conversational response that either:
1. Asks the next natural question based on what you've learned so far
2. Acknowledges the patient's response and asks a follow-up question
3. Provides a warm summary and recommendations if all data has been collected

The response should be natural, empathetic, and appropriate for speaking over the phone."""
    )
    
    # Create crew with sequential process (one agent, conversational)
    crew = Crew(
        agents=[health_coordinator],
        tasks=[health_conversation_task],
        process=Process.sequential,
        verbose=True,
        memory=True  # Enable crew-level memory
    )
    
    return crew
