# GrandFLOW Backend

AI-powered voice assistant for elderly care with daily check-ins, cognitive testing, and service concierge capabilities.

## 🏗️ Architecture Overview

### Voice Pipeline Integration

The GrandFLOW backend integrates **Twilio** (for voice calls) with **Fish Audio** (for natural TTS) to create a seamless conversational experience:

```
┌─────────────┐
│   Patient   │
│   Phone     │
└──────┬──────┘
       │
       │ Voice Call
       ▼
┌─────────────────┐
│  Twilio Voice   │ ◄──── Handles incoming/outgoing calls
│   Platform      │       Manages call state & audio routing
└────────┬────────┘
         │
         │ Call SID
         ▼
┌─────────────────────────┐
│  ConversationManager    │ ◄──── Orchestrates conversation flow
│  (conversation_manager) │       Routes to appropriate AI crews
└────────┬────────────────┘
         │
         ├──► 1. Speech → Text
         │    (Fish Audio STT)
         │
         ├──► 2. AI Processing
         │    (CrewAI Agents + OpenRouter LLM)
         │
         └──► 3. Text → Speech → Call
              (Fish Audio TTS + Twilio)
```

### Twilio + Fish Audio Integration Flow

1. **Text Generation**: CrewAI agents generate conversational responses
2. **TTS Synthesis**: Fish Audio converts text to natural-sounding speech (MP3)
3. **Audio Storage**: Audio uploaded to Supabase Storage for public access
4. **Call Update**: Twilio call updated with TwiML to play the audio URL
5. **Playback**: Audio plays on the active call in real-time

#### Implementation Details

The `play_audio_on_call()` function in `conversation_manager.py`:
- Receives MP3 bytes from Fish Audio TTS
- Saves to temporary file
- Uploads to Supabase Storage bucket `call-audio`
- Generates public URL
- Updates Twilio call with TwiML `<Play>` verb
- Cleans up temporary files

This approach ensures:
- ✅ Natural, human-like voice quality (Fish Audio)
- ✅ Reliable call handling (Twilio)
- ✅ Persistent audio storage (Supabase)
- ✅ Real-time playback during active calls

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Copy environment template
bash setup_env.sh

# Or manually:
cp env.example .env
```

Edit `.env` and add your API keys:

```env
# Required for basic functionality
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key

# Required for voice calls
FISH_AUDIO_API_KEY=your-fish-audio-key
FISH_AUDIO_VOICE_ID=your-voice-id
FISH_AUDIO_STT_MODEL=whisper-large-v3
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890
```

### 2. Supabase Setup

Create a storage bucket for call audio:

```sql
-- In Supabase SQL Editor
INSERT INTO storage.buckets (id, name, public)
VALUES ('call-audio', 'call-audio', true);

-- Set storage policies (public read for Twilio)
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'call-audio');

CREATE POLICY "Service Role Upload"
ON storage.objects FOR INSERT
WITH CHECK (bucket_id = 'call-audio');
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Server

```bash
cd backend
python -m app.main
```

The server will start on `http://localhost:8000`

## 📡 API Endpoints

### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user

### Dashboard
- `GET /dashboard/summary` - Get user dashboard summary
- `GET /dashboard/health` - Health metrics
- `GET /dashboard/cognitive` - Cognitive test results
- `GET /dashboard/services` - Service history

### Voice Calls
- `POST /calls/incoming` - Twilio webhook for incoming calls
- `POST /calls/outgoing` - Initiate outbound call
- `POST /calls/webhook` - Call status updates

## 🤖 AI Crews

### 1. Health Monitoring Crew
Daily check-ins covering:
- Medication adherence
- Diet and hydration
- Physical activity
- Sleep quality
- Mood and wellness

### 2. Cognitive Testing Crew
Weekly cognitive assessments:
- Memory recall tests
- Word association
- Simple math problems
- Orientation questions
- Pattern recognition

### 3. Service Concierge Crew
On-demand services:
- Ride booking (Uber, Lyft)
- Food delivery (DoorDash)
- Grocery delivery (Instacart)
- Appointment reminders
- Family notifications

## 🔧 Configuration

### Voice Settings

```python
# config.py
MAX_CALL_DURATION_SECONDS = 600  # 10 minutes
RECORDING_ENABLED = True
DAILY_CALL_TIME = "09:00"  # 9 AM local time
```

### Fish Audio Voice Tuning

```python
# voice/text_to_speech.py
payload = {
    "voice_id": FISH_AUDIO_VOICE_ID,
    "format": "mp3",
    "sample_rate": 24000,
    "speed": 0.9  # Slower for clarity with elderly users
}
```

## 🧪 Testing

### Test Voice Pipeline

```python
# Test Fish Audio → Twilio integration
from app.voice.conversation_manager import ConversationManager

manager = ConversationManager(
    user_id="test-user",
    call_sid="CAxxxxx"
)

# Test TTS and playback
await manager.speak("Hello, this is a test of the voice system.")
```

### Mock API Calls

For development without actual service APIs:

```env
UBER_API_KEY=MOCK_KEY
LYFT_API_KEY=MOCK_KEY
DOORDASH_API_KEY=MOCK_KEY
```

## 📦 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── config.py              # Configuration & settings
│   ├── database.py            # Database client
│   │
│   ├── api/                   # REST API endpoints
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   └── caregivers.py
│   │
│   ├── crews/                 # CrewAI agent definitions
│   │   ├── orchestrator.py
│   │   ├── health_monitoring.py
│   │   ├── cognitive_testing.py
│   │   └── service_concierge.py
│   │
│   ├── voice/                 # Voice pipeline
│   │   ├── conversation_manager.py  # Main conversation orchestrator
│   │   ├── speech_to_text.py       # Whisper integration
│   │   ├── text_to_speech.py       # Fish Audio integration
│   │   └── voice_handler.py        # Twilio webhook handlers
│   │
│   ├── tools/                 # CrewAI tools
│   │   ├── database_tools.py
│   │   ├── health_analysis_tools.py
│   │   ├── cognitive_test_tools.py
│   │   └── service_tools.py
│   │
│   └── models/                # Database models
│       ├── user.py
│       ├── patient.py
│       ├── call_log.py
│       └── ...
│
├── env.example               # Environment template
├── setup_env.sh             # Setup script
└── requirements.txt         # Python dependencies
```

## 🔐 Security Notes

- Never commit `.env` files to version control
- Use Supabase RLS policies for data access control
- Validate Twilio webhook signatures in production
- Rotate API keys regularly
- Use service role keys only on backend

## 🐛 Troubleshooting

### Audio not playing on Twilio call

1. Check Supabase storage bucket is public
2. Verify audio URL is accessible (test in browser)
3. Ensure Twilio call is in `in-progress` state
4. Check Twilio logs for TwiML errors

### Fish Audio API errors

**TTS Issues:**
1. Verify API key is valid
2. Check voice ID exists in your account
3. Monitor rate limits
4. Test with smaller text samples

**STT Issues:**
1. Verify audio format (WAV preferred)
2. Check audio file size limits
3. Ensure language is set to 'en'
4. Test with short audio clips first

### CrewAI agents not responding

1. Verify OpenRouter API key
2. Check crew definitions in `crews/`
3. Review agent prompts and tools
4. Check database connectivity
5. Try different models if current one is slow

## 📚 Resources

- [Twilio Voice API](https://www.twilio.com/docs/voice)
- [Fish Audio API](https://fish.audio/docs)
- [OpenRouter API](https://openrouter.ai/docs)
- [CrewAI Documentation](https://docs.crewai.com)
- [Supabase Storage](https://supabase.com/docs/guides/storage)

## 🤝 Contributing

This is a hackathon project. For production deployment:

1. Add proper error handling
2. Implement rate limiting
3. Add comprehensive logging
4. Set up monitoring & alerts
5. Add unit & integration tests
6. Implement proper authentication middleware
7. Add Twilio webhook signature verification

## 📄 License

MIT License - Cal Hacks 2025 Project

