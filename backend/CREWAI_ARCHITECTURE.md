# CrewAI Multi-Turn Conversation Architecture

## Overview

GrandFLOW now uses **CrewAI agents with memory** to enable natural, multi-turn conversations through Twilio voice calls. Agents act like real doctors or health coordinators, asking questions naturally and gathering information gradually through conversation.

## Key Concept: Agent Memory

Unlike the previous approach, this architecture leverages CrewAI's built-in memory capabilities:

- **Agent Memory (`memory=True`)**: Agents remember the entire conversation context
- **Crew Memory (`memory=True`)**: The crew maintains state across multiple `kickoff()` calls
- **Same Crew Instance**: We reuse the same crew instance throughout the conversation loop

This allows agents to:
- Remember what they've already asked
- Build on previous responses
- Ask natural follow-up questions
- Avoid repeating questions
- Call tools at the appropriate time based on collected information

## Architecture Flow

```
1. Twilio Call Initiated
   ↓
2. Orchestrator Creates CallSession
   ↓
3. Appropriate CrewAI Crew Created (memory=True)
   ↓
4. Crew Stored in Session
   ↓
5. Initial kickoff() → Agent's first question
   ↓
6. TTS → Play to user
   ↓
7. User responds → STT → Text
   ↓
8. Feed back to SAME crew instance via kickoff(inputs={"user_input": text})
   ↓
9. Agent processes with memory context
   ↓
10. Agent may call tools or ask follow-up
   ↓
11. Repeat steps 6-10 until conversation complete
   ↓
12. Agent indicates completion
   ↓
13. Finalize: Save transcript, close session
```

## Core Components

### 1. CallSession (`app/voice/call_session.py`)

Tracks state for each active call:
- `active_crew`: The CrewAI crew instance (with memory)
- `conversation_history`: All turns in the conversation
- `diet_data`, `medication_data`, `wellness_data`, `cognitive_data`: Accumulated data
- `turn_count`: Number of conversation turns
- `state`: Current state (INITIATED, IN_CONVERSATION, FINALIZING, COMPLETED)

The session is the "memory" outside of CrewAI that tracks overall call state.

### 2. CrewAI Crews with Memory

#### Health Monitoring Crew (`app/crews/health_monitoring.py`)

**Agent**: Health Conversation Coordinator
- **Role**: Have natural conversations to collect daily health info
- **Memory**: Enabled (`memory=True`)
- **Tools**:
  - `calculate_diet_quality_score`
  - `calculate_exercise_quality_score`
  - `calculate_medication_adherence_rate`
  - `generate_health_recommendations`
  - `insert_diet_report`
  - `insert_wellness_report`
  - `insert_medication_adherence`

**Conversation Topics** (asked naturally):
1. How are you feeling today?
2. What did you eat for meals?
3. Did you take vitamins/supplements?
4. Did you take your medications?
5. Did you exercise or walk?
6. How did you sleep?
7. Any symptoms or pain?

The agent asks ONE question at a time, listens to the response with memory, and naturally transitions to the next topic.

#### Cognitive Testing Crew (`app/crews/cognitive_testing.py`)

**Agent**: Cognitive Assessment Specialist
- **Role**: Administer TICS test conversationally
- **Memory**: Enabled (`memory=True`)
- **Tools**:
  - `administer_tics_test`
  - `convert_tics_to_mmse`
  - `calculate_cognitive_quality_score`
  - `determine_cognitive_risk_level`
  - `generate_cognitive_recommendations`
  - `insert_cognitive_test_report`

**TICS Test Sections** (asked one at a time):
1. Orientation (5 questions)
2. Registration (3 words)
3. Attention/Calculation (serial 7s)
4. Recall (3 words)
5. Naming (2 objects)
6. Repetition (1 phrase)
7. Comprehension (3 commands)

The agent remembers test progress, scores each response, and moves naturally through sections.

### 3. ConversationLoopHandler (`app/voice/conversation_loop.py`)

Manages the multi-turn loop:

**Key Methods**:
- `initiate_conversation()`: Creates session, creates crew, gets first response
- `continue_conversation()`: Feeds user input back to crew, gets next response
- `finalize_conversation()`: Ends session, saves transcript

**How it Works**:
```python
# First call
result = crew.kickoff(inputs={"user_input": "Hello"})
agent_response = result.output

# User responds with "I had oatmeal"
result = crew.kickoff(inputs={"user_input": "I had oatmeal"})
# Agent remembers previous context and asks about lunch

# Continue feeding responses back
result = crew.kickoff(inputs={"user_input": "Chicken salad"})
# Agent remembers both breakfast and lunch, asks about dinner

# And so on...
```

The same crew instance is reused, so memory persists!

### 4. CallOrchestrator (`app/crews/orchestrator.py`)

Coordinates the call:
- Creates call log
- Routes to appropriate crew based on call_type
- Delegates to ConversationLoopHandler
- Manages finalization

### 5. VoiceCallHandler (`app/voice/voice_handler.py`)

Handles Twilio webhooks:
- **`/voice/outbound`**: Initiates outbound call
- **`/voice/outbound-start`**: When call connects, starts CrewAI conversation
- **`/voice/conversation`**: Main loop - receives user speech, feeds to crew, plays response
- **`/voice/call-status`**: Handles call status updates

## Data Flow

### How Data Gets to Database

The CrewAI agents have **database tools** in their toolkit. When they've collected enough information through conversation, they call these tools:

```python
# Agent has asked about meals and collected responses
# Agent's memory contains:
# - "I had oatmeal for breakfast"
# - "Chicken salad for lunch"
# - "Baked cod for dinner"

# Agent calls tool
insert_diet_report({
    "user_id": patient_id,
    "call_id": call_id,
    "date": today,
    "macronutrients": {estimated from conversation},
    "calories": {estimated},
    "meals_count": 3,
    ...
})
```

The tools use Pydantic models for validation:
```python
DietReport(
    user_id=uuid,
    call_id=uuid,
    macronutrients={...},
    calories=1800,
    ...
)
```

Then save to Supabase through `database_tools.py`.

### When Tools Are Called

Agents decide when to call tools based on their instructions and the conversation context. Typically:

1. **During conversation**: As they gather enough info for a section
   - After asking about all meals → calculate diet score
   - After asking about medications → calculate adherence
   
2. **End of conversation**: When they have all needed data
   - Insert complete reports to database
   - Generate final recommendations

## Running an Outbound Call

### 1. Initiate Call

```python
POST /voice/outbound
{
    "patient_id": "uuid-123",
    "call_type": "health_checkup"
}
```

### 2. System Actions

1. Call patient's phone number via Twilio
2. When answered, webhook to `/voice/outbound-start`
3. Create `CallOrchestrator`
4. Create `CallSession`
5. Create health monitoring crew with memory
6. Store crew in session
7. Get initial response: "Good morning! How are you feeling today?"
8. Play to user with TTS

### 3. Conversation Loop

```
User: "I'm feeling pretty good"
→ Transcribed via STT
→ Fed to crew: kickoff(inputs={"user_input": "I'm feeling pretty good"})
→ Agent (with memory): "That's wonderful! What did you have for breakfast this morning?"
→ TTS → Play to user

User: "I had oatmeal with berries"
→ STT
→ Fed to crew: kickoff(inputs={"user_input": "I had oatmeal with berries"})
→ Agent (remembers previous): "Nice! And what did you have for lunch?"
→ TTS → Play

... continues naturally through all topics ...

Agent: "Thank you for sharing! Your diet score today is 85/100. You're doing great..."
→ Completion detected
→ Finalize call
```

### 4. Finalization

- Save transcript to `call_logs`
- Crew has already called tools to save data:
  - `diet_reports` table populated
  - `wellness_reports` table populated
  - `medication_adherence` table populated
- Session cleaned up

## Key Differences from Previous Approach

| Aspect | Old (Non-CrewAI) | New (CrewAI with Memory) |
|--------|------------------|--------------------------|
| **Questions** | Hardcoded 8 questions in sequence | Natural conversation, agent adapts |
| **Memory** | Manual context tracking | CrewAI built-in memory |
| **Flexibility** | Fixed flow | Agent can ask follow-ups, probe deeper |
| **Tool Calling** | After all questions | Throughout conversation as appropriate |
| **AI Intelligence** | None (scripted) | Full LLM reasoning and conversation |
| **Natural Feel** | Robotic, form-filling | Like talking to a real health coordinator |

## Testing

### Manual Test

```bash
# Start backend
cd backend
python -m uvicorn app.main:app --reload

# In another terminal, trigger outbound call
curl -X POST "http://localhost:8000/voice/outbound?patient_id=test-uuid&call_type=health_checkup"
```

### Test with Twilio

1. Set up ngrok: `ngrok http 8000`
2. Configure Twilio webhook URL: `https://your-ngrok-url.ngrok.io/voice/outbound-start`
3. Initiate call through API
4. Talk to the agent naturally
5. Check Supabase database for saved data

## Environment Variables Required

```env
# CrewAI/LLM
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# Speech
FISH_AUDIO_API_KEY=your_key
FISH_AUDIO_STT_MODEL=your_model

# Twilio
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Database
SUPABASE_URL=your_url
SUPABASE_KEY=your_key

# API
API_BASE_URL=https://your-ngrok-url.ngrok.io
```

## Files Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app with webhook endpoints
│   ├── voice/
│   │   ├── call_session.py          # Session management
│   │   ├── conversation_loop.py     # Multi-turn loop handler
│   │   ├── voice_handler.py         # Twilio webhook handler
│   │   ├── text_to_speech.py        # Fish Audio TTS
│   │   └── speech_to_text.py        # Fish Audio STT
│   ├── crews/
│   │   ├── orchestrator.py          # Call orchestrator
│   │   ├── health_monitoring.py     # Health crew with memory
│   │   └── cognitive_testing.py     # Cognitive crew with memory
│   ├── tools/
│   │   ├── health_analysis_tools.py # Health calculation tools
│   │   ├── cognitive_test_tools.py  # TICS scoring tools
│   │   └── database_tools.py        # Supabase save tools
│   └── models/
│       ├── health_entries.py        # Pydantic models
│       └── cognitive_entries.py     # Pydantic models
```

## Summary

This architecture achieves the goal of having **CrewAI agents naturally converse** with patients to:

✅ Gather health information through multi-turn conversation  
✅ Call tools at appropriate times based on conversation context  
✅ Populate Pydantic models gradually through conversation  
✅ Save all data to Supabase database  
✅ Maintain memory and context throughout the entire call  
✅ Feel like talking to a real doctor or health coordinator  

The agents are **truly conversational** and use LLM intelligence to adapt the conversation, ask follow-ups, and provide personalized responses.
