# backend/app/crews/cognitive_testing_crew.py

from crewai import Agent, Task, Crew
from app.tools.database_tools import insert_cognitive_test_report, get_user_medical_profile
from app.tools.cognitive_test_tools import administer_tics_test, convert_tics_to_mmse

def create_cognitive_testing_crew(user_id: str, call_id: str):
    """
    Creates a crew for weekly TICS cognitive screening
    """
    
    cognitive_agent = Agent(
        role="Cognitive Assessment Specialist",
        goal="Administer TICS test and assess cognitive function",
        backstory="""You are a neuropsychologist specialized in dementia screening.
        You administer the Telephone Interview for Cognitive Status (TICS) test,
        which is designed for phone-based assessment. You are warm, patient, and 
        explain that this is a routine check-up.""",
        tools=[insert_cognitive_test_report, get_user_medical_profile, 
               administer_tics_test, convert_tics_to_mmse],
        verbose=True
    )
    
    tics_task = Task(
        description=f"""
        Administer TICS cognitive test to user {user_id}.
        
        Test Components (use administer_tics_test tool):
        
        1. ORIENTATION (5 points):
           - What is today's date? (day, month, year)
           - What day of the week is it?
           - What season are we in?
        
        2. REGISTRATION (3 points):
           - "I'm going to say 3 words. Please repeat them: APPLE, TABLE, PENNY"
           - Award 1 point for each correct immediate recall
        
        3. ATTENTION & CALCULATION (5 points):
           - "Starting at 100, subtract 7. What is 100 minus 7?" (93)
           - "Subtract 7 from that number" (86)
           - Continue for 5 subtractions: 93, 86, 79, 72, 65
        
        4. DELAYED RECALL (3 points):
           - "Do you remember those 3 words I asked you to repeat earlier?"
           - Award 1 point for each word recalled (APPLE, TABLE, PENNY)
        
        5. NAMING (2 points):
           - "What do you call the thing you use to tell time?" (watch/clock)
           - "What do you call the thing you write with?" (pen/pencil)
        
        6. REPETITION (1 point):
           - "Please repeat this phrase: NO IFS, ANDS, OR BUTS"
        
        7. COMPREHENSION (3 points):
           - "I'm going to give you instructions. Listen carefully."
           - "With your right hand, touch your left ear"
           - "Then touch your nose"
           - "Then touch your right shoulder"
           - Award 1 point for each step completed correctly
        
        Scoring:
        - Total possible: 41 points
        - Convert to MMSE equivalent (TICS ≈ MMSE - 2)
        - Risk levels:
          * 35-41: Normal cognitive function
          * 31-34: Mild cognitive impairment
          * 21-30: Moderate impairment
          * <21: Severe impairment
        
        After scoring:
        1. Calculate cognitive quality score (normalize to 0-100)
        2. Compare to user's baseline (if exists in database)
        3. Generate recommendations based on score
        4. Insert cognitive test report using insert_cognitive_test_report tool
        
        Important:
        - Be patient and repeat questions if needed
        - Speak clearly and slowly
        - Don't rush the patient
        - If they seem anxious, reassure them this is routine
        """,
        agent=cognitive_agent,
        expected_output="TICS test completed and cognitive report saved to database"
    )
    
    crew = Crew(
        agents=[cognitive_agent],
        tasks=[tics_task],
        verbose=True
    )
    
    return crew
