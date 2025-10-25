# Twilio + Fish Audio Integration Guide

## Overview

This document explains how GrandFLOW integrates Twilio (voice calls) with Fish Audio (TTS) to create natural conversational experiences for elderly users.

## 🎯 Integration Strategy

### Why This Approach?

1. **Fish Audio**: Provides natural, human-like TTS that's easier for elderly users to understand
2. **Twilio**: Handles reliable phone call infrastructure and routing
3. **Supabase Storage**: Acts as the bridge, hosting audio files for Twilio to play

### Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CONVERSATION FLOW                         │
└─────────────────────────────────────────────────────────────┘

1. AI generates response text
   │
   ▼
2. Fish Audio TTS API
   ├─► Input: "Good morning! How are you feeling today?"
   └─► Output: MP3 audio bytes
   │
   ▼
3. Save to temp file (.mp3)
   │
   ▼
4. Upload to Supabase Storage
   ├─► Bucket: call-audio
   ├─► Path: call_audio/{call_id}/{uuid}.mp3
   └─► Result: Public URL
   │
   ▼
5. Generate TwiML with Play verb
   ├─► <Response>
   │      <Play>https://supabase.../audio.mp3</Play>
   │   </Response>
   │
   ▼
6. Update Twilio call with TwiML
   ├─► twilio_client.calls(call_sid).update(twiml=...)
   │
   ▼
7. Audio plays on active call
   │
   ▼
8. Clean up temp file
```

## 🔧 Implementation Details

### Key Function: `play_audio_on_call()`

Located in: `app/voice/conversation_manager.py`

```python
async def play_audio_on_call(self, audio_bytes: bytes):
    """
    Play Fish Audio TTS on active Twilio call
    
    Flow:
    1. Save audio_bytes to temp file
    2. Upload to Supabase Storage
    3. Get public URL
    4. Update call with TwiML
    5. Clean up
    """
```

### Critical Components

#### 1. Twilio Client Initialization
```python
self.twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)
```

#### 2. Fish Audio TTS Call
```python
# In text_to_speech.py
audio_bytes = await synthesize_speech(text)
# Returns: MP3 format audio data
```

#### 3. Supabase Storage Upload
```python
# Upload audio file
self.supabase.storage.from_('call-audio').upload(
    file_name,
    file_data,
    file_options={"content-type": "audio/mpeg"}
)

# Get public URL
audio_url = self.supabase.storage.from_('call-audio').get_public_url(file_name)
```

#### 4. TwiML Generation
```python
from twilio.twiml.voice_response import VoiceResponse

twiml = VoiceResponse()
twiml.play(audio_url)  # Plays the MP3 from URL
```

#### 5. Call Update
```python
call = self.twilio_client.calls(self.call_sid).update(
    twiml=str(twiml)
)
```

## ⚙️ Configuration Requirements

### Environment Variables

```env
# Twilio (Required)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+15551234567

# Fish Audio (Required)
FISH_AUDIO_API_KEY=your_fish_api_key
FISH_AUDIO_VOICE_ID=voice_id_for_elderly_friendly_voice

# Supabase (Required)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_supabase_anon_key
```

### Supabase Storage Setup

Create a public bucket for call audio:

```sql
-- Create bucket
INSERT INTO storage.buckets (id, name, public)
VALUES ('call-audio', 'call-audio', true);

-- Allow public reads (required for Twilio)
CREATE POLICY "Allow public audio playback"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'call-audio');

-- Allow authenticated uploads
CREATE POLICY "Allow service uploads"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'call-audio');
```

### Fish Audio Voice Settings

For elderly users, optimize for clarity:

```python
payload = {
    "text": text,
    "voice_id": FISH_AUDIO_VOICE_ID,
    "format": "mp3",           # Twilio supports MP3
    "sample_rate": 24000,      # Good quality
    "speed": 0.9               # 10% slower for clarity
}
```

## 🚨 Common Issues & Solutions

### Issue 1: Audio doesn't play on call

**Symptoms**: Call continues but no audio plays

**Solutions**:
- ✅ Check Supabase bucket is public
- ✅ Verify audio URL is accessible (test in browser)
- ✅ Ensure call is in `in-progress` state (not completed/busy)
- ✅ Check Twilio debugger for TwiML errors

### Issue 2: "Access Denied" on Supabase

**Symptoms**: Upload fails or URL returns 403

**Solutions**:
- ✅ Create storage bucket: `call-audio`
- ✅ Set bucket to public
- ✅ Add RLS policies for public read access
- ✅ Use service role key if needed

### Issue 3: Latency/delay in responses

**Symptoms**: Long pause before audio plays

**Solutions**:
- ✅ Use async/await properly
- ✅ Pre-warm Fish Audio API connection
- ✅ Consider caching common phrases
- ✅ Optimize audio file size (lower sample rate if needed)

### Issue 4: TwiML update fails

**Symptoms**: `twilio_client.calls().update()` raises error

**Solutions**:
- ✅ Verify `call_sid` is correct
- ✅ Check call is still active (not ended)
- ✅ Ensure TwiML is valid XML
- ✅ Review Twilio account credentials

## 🧪 Testing the Integration

### Manual Test

```python
# Test script: test_voice_integration.py

import asyncio
from app.voice.conversation_manager import ConversationManager

async def test_speak():
    # Initialize with test call
    manager = ConversationManager(
        user_id="test-user-123",
        call_sid="CA1234567890abcdef"  # Active Twilio call SID
    )
    
    # Test speaking
    await manager.speak("Hello! This is a test of the voice system.")
    
    print("✅ Audio should now be playing on the call")

# Run test
asyncio.run(test_speak())
```

### Verify Storage

```bash
# Check Supabase storage
curl https://your-project.supabase.co/storage/v1/object/public/call-audio/test.mp3
```

### Verify Twilio

```bash
# Check call status
curl -X GET https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Calls/{CallSid}.json \
  -u {AccountSid}:{AuthToken}
```

## 🔐 Security Best Practices

### Production Checklist

- [ ] Store API keys in environment variables (never in code)
- [ ] Use Supabase RLS policies to restrict uploads to service role
- [ ] Implement Twilio webhook signature validation
- [ ] Add rate limiting on voice endpoints
- [ ] Set up monitoring for failed TTS/upload operations
- [ ] Clean up old audio files (implement retention policy)
- [ ] Use HTTPS for all Supabase URLs
- [ ] Rotate API keys regularly

### Audio File Cleanup

Implement cleanup to avoid storage bloat:

```python
# Cleanup old audio files (run daily)
async def cleanup_old_audio():
    # Delete files older than 7 days
    cutoff_date = datetime.now() - timedelta(days=7)
    
    files = supabase.storage.from_('call-audio').list()
    for file in files:
        if file['created_at'] < cutoff_date:
            supabase.storage.from_('call-audio').remove([file['name']])
```

## 📊 Performance Metrics

### Expected Latencies

| Operation | Typical Time |
|-----------|--------------|
| Fish Audio TTS | 200-500ms |
| Supabase Upload | 100-300ms |
| Twilio Call Update | 50-200ms |
| **Total Response Time** | **350-1000ms** |

### Optimization Tips

1. **Parallel Operations**: Upload while generating next response
2. **Connection Pooling**: Reuse HTTP clients
3. **Audio Caching**: Cache common phrases (greetings, farewells)
4. **Streaming**: Consider WebSocket for faster audio delivery

## 🔄 Alternative Approaches

### Option 1: Direct Streaming (WebSocket)

**Pros**: Lower latency, no storage needed  
**Cons**: More complex, requires WebSocket setup

```python
# Use Twilio Media Streams
# Stream audio directly without storage
```

### Option 2: Pre-generated Audio

**Pros**: Instant playback, predictable responses  
**Cons**: Less natural, limited flexibility

```python
# Pre-generate common phrases
# Store URLs in database
```

### Option 3: Twilio Built-in TTS

**Pros**: Simple, no extra services  
**Cons**: Less natural voice quality

```python
twiml.say("Hello, how are you?", voice="alice")
```

## 📚 Additional Resources

- [Twilio Voice TwiML Reference](https://www.twilio.com/docs/voice/twiml)
- [Fish Audio API Docs](https://fish.audio/docs/api)
- [Supabase Storage Guide](https://supabase.com/docs/guides/storage)
- [CrewAI Voice Integration](https://docs.crewai.com)

## 🎓 Learning Path

For team members new to this integration:

1. **Day 1**: Understand Twilio basics (calls, TwiML)
2. **Day 2**: Test Fish Audio TTS API
3. **Day 3**: Set up Supabase storage
4. **Day 4**: Integrate all three components
5. **Day 5**: Test end-to-end on real calls

## 💡 Pro Tips

1. **Test with Real Calls**: Use Twilio test credentials and your phone
2. **Monitor Costs**: Track Fish Audio + Supabase usage
3. **Log Everything**: Add detailed logging for debugging
4. **Graceful Fallbacks**: Use Twilio TTS if Fish Audio fails
5. **User Feedback**: Test with actual elderly users for voice quality

---

**Questions?** Check the main README or create an issue!

