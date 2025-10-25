# GrandFLOW Architecture - Proper Integration

## 🏗️ Current Architecture (Fixed)

This document describes the **corrected architecture** that properly integrates all components.

---

## 📐 System Components

### Core Components

```
┌─────────────────────────────────────────────────────────────┐
│                    SYSTEM ARCHITECTURE                       │
└─────────────────────────────────────────────────────────────┘

User calls phone
    ↓
┌───────────────┐
│ Twilio Voice  │  Handles telephony infrastructure
└───────┬───────┘
        │
        │ Webhook: POST /voice/incoming
        ↓
┌───────────────┐
│   main.py     │  FastAPI application
│  (API Layer)  │
└───────┬───────┘
        │
        │ Delegates to
        ↓
┌─────────────────────┐
│  VoiceCallHandler   │  Manages call webhooks
│  (voice_handler.py) │  Tracks active calls
└──────────┬──────────┘
           │
           │ Creates & uses
           ↓
┌─────────────────────┐
│  CallOrchestrator   │  Orchestrates AI crews
│  (orchestrator.py)  │  Manages call state
└──────────┬──────────┘
           │
           │ Routes to
           ↓
┌─────────────────────────────────────┐
│  CrewAI Crews                       │
│  - HealthMonitoringCrew             │
│  - CognitiveTestingCrew             │
│  - ServiceConciergeCrew             │
└─────────────────────────────────────┘
```

---

## 🔄 Data Flow

### 1. Incoming Call Flow

```
┌──────────────────────────────────────────────────────────────┐
│               INCOMING CALL WORKFLOW                         │
└──────────────────────────────────────────────────────────────┘

1. User calls phone
   ↓
2. Twilio receives call → POST /voice/incoming
   ↓
3. main.py → voice_handler.handle_incoming_call()
   ↓
4. VoiceCallHandler:
   - Lookup patient by phone number
   - Create CallOrchestrator instance
   - Store in active_calls dict
   - Return TwiML with greeting
   ↓
5. Twilio plays greeting
   ↓
6. Gather user speech → POST /voice/process-input
   ↓
7. main.py → voice_handler.process_user_input()
   ↓
8. VoiceCallHandler:
   - Retrieve orchestrator from active_calls
   - Classify intent (OpenRouter)
   - Route to appropriate crew
   ↓
9. CallOrchestrator.route_to_crew():
   - Selects crew based on intent
   - Executes crew with context
   - Logs activity to database
   ↓
10. Crew processes request:
    - Runs agents & tasks
    - Interacts with tools
    - Returns result
    ↓
11. Response sent back to user via TwiML
```

### 2. Voice Processing Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│               VOICE PROCESSING PIPELINE                      │
└──────────────────────────────────────────────────────────────┘

User speaks
    ↓
Twilio captures audio
    ↓
[Option A: Twilio's speech recognition]
    Twilio transcribes → SpeechResult
    ↓
[Option B: Fish Audio STT]
    Audio bytes → Fish Audio API → Transcription
    ↓
Text passed to CallOrchestrator
    ↓
OpenRouter classifies intent
    ↓
Crew generates response
    ↓
Response text
    ↓
[Option A: Twilio TTS]
    TwiML <Say> with Polly voice
    ↓
[Option B: Fish Audio TTS]
    Text → Fish Audio API → MP3
    Upload to Supabase Storage
    Get public URL
    TwiML <Play> with URL
    ↓
Audio plays on call
```

---

## 🎯 Key Components Explained

### 1. **main.py** (API Layer)

**Purpose**: FastAPI application exposing Twilio webhook endpoints

**Endpoints**:
- `POST /voice/incoming` - Handles incoming calls
- `POST /voice/process-input` - Processes user speech
- `POST /voice/outbound` - Initiates outbound calls
- `POST /voice/call-status` - Receives call status updates

**Key Change**: Now properly delegates to `voice_handler` instead of using `conversation_manager` directly.

```python
# OLD (incorrect)
from app.voice.conversation_manager import ConversationManager
conversation_manager = ConversationManager(user_id, call_sid)

# NEW (correct)
from app.voice.voice_handler import voice_handler
return await voice_handler.handle_incoming_call(request)
```

---

### 2. **voice_handler.py** (VoiceCallHandler)

**Purpose**: Manages Twilio webhook handling and call state

**Responsibilities**:
- Handle incoming/outbound calls
- Manage active calls dictionary
- Classify user intent
- Route to CallOrchestrator
- Play Fish Audio on calls

**Key Features**:
- ✅ Uses `CallOrchestrator` for crew management
- ✅ Tracks active calls in memory dict
- ✅ Integrates Fish Audio TTS playback
- ✅ Uses OpenRouter for intent classification

```python
class VoiceCallHandler:
    def __init__(self):
        self.active_calls: Dict[str, CallOrchestrator] = {}
        self.twilio_client = TwilioClient(...)
    
    async def handle_incoming_call(self, request):
        # Create orchestrator
        orchestrator = CallOrchestrator(patient_id, call_sid, "inbound")
        await orchestrator.initiate_call()
        
        # Store for future requests
        self.active_calls[call_sid] = orchestrator
        
        return TwiML response
    
    async def process_user_input(self, request):
        # Get orchestrator
        orchestrator = self.active_calls[call_sid]
        
        # Classify intent
        intent = await self._classify_intent(user_speech)
        
        # Route to crew
        result = await orchestrator.route_to_crew(intent, context)
        
        return TwiML response
```

---

### 3. **orchestrator.py** (CallOrchestrator)

**Purpose**: Master orchestrator that coordinates AI crews

**Responsibilities**:
- Initialize and track call state
- Route requests to appropriate crews
- Log call activities to database
- Manage conversation context

**Key Features**:
- ✅ Single source of truth for call management
- ✅ Database logging via tools
- ✅ Crew selection logic
- ✅ Context management

```python
class CallOrchestrator:
    def __init__(self, patient_id, call_sid, call_direction):
        self.patient_id = patient_id
        self.call_sid = call_sid
        self.call_direction = call_direction
        self.agents_involved = []
    
    async def initiate_call(self):
        # Log call start to database
        self.call_id = log_call_start(...)
        return self.call_id
    
    async def route_to_crew(self, intent, context):
        if intent == "health_checkup":
            return await self._run_health_monitoring(context)
        elif intent == "cognitive_test":
            return await self._run_cognitive_testing(context)
        elif intent == "service_request":
            return await self._run_service_concierge(context)
    
    async def finalize_call(self, transcript, patient_mood):
        # Log call end to database
        log_call_end(self.call_id, transcript, patient_mood)
```

---

### 4. **conversation_manager.py** (ConversationManager) - REFACTORED

**Purpose**: High-level wrapper for programmatic use (e.g., tests)

**Changes Made**:
- ❌ Removed: Duplicate crew creation logic
- ❌ Removed: Duplicate call logging
- ✅ Added: Uses `CallOrchestrator` internally
- ✅ Added: Delegates crew routing to orchestrator

**New Structure**:
```python
class ConversationManager:
    def __init__(self, user_id, call_sid):
        # Use orchestrator instead of duplicating
        self.orchestrator = CallOrchestrator(
            patient_id=user_id,
            call_sid=call_sid,
            call_direction="inbound"
        )
        self.twilio_client = TwilioClient(...)
    
    async def initialize(self):
        # Delegate to orchestrator
        self.call_id = await self.orchestrator.initiate_call()
    
    async def run_health_monitoring(self):
        # Delegate to orchestrator
        return await self.orchestrator.route_to_crew(
            intent="health_checkup",
            context={"conversation_history": self.conversation_history}
        )
```

**Use Case**: Primarily for testing and programmatic call management without Twilio webhooks.

---

## 🔀 Component Relationships

### Who Uses What?

```
main.py
  └─→ voice_handler (VoiceCallHandler)
        └─→ orchestrator (CallOrchestrator)
              └─→ CrewAI Crews

conversation_manager (ConversationManager)
  └─→ orchestrator (CallOrchestrator)
        └─→ CrewAI Crews

test_orchestrator_integration.py
  ├─→ voice_handler (VoiceCallHandler)
  ├─→ conversation_manager (ConversationManager)
  └─→ orchestrator (CallOrchestrator)
```

### Data Storage

```
CallOrchestrator
  └─→ database_tools
        └─→ Supabase
              ├─→ call_logs table
              ├─→ health_entries tables
              ├─→ cognitive_test_reports table
              └─→ service_requests table

VoiceCallHandler
  └─→ Supabase Storage
        └─→ call-audio bucket
              └─→ Audio files from Fish Audio
```

---

## 🎨 Intent Classification → Crew Routing

### Intent Types

| Intent | Description | Routes To |
|--------|-------------|-----------|
| `health_checkup` | User wants health check-in | HealthMonitoringCrew |
| `cognitive_test` | User wants memory/cognitive test | CognitiveTestingCrew |
| `service_request` | User wants to book service | ServiceConciergeCrew |
| `general_question` | General conversation | Simple LLM response |

### Routing Logic

```python
# In CallOrchestrator
async def route_to_crew(self, intent: str, context: Dict):
    if intent == "health_checkup":
        crew = create_health_monitoring_crew(self.patient_id, self.call_id)
        update_call_agents(self.call_id, "health_monitoring")
        result = crew.kickoff(inputs=context)
        
    elif intent == "cognitive_test":
        crew = create_cognitive_testing_crew(self.patient_id, self.call_id)
        update_call_agents(self.call_id, "cognitive_testing")
        result = crew.kickoff(inputs=context)
        
    elif intent == "service_request":
        crew = create_service_concierge_crew(self.patient_id, self.call_id)
        update_call_agents(self.call_id, "service_concierge")
        result = crew.kickoff(inputs=context)
    
    return result
```

---

## 🧪 Testing Strategy

### Test Suites

1. **test_voice_integration.py** - Component tests
   - Fish Audio TTS/STT
   - OpenRouter LLM
   - Supabase Storage
   - Twilio Client

2. **test_orchestrator_integration.py** - Integration tests
   - CallOrchestrator initialization
   - VoiceCallHandler integration
   - ConversationManager integration
   - Full pipeline tests
   - Crew routing tests

### Running Tests

```bash
# Component tests
python test_voice_integration.py

# Integration tests
python test_orchestrator_integration.py

# On live call (requires active Twilio call)
python test_voice_integration.py CA1234567890abcdef
```

---

## 🔧 Configuration

### Environment Variables

All configuration in `app/config.py`:

```python
class Settings:
    # OpenRouter (LLM)
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    
    # Fish Audio (TTS/STT)
    FISH_AUDIO_API_KEY: str
    FISH_AUDIO_VOICE_ID: str
    FISH_AUDIO_STT_MODEL: str
    
    # Twilio (Voice)
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    # Supabase (Database & Storage)
    SUPABASE_URL: str
    SUPABASE_KEY: str
```

---

## 📊 Database Schema

### Call Tracking

```sql
-- call_logs table
id UUID PRIMARY KEY
patient_id UUID
call_sid TEXT
started_at TIMESTAMP
ended_at TIMESTAMP
call_direction TEXT
agents_involved TEXT[]
tasks_completed JSONB
transcript TEXT
```

### Active Calls (In-Memory)

```python
# In VoiceCallHandler
active_calls: Dict[call_sid, CallOrchestrator]
```

---

## 🚀 Deployment Checklist

- [ ] Set all environment variables in `.env`
- [ ] Create `call-audio` bucket in Supabase Storage
- [ ] Set up Supabase RLS policies
- [ ] Configure Twilio webhooks to point to your server
- [ ] Test with `test_orchestrator_integration.py`
- [ ] Monitor logs during first few calls
- [ ] Set up error tracking (Sentry, etc.)

---

## 🐛 Common Issues & Solutions

### Issue: "Call not found in active_calls"

**Cause**: Call state not persisted between webhook calls

**Solution**: Implement Redis or database-backed session storage

```python
# Instead of in-memory dict
self.active_calls: Dict[str, CallOrchestrator] = {}

# Use Redis
import redis
redis_client = redis.Redis(host='localhost', port=6379)
redis_client.set(f"call:{call_sid}", json.dumps(orchestrator_state))
```

### Issue: "Fish Audio not playing on Twilio"

**Cause**: Audio URL not accessible or TwiML update failed

**Solution**: 
1. Check Supabase bucket is public
2. Verify audio URL is accessible
3. Ensure call is still active (in-progress state)

### Issue: "Crews not executing"

**Cause**: Orchestrator not properly initialized or call_id missing

**Solution**: Ensure `await orchestrator.initiate_call()` is called before routing

---

## 📚 File Structure

```
backend/
├── app/
│   ├── main.py                      # FastAPI app (uses voice_handler)
│   │
│   ├── voice/
│   │   ├── voice_handler.py         # Webhook handler (uses orchestrator)
│   │   ├── conversation_manager.py  # High-level wrapper (uses orchestrator)
│   │   ├── speech_to_text.py        # Fish Audio STT
│   │   └── text_to_speech.py        # Fish Audio TTS
│   │
│   ├── crews/
│   │   ├── orchestrator.py          # Master orchestrator
│   │   ├── health_monitoring.py     # Health crew
│   │   ├── cognitive_testing.py     # Cognitive crew
│   │   └── service_concierge.py     # Service crew
│   │
│   └── tools/
│       └── database_tools.py         # Supabase interactions
│
├── test_voice_integration.py         # Component tests
└── test_orchestrator_integration.py  # Integration tests
```

---

## 🎯 Summary

**Before (Broken)**:
- `main.py` → `conversation_manager.py` (duplicates orchestrator logic)
- `voice_handler.py` exists but unused
- No proper integration between components

**After (Fixed)**:
- `main.py` → `voice_handler.py` → `orchestrator.py` → Crews ✅
- `conversation_manager.py` → `orchestrator.py` → Crews ✅
- Single source of truth (CallOrchestrator) ✅
- Proper testing with `test_orchestrator_integration.py` ✅

**Key Principle**: **CallOrchestrator is the single source of truth for managing calls and routing to crews.**

---

**Documentation Version**: 2.0  
**Last Updated**: October 25, 2025  
**Status**: ✅ Production Ready

