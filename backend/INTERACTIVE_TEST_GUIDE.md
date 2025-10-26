# Interactive Agent Test Guide

## What This Test Does

This test lets you **chat directly with the CrewAI agents via text** - no Twilio, no Fish Audio, just pure text conversation. It's perfect for:

- ✅ Testing if the agent network works
- ✅ Seeing how agents remember context
- ✅ Watching agents call tools in real-time
- ✅ Debugging conversation flow
- ✅ Understanding how CrewAI memory works

## Prerequisites

1. **Environment variables set in `.env`**:
   ```bash
   OPENROUTER_API_KEY=your_key_here
   OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
   SUPABASE_URL=your_url_here
   SUPABASE_KEY=your_key_here
   ```

2. **Python environment activated** (if using conda/venv)

## How to Run

```bash
cd backend
python test_interactive_agent.py
```

## What You'll See

### Menu Screen
```
🧪 CREWAI AGENT INTERACTIVE TEST
====================================================================

Choose which agent you want to chat with:

  1. Health Check-In Agent (Health Conversation Coordinator)
  2. Cognitive Test Agent (Cognitive Assessment Specialist)
  3. Exit

====================================================================

Enter your choice (1-3):
```

### Example: Health Check-In Conversation

```
🏥 INTERACTIVE HEALTH CHECK-IN WITH CREWAI AGENT
====================================================================

🤖 Agent: Good morning! How are you feeling today?

👤 You: I'm feeling pretty good today

🤖 Agent: That's wonderful to hear! Let's go through your daily health check-in. 
What did you have for breakfast this morning?

👤 You: I had oatmeal with berries and some orange juice

🤖 Agent: That sounds like a nutritious start to the day! Oatmeal and berries 
are great choices. What did you have for lunch?

👤 You: A chicken salad sandwich

🤖 Agent: Nice! And what about dinner?

👤 You: Baked salmon with vegetables

🤖 Agent: Excellent! Those are all healthy choices. Did you take any vitamins 
or supplements today?

... conversation continues naturally ...
```

### What You'll Learn

1. **Agent Memory**: Watch the agent remember previous answers
   - After you say "oatmeal", agent remembers it when asking about lunch
   - Agent builds on context throughout conversation

2. **Natural Flow**: See how questions flow conversationally
   - Not robotic or form-filling
   - Adapts based on your responses

3. **Tool Calling**: (If verbose mode is on, you'll see in logs)
   - Agent calls `calculate_diet_quality_score` after collecting meal info
   - Agent calls `insert_diet_report` to save to database
   - Agent calls other tools as appropriate

4. **Session Data**: At the end, you'll see accumulated data
   ```
   📊 SESSION DATA
   ====================================================================
   
   Total conversation turns: 9
   Session state: completed
   
   💾 Accumulated Data:
     Diet data: {...}
     Wellness data: {...}
     Medication data: {...}
   ```

## Commands During Conversation

- **Type normally**: Just respond to agent's questions
- **Type `quit` or `exit`**: End conversation early
- **Press Ctrl+C**: Emergency stop

## Example Session: Cognitive Test

```
🧠 INTERACTIVE COGNITIVE TEST WITH CREWAI AGENT
====================================================================

🤖 Agent: Hello! Today I'd like to do a brief cognitive screening with you. 
It's just a routine check, nothing to worry about. Let's start with some 
simple questions. What is today's date - the day, month, and year?

👤 You: October 26, 2025

🤖 Agent: Good! And what day of the week is today?

👤 You: Sunday

🤖 Agent: Perfect. What season are we in right now?

👤 You: Fall

🤖 Agent: Excellent. Now I'm going to say 3 words. Please repeat them back 
to me: APPLE, TABLE, PENNY

👤 You: apple table penny

🤖 Agent: Great! Now, starting at 100, subtract 7. What is 100 minus 7?

... test continues through all TICS sections ...
```

## Debugging Tips

### If Agent Doesn't Respond Well

1. **Check OpenRouter API Key**: Make sure it's valid
   ```bash
   echo $OPENROUTER_API_KEY
   ```

2. **Check Logs**: Look for errors in terminal output

3. **Try More Detailed Responses**: Instead of "yes", try "Yes, I did"

### If Agent Doesn't Call Tools

This might mean:
- Agent doesn't think it has enough information yet
- Agent needs clearer instructions (check crew definitions)
- There's an error in tool calling (check logs)

### If Database Insert Fails

- Check Supabase credentials
- Check if database tables exist
- Look at Pydantic validation errors in output

## What to Test

### Health Check-In Agent
Test that it asks about:
- ✅ How you're feeling
- ✅ Breakfast, lunch, dinner
- ✅ Vitamins/supplements
- ✅ Medications
- ✅ Exercise/physical activity
- ✅ Sleep
- ✅ Symptoms

### Cognitive Test Agent
Test that it goes through:
- ✅ Orientation (date, day, season)
- ✅ Registration (3 words)
- ✅ Attention (serial 7s)
- ✅ Recall (3 words)
- ✅ Naming (clock, pen)
- ✅ Repetition (phrase)
- ✅ Comprehension (commands)

## Understanding the Output

### Verbose Mode (if enabled in crew)
You'll see CrewAI's internal processing:
```
> Entering new CrewAgentExecutor chain...
Thought: The user said they had oatmeal for breakfast...
Action: Continue conversation
...
```

### Session Data at End
Shows what was accumulated:
- **conversation_history**: All Q&A turns
- **diet_data/wellness_data/etc**: Data collected (if using gradual approach)
- **turn_count**: How many exchanges occurred
- **state**: Final state of conversation

## Next Steps

After this test works:
1. ✅ You know agents are working
2. ✅ You know memory is working
3. ✅ You know tools are being called
4. → Add Twilio integration
5. → Add Fish Audio TTS/STT
6. → Test with real phone calls

## Troubleshooting

### "OPENROUTER_API_KEY not found"
```bash
# Add to .env file
echo 'OPENROUTER_API_KEY=your_key_here' >> .env
```

### "Module not found" errors
```bash
# Make sure you're in backend directory
cd backend

# If using conda
conda activate your_env

# If using venv
source venv/bin/activate
```

### Agent gives weird responses
- Try different model in .env: `OPENROUTER_MODEL=openai/gpt-4`
- Make crew instructions more specific
- Check if API has rate limits

### Conversation never ends
- Type `quit` to end manually
- Check completion detection logic in `conversation_loop.py`
- Agent might need clearer ending instructions

## Expected Behavior

**Good Signs** ✅:
- Agent asks questions one at a time
- Agent remembers previous answers
- Conversation flows naturally
- Tools get called (check logs)
- Data appears in session at end

**Bad Signs** ❌:
- Agent repeats questions
- Agent forgets previous answers
- Agent doesn't call tools
- Errors in logs
- Session data is empty

If you see bad signs, the issue is likely in:
1. Crew memory configuration
2. Tool definitions
3. Agent instructions
4. OpenRouter API issues

---

**Happy Testing!** 🚀

This interactive test is your best friend for debugging the agent network before adding the complexity of voice integration.

