# backend/app/crews/health_monitoring_crew.py

from crewai import Agent, Task, Crew
from app.tools.database_tools import (
    insert_diet_report, insert_medication_adherence, 
    insert_wellness_report, get_user_medical_profile, get_latest_vitals
)
from app.tools.health_analysis_tools import (
    calculate_diet_quality_score, calculate_exercise_quality_score,
    generate_health_recommendations
)

def create_health_monitoring_crew(user_id: str, call_id: str):
    """
    Creates a crew for daily health check-ins
    """
    
    # Agent 1: Diet Analyzer
    diet_agent = Agent(
        role="Diet Assessment Specialist",
        goal="Assess daily nutrition and provide dietary recommendations",
        backstory="""You are a nutritionist specialized in senior care. 
        You ask about meals eaten today, estimate nutritional content, and 
        provide personalized recommendations based on medical conditions.""",
        tools=[insert_diet_report, get_user_medical_profile, calculate_diet_quality_score],
        verbose=True
    )
    
    # Agent 2: Medication Tracker
    medication_agent = Agent(
        role="Medication Adherence Monitor",
        goal="Verify medications were taken as prescribed",
        backstory="""You are a clinical pharmacist focused on medication compliance.
        You ask which medications were taken today, compare to the prescribed schedule,
        and gently remind about any missed doses.""",
        tools=[insert_medication_adherence, get_user_medical_profile],
        verbose=True
    )
    
    # Agent 3: Wellness Coach
    wellness_agent = Agent(
        role="Physical Wellness Coach",
        goal="Assess exercise, sleep, and overall physical wellness",
        backstory="""You are a geriatric wellness coach. You ask about exercise,
        steps walked, sleep quality, and any physical symptoms. You provide
        encouragement and realistic exercise recommendations.""",
        tools=[insert_wellness_report, get_latest_vitals, calculate_exercise_quality_score],
        verbose=True
    )
    
    # Tasks
    diet_task = Task(
        description=f"""
        Conduct a diet assessment for user {user_id}.
        
        Steps:
        1. Ask: "What did you eat for breakfast, lunch, and dinner today?"
        2. Estimate macronutrients and calories from their description
        3. Ask about vitamins/supplements taken
        4. Fetch user's dietary restrictions from medical profile
        5. Calculate diet quality score (0-100)
        6. Generate 2-3 personalized recommendations
        7. Insert diet report to database using insert_diet_report tool
        
        Be conversational and empathetic.
        """,
        agent=diet_agent,
        expected_output="Diet report successfully saved to database"
    )
    
    medication_task = Task(
        description=f"""
        Check medication adherence for user {user_id}.
        
        Steps:
        1. Fetch prescribed medications from medical profile
        2. Ask: "Did you take your medications today?" (list them by name)
        3. For each medication, confirm it was taken
        4. Calculate adherence rate (% of medications taken)
        5. If any missed, ask why and provide gentle reminder
        6. Insert medication adherence entry using insert_medication_adherence tool
        
        Be supportive, not judgmental.
        """,
        agent=medication_agent,
        expected_output="Medication adherence recorded in database"
    )
    
    wellness_task = Task(
        description=f"""
        Assess physical wellness for user {user_id}.
        
        Steps:
        1. Fetch recent vitals (steps, heart rate) from wearable data
        2. Ask: "Did you do any exercise today?"
        3. Ask: "How did you sleep last night?" (hours)
        4. Ask: "Are you experiencing any pain or discomfort?"
        5. Calculate exercise quality score based on activity level
        6. Generate recommendations (e.g., "Try a 10-minute walk after lunch")
        7. Insert wellness report using insert_wellness_report tool
        
        Be encouraging and realistic with goals.
        """,
        agent=wellness_agent,
        expected_output="Wellness report saved to database"
    )
    
    # Create crew
    crew = Crew(
        agents=[diet_agent, medication_agent, wellness_agent],
        tasks=[diet_task, medication_task, wellness_task],
        verbose=True
    )
    
    return crew
