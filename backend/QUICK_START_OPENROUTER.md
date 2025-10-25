# Quick Start: OpenRouter & Fish Audio STT

## 🎯 What Just Changed

Your GrandFLOW backend now uses:
- **OpenRouter** for all LLM calls (instead of OpenAI)
- **Fish Audio STT** for speech-to-text (instead of OpenAI Whisper)
- **Fish Audio TTS** for text-to-speech (unchanged)

## ⚡ Quick Setup (5 minutes)

### Step 1: Get API Keys

1. **OpenRouter**: https://openrouter.ai/keys
   - Sign up → Create API key
   - Copy key (starts with `sk-or-v1-`)

2. **Fish Audio**: https://fish.audio (if not already)
   - Sign up → Get API key
   - Copy key

### Step 2: Update Your `.env`

```bash
cd backend

# Edit .env file
nano .env  # or use your editor
```

Add/update these lines:

```env
# Remove or comment out:
# OPENAI_API_KEY=...

# Add these:
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
FISH_AUDIO_STT_MODEL=whisper-large-v3

# Keep existing:
FISH_AUDIO_API_KEY=your-existing-fish-key
FISH_AUDIO_VOICE_ID=your-voice-id
```

### Step 3: Test Everything

```bash
python test_voice_integration.py
```

You should see:
```
✅ PASS - Fish Audio TTS
✅ PASS - Fish Audio STT
✅ PASS - OpenRouter LLM
✅ PASS - Supabase Storage
✅ PASS - Twilio Client

🎉 All tests passed!
```

### Step 4: Run Your Backend

```bash
python -m app.main
```

That's it! 🚀

---

## 📝 What Changed in Code

### Before
```python
# Old OpenAI Whisper
import openai
client = openai.OpenAI()
transcript = client.audio.transcriptions.create(...)

# Old OpenAI GPT-4
client = OpenAI()
response = client.chat.completions.create(model="gpt-4-turbo", ...)
```

### After
```python
# New Fish Audio STT
async with aiohttp.ClientSession() as session:
    result = await session.post("https://api.fish.audio/v1/asr", ...)

# New OpenRouter (any LLM)
client = OpenAI(
    api_key=settings.OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)
response = client.chat.completions.create(
    model=settings.OPENROUTER_MODEL,  # Claude, GPT-4, Llama, etc.
    ...
)
```

---

## 💰 Benefits

### Cost Savings
- **~38% cheaper** per call
- Save ~$1,080/year (at 10K calls/month)

### Flexibility
- Access to 100+ models with one key
- Easy to switch between Claude, GPT-4, Llama, Gemini
- No vendor lock-in

### Simplicity
- One API key for all voice (Fish Audio)
- Unified billing via OpenRouter
- Better integration

---

## 🎨 Model Options

Want to try different models? Just change one line in `.env`:

```env
# Best balance (recommended)
OPENROUTER_MODEL=anthropic/claude-3.5-sonnet

# OpenAI's GPT-4
OPENROUTER_MODEL=openai/gpt-4-turbo

# Google's Gemini (cheaper)
OPENROUTER_MODEL=google/gemini-pro-1.5

# Meta's Llama (open source)
OPENROUTER_MODEL=meta-llama/llama-3-70b-instruct

# Highest quality
OPENROUTER_MODEL=anthropic/claude-3-opus
```

See all models: https://openrouter.ai/models

---

## 🧪 Testing Individual Components

### Test Fish Audio STT
```bash
python -c "
import asyncio
from app.voice.text_to_speech import synthesize_speech
from app.voice.speech_to_text import transcribe_audio

async def test():
    audio = await synthesize_speech('Test message')
    text = await transcribe_audio(audio)
    print(f'Transcribed: {text}')

asyncio.run(test())
"
```

### Test OpenRouter
```bash
python -c "
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv('OPENROUTER_API_KEY'),
    base_url='https://openrouter.ai/api/v1'
)

response = client.chat.completions.create(
    model='anthropic/claude-3.5-sonnet',
    messages=[{'role': 'user', 'content': 'Say hi'}],
    max_tokens=20
)

print(response.choices[0].message.content)
"
```

---

## 🐛 Common Issues

### "Invalid API key" (OpenRouter)
- Key must start with `sk-or-v1-`
- Check at https://openrouter.ai/keys
- No spaces in `.env` file

### "Model not found"
- Model names are case-sensitive
- Check spelling: `anthropic/claude-3.5-sonnet`
- View available: https://openrouter.ai/models

### "Fish Audio STT failed"
- Ensure audio is WAV format
- Check API key is correct
- Try with small audio file first

---

## 📚 Full Documentation

- **Migration Guide**: `MIGRATION_OPENROUTER_FISH.md`
- **Summary**: `OPENROUTER_FISH_SUMMARY.md`
- **Main README**: `README.md`

---

## ✅ Checklist

- [ ] Got OpenRouter API key
- [ ] Updated `.env` with `OPENROUTER_API_KEY`
- [ ] Updated `.env` with `OPENROUTER_MODEL`
- [ ] Ran `python test_voice_integration.py`
- [ ] All tests passed
- [ ] Tested on real call
- [ ] Monitoring costs at https://openrouter.ai/activity

---

## 🎉 You're Done!

Your backend now uses:
- ✅ OpenRouter for flexible LLM access
- ✅ Fish Audio for unified voice processing
- ✅ Better pricing and performance

Start the backend and test a call! 📞

---

**Questions?** See detailed guides in:
- `MIGRATION_OPENROUTER_FISH.md`
- `OPENROUTER_FISH_SUMMARY.md`

**Need help?** Check:
- OpenRouter docs: https://openrouter.ai/docs
- Fish Audio docs: https://fish.audio/docs/api

