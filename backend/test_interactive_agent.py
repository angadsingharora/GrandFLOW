#!/usr/bin/env python3
"""
Interactive Agent Test - Chat Directly with CrewAI Agents

This test lets you interact with the health monitoring or cognitive testing
agents through text, without Twilio or Fish Audio. Just pure CrewAI conversation.

Usage:
    python test_interactive_agent.py
"""

import asyncio
import sys
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.voice.conversation_loop import conversation_loop
from app.voice.call_session import session_manager


class InteractiveAgentTest:
    """Interactive test for chatting with CrewAI agents"""
    
    def __init__(self):
        self.test_patient_id = "test-patient-interactive"
        self.test_call_sid = f"CA-interactive-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.test_call_id = f"call-interactive-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    async def run_health_checkup_chat(self):
        """Interactive chat with health monitoring agent"""
        print("\n" + "="*70)
        print("🏥 INTERACTIVE HEALTH CHECK-IN WITH CREWAI AGENT")
        print("="*70)
        print("\nYou'll be chatting with the Health Conversation Coordinator agent.")
        print("The agent will ask you questions about your health naturally.")
        print("Type your responses as if you're talking on the phone.")
        print("\nType 'quit' or 'exit' to end the conversation early.")
        print("="*70)
        
        try:
            # Initiate conversation
            print("\n🚀 Initiating health check-in conversation...\n")
            
            init_result = await conversation_loop.initiate_conversation(
                call_sid=self.test_call_sid,
                patient_id=self.test_patient_id,
                call_id=self.test_call_id,
                call_type="health_checkup",
                call_direction="outbound_health_checkup"
            )
            
            if not init_result.get("success"):
                print(f"❌ Failed to initiate: {init_result.get('error')}")
                return
            
            # First agent response
            agent_response = init_result.get("agent_response", "")
            print(f"🤖 Agent: {agent_response}\n")
            
            # Conversation loop
            turn = 1
            while True:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    print("   (Please type something)\n")
                    continue
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Ending conversation...\n")
                    break
                
                print()  # Blank line for readability
                
                # Send to agent
                result = await conversation_loop.continue_conversation(
                    call_sid=self.test_call_sid,
                    user_input=user_input
                )
                
                if not result.get("success"):
                    print(f"❌ Error: {result.get('error')}\n")
                    continue
                
                # Display agent response
                agent_response = result.get("agent_response", "")
                print(f"🤖 Agent: {agent_response}\n")
                
                # Check if conversation is complete
                if result.get("completed"):
                    print("✅ Conversation completed!\n")
                    break
                
                turn += 1
            
            # Show session data
            print("\n" + "="*70)
            print("📊 SESSION DATA")
            print("="*70)
            
            session = session_manager.get_session(self.test_call_sid)
            if session:
                print(f"\nTotal conversation turns: {session.turn_count}")
                print(f"Session state: {session.state.value}")
                
                print("\n📝 Conversation History:")
                for entry in session.conversation_history:
                    print(f"\n  Turn {entry['turn']}:")
                    print(f"    You: {entry['user']}")
                    print(f"    Agent: {entry['agent'][:100]}...")
                
                print("\n💾 Accumulated Data:")
                if session.diet_data:
                    print(f"  Diet data: {session.diet_data}")
                if session.medication_data:
                    print(f"  Medication data: {session.medication_data}")
                if session.wellness_data:
                    print(f"  Wellness data: {session.wellness_data}")
            
            # Finalize
            print("\n🔚 Finalizing conversation...")
            final_result = await conversation_loop.finalize_conversation(
                call_sid=self.test_call_sid
            )
            
            if final_result.get("success"):
                print("✅ Conversation finalized successfully")
                print(f"   Call ID: {final_result.get('call_id')}")
                print(f"   Patient mood: {final_result.get('patient_mood')}")
            
            print("\n" + "="*70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Cleaning up...")
            await conversation_loop.finalize_conversation(self.test_call_sid)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def run_cognitive_test_chat(self):
        """Interactive chat with cognitive testing agent"""
        print("\n" + "="*70)
        print("🧠 INTERACTIVE COGNITIVE TEST WITH CREWAI AGENT")
        print("="*70)
        print("\nYou'll be chatting with the Cognitive Assessment Specialist agent.")
        print("The agent will administer the TICS cognitive test conversationally.")
        print("Answer the questions as if you're taking a real cognitive test.")
        print("\nType 'quit' or 'exit' to end early.")
        print("="*70)
        
        test_call_sid = self.test_call_sid + "-cognitive"
        
        try:
            # Initiate
            print("\n🚀 Initiating cognitive test conversation...\n")
            
            init_result = await conversation_loop.initiate_conversation(
                call_sid=test_call_sid,
                patient_id=self.test_patient_id,
                call_id=self.test_call_id + "-cog",
                call_type="cognitive_test",
                call_direction="outbound_cognitive_test"
            )
            
            if not init_result.get("success"):
                print(f"❌ Failed to initiate: {init_result.get('error')}")
                return
            
            # First question
            agent_response = init_result.get("agent_response", "")
            print(f"🤖 Agent: {agent_response}\n")
            
            # Test loop
            turn = 1
            while True:
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    print("   (Please type something)\n")
                    continue
                
                if user_input.lower() in ['quit', 'exit']:
                    print("\n👋 Ending test...\n")
                    break
                
                print()
                
                # Send to agent
                result = await conversation_loop.continue_conversation(
                    call_sid=test_call_sid,
                    user_input=user_input
                )
                
                if not result.get("success"):
                    print(f"❌ Error: {result.get('error')}\n")
                    continue
                
                # Display response
                agent_response = result.get("agent_response", "")
                print(f"🤖 Agent: {agent_response}\n")
                
                if result.get("completed"):
                    print("✅ Cognitive test completed!\n")
                    break
                
                turn += 1
            
            # Show results
            print("\n" + "="*70)
            print("📊 TEST RESULTS")
            print("="*70)
            
            session = session_manager.get_session(test_call_sid)
            if session:
                print(f"\nTest questions answered: {session.turn_count}")
                print(f"Session state: {session.state.value}")
                
                if session.cognitive_data:
                    print(f"\nCognitive data collected: {list(session.cognitive_data.keys())}")
            
            # Finalize
            await conversation_loop.finalize_conversation(test_call_sid)
            print("\n✅ Test finalized")
            print("="*70)
            
        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user.")
            await conversation_loop.finalize_conversation(test_call_sid)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    async def run_menu(self):
        """Main menu for choosing test type"""
        print("\n" + "="*70)
        print("🧪 CREWAI AGENT INTERACTIVE TEST")
        print("="*70)
        print("\nChoose which agent you want to chat with:\n")
        print("  1. Health Check-In Agent (Health Conversation Coordinator)")
        print("  2. Cognitive Test Agent (Cognitive Assessment Specialist)")
        print("  3. Exit")
        print("\n" + "="*70)
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            await self.run_health_checkup_chat()
        elif choice == "2":
            await self.run_cognitive_test_chat()
        elif choice == "3":
            print("\n👋 Goodbye!\n")
            return
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, or 3.\n")
            await self.run_menu()


async def main():
    """Main entry point"""
    print("\n" + "="*70)
    print("🤖 GRANDFLOW CREWAI INTERACTIVE AGENT TEST")
    print("="*70)
    print("\nThis test lets you chat directly with the CrewAI agents via text.")
    print("No Twilio, no Fish Audio - just pure agent conversation.")
    print("\nMake sure you have:")
    print("  ✓ OPENROUTER_API_KEY set in .env")
    print("  ✓ SUPABASE_URL and SUPABASE_KEY set")
    print("="*70)
    
    # Check environment
    if not os.getenv("OPENROUTER_API_KEY"):
        print("\n⚠️  WARNING: OPENROUTER_API_KEY not found in environment")
        print("   The agents need this to work!")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            print("\n👋 Exiting. Please set OPENROUTER_API_KEY in your .env file.\n")
            return
    
    tester = InteractiveAgentTest()
    await tester.run_menu()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)

