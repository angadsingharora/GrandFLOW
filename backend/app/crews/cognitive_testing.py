# backend/app/crews/cognitive_testing.py

"""
Cognitive Testing Crew with Memory for Multi-Turn TICS Administration

This crew uses CrewAI agents with memory=True to administer the TICS
cognitive test through natural conversation.
"""

from crewai import Agent, Task, Crew, Process
from app.tools.database_tools import insert_cognitive_test_report, get_user_medical_profile
from app.tools.cognitive_test_tools import (
    administer_tics_test, convert_tics_to_mmse,
    calculate_cognitive_quality_score, determine_cognitive_risk_level,
    generate_cognitive_recommendations
)


def create_cognitive_testing_crew(patient_id: str, call_id: str, session: any):
    """
    Creates a crew for administering TICS cognitive test conversationally
    
    Args:
        patient_id: Patient UUID
        call_id: Call log UUID
        session: CallSession object for tracking test progress
    
    Returns:
        Crew with cognitive assessment agent with memory
    """
    
    # Agent: Cognitive Assessment Specialist
    cognitive_specialist = Agent(
        role="Cognitive Assessment Specialist",
        goal=f"""Administer the Telephone Interview for Cognitive Status (TICS) test through 
        natural conversation. Ask questions one at a time, score responses, and provide 
        supportive feedback throughout. Make the patient feel comfortable and not tested.""",
        
        backstory="""You are a skilled neuropsychologist with 20 years of experience in 
        dementia screening and cognitive assessment. You specialize in phone-based testing 
        and have a gentle, reassuring manner that puts seniors at ease. You know how to 
        administer standardized tests while making them feel like a natural conversation. 
        You're patient, clear in your speech, and excellent at providing encouragement 
        without giving away answers.""",
        
        tools=[
            administer_tics_test,
            convert_tics_to_mmse,
            calculate_cognitive_quality_score,
            determine_cognitive_risk_level,
            generate_cognitive_recommendations,
            insert_cognitive_test_report,
            get_user_medical_profile
        ],
        
        verbose=True,
        memory=True,  # Remember the conversation and test progress
        allow_delegation=False
    )
    
    # Task: TICS Test Administration
    tics_administration_task = Task(
        description=f"""Administer the TICS cognitive test through conversational questions.

Patient ID: {patient_id}
Call ID: {call_id}

TICS TEST PROTOCOL:
Use administer_tics_test tool to get the test structure, then proceed through sections:

1. ORIENTATION (5 points):
   - Ask: "What is today's date?" (day, month, year - 3 points)
   - Ask: "What day of the week is it?" (1 point)
   - Ask: "What season are we in?" (1 point)

2. REGISTRATION (3 points):
   - Say: "I'm going to say 3 words. Please repeat them back to me: APPLE, TABLE, PENNY"
   - Award 1 point for each word repeated correctly

3. ATTENTION/CALCULATION (5 points):
   - Ask: "Starting at 100, subtract 7. What is 100 minus 7?"
   - Continue: "Now subtract 7 from that number" (repeat 5 times)
   - Award 1 point for each correct answer (93, 86, 79, 72, 65)

4. RECALL (3 points):
   - Ask: "Do you remember those 3 words I asked you to repeat earlier?"
   - Award 1 point for each word recalled (apple, table, penny)

5. NAMING (2 points):
   - Ask: "What do you call the thing you use to tell time?" (watch/clock)
   - Ask: "What do you call the thing you write with?" (pen/pencil)

6. REPETITION (1 point):
   - Say: "Please repeat this phrase: NO IFS, ANDS, OR BUTS"
   - Award 1 point if repeated correctly

7. COMPREHENSION (3 points):
   - Say: "With your right hand, touch your left ear. Did you do that?"
   - Say: "Now touch your nose. Did you do that?"
   - Say: "Now touch your right shoulder. Did you do that?"
   - Award 1 point for each command followed

IMPORTANT GUIDELINES:
- Ask ONE question at a time
- Wait for the patient's response before continuing
- Use your memory to track which questions you've asked and the scores
- Be patient and repeat questions if needed
- Provide gentle encouragement ("That's great", "You're doing well")
- DON'T tell them if answers are wrong - just move to the next question
- After completing all sections:
  * Use convert_tics_to_mmse to convert the total score
  * Use calculate_cognitive_quality_score to get normalized score
  * Use determine_cognitive_risk_level to classify results
  * Use generate_cognitive_recommendations to provide guidance
  * Use insert_cognitive_test_report to save to database

- End with a warm, reassuring summary regardless of performance

User's last message: {{user_input}}
""",
        agent=cognitive_specialist,
        expected_output="""A conversational response that either:
1. Asks the next TICS test question naturally
2. Acknowledges the response and moves to the next section
3. Provides encouragement and transitions between test sections
4. Gives a final summary with results and recommendations (after completing all sections)

The response should be clear, warm, and appropriate for phone conversation."""
    )
    
    # Create crew
    crew = Crew(
        agents=[cognitive_specialist],
        tasks=[tics_administration_task],
        process=Process.sequential,
        verbose=True,
        memory=True
    )
    
    return crew
