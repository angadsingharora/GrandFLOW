# backend/app/crews/service_concierge_crew.py

from crewai import Agent, Task, Crew
from app.tools.database_tools import insert_rideshare_task, insert_delivery_task
from app.tools.service_tools import (
    book_uber, book_lyft, order_doordash, order_instacart, 
    schedule_prescription_delivery, book_home_service
)

def create_service_concierge_crew(user_id: str, call_id: str):
    """
    Creates a crew for coordinating GoGoGrandparent services
    """
    
    concierge_agent = Agent(
        role="Service Coordination Specialist",
        goal="Book rides, meals, groceries, and other services for the user",
        backstory="""You are a helpful concierge assistant specialized in senior services.
        You can book Uber/Lyft rides, order meals from DoorDash, groceries from Instacart,
        coordinate prescription delivery, and arrange home services. You confirm all details
        before booking.""",
        tools=[
            insert_rideshare_task, insert_delivery_task,
            book_uber, book_lyft, order_doordash, order_instacart,
            schedule_prescription_delivery, book_home_service
        ],
        verbose=True
    )
    
    service_task = Task(
        description=f"""
        Assist user {user_id} with service requests.
        
        Listen for requests like:
        - "I need a ride to the doctor"
        - "Can you order me lunch?"
        - "I need groceries delivered"
        - "I need to refill my prescription"
        - "I need someone to clean my house"
        
        For RIDES:
        1. Ask: "Where do you need to go?"
        2. Ask: "When do you need the ride?" (or default to ASAP)
        3. Ask: "Uber or Lyft preference?" (or choose based on availability)
        4. Use book_uber or book_lyft tool
        5. Insert rideshare task to database using insert_rideshare_task
        6. Confirm: "Your [Uber/Lyft] is booked for [time] to [location]"
        
        For MEAL DELIVERY:
        1. Ask: "What would you like to eat?"
        2. Check dietary restrictions from medical profile
        3. Suggest restaurants matching their preferences
        4. Use order_doordash tool
        5. Insert delivery task using insert_delivery_task
        6. Confirm: "Your order from [restaurant] will arrive around [time]"
        
        For GROCERIES:
        1. Ask: "What groceries do you need?"
        2. Use order_instacart tool
        3. Insert delivery task
        4. Confirm: "Your groceries will be delivered around [time]"
        
        For PRESCRIPTIONS:
        1. Ask: "Which medications need refilling?"
        2. Use schedule_prescription_delivery tool
        3. Insert delivery task
        4. Confirm: "Your prescription will be ready for pickup/delivery on [date]"
        
        For HOME SERVICES:
        1. Ask: "What type of service do you need?" (cleaning, repairs, etc.)
        2. Ask: "When would you like it scheduled?"
        3. Use book_home_service tool
        4. Insert delivery task (or create separate home_service_tasks table)
        5. Confirm: "[Service] is scheduled for [date/time]"
        
        Always:
        - Confirm details before booking
        - Provide cost estimate if available
        - Save all tasks to database
        - Offer to help with anything else
        """,
        agent=concierge_agent,
        expected_output="Service request completed and recorded in database"
    )
    
    crew = Crew(
        agents=[concierge_agent],
        tasks=[service_task],
        verbose=True
    )
    
    return crew
