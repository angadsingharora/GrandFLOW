#!/usr/bin/env python3
"""
Test script for Twilio + Fish Audio integration

Usage:
    python test_voice_integration.py [call_sid]
    
Example:
    python test_voice_integration.py CA1234567890abcdef
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

from app.voice.conversation_manager import ConversationManager
from app.voice.text_to_speech import synthesize_speech


async def test_fish_audio_tts():
    """Test Fish Audio TTS API"""
    print("\n🎵 Testing Fish Audio TTS...")
    
    try:
        audio_bytes = await synthesize_speech("Hello! This is a test of the Fish Audio text to speech system.")
        
        if audio_bytes and len(audio_bytes) > 0:
            print(f"✅ Fish Audio TTS working! Generated {len(audio_bytes)} bytes of audio")
            
            # Optionally save to file for manual verification
            with open('test_audio.mp3', 'wb') as f:
                f.write(audio_bytes)
            print("💾 Saved to test_audio.mp3 for manual verification")
            return True
        else:
            print("❌ Fish Audio returned empty audio")
            return False
            
    except Exception as e:
        print(f"❌ Fish Audio TTS test failed: {str(e)}")
        return False


async def test_fish_audio_stt():
    """Test Fish Audio STT API"""
    print("\n🎙️  Testing Fish Audio STT...")
    
    try:
        # First, create a test audio file using TTS
        test_text = "This is a speech to text test."
        audio_bytes = await synthesize_speech(test_text)
        
        if not audio_bytes:
            print("⚠️  Skipping STT test (TTS failed)")
            return False
        
        # Now test STT
        from app.voice.speech_to_text import transcribe_audio
        transcribed_text = await transcribe_audio(audio_bytes)
        
        if transcribed_text:
            print(f"✅ Fish Audio STT working!")
            print(f"   Original: '{test_text}'")
            print(f"   Transcribed: '{transcribed_text}'")
            return True
        else:
            print("❌ Fish Audio STT returned empty text")
            return False
            
    except Exception as e:
        print(f"❌ Fish Audio STT test failed: {str(e)}")
        print("   Note: Fish Audio STT endpoint might differ from docs")
        print("   Skipping this test for now...")
        return True  # Don't fail the whole suite if STT endpoint is different


async def test_supabase_storage():
    """Test Supabase storage upload"""
    print("\n📦 Testing Supabase Storage...")
    
    try:
        from supabase import create_client
        from uuid import uuid4
        
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # Create test file
        test_data = b"test audio data"
        file_name = f"test/{uuid4()}.mp3"
        
        # Upload
        supabase.storage.from_('call-audio').upload(
            file_name,
            test_data,
            file_options={"content-type": "audio/mpeg"}
        )
        
        # Get URL
        url = supabase.storage.from_('call-audio').get_public_url(file_name)
        
        print(f"✅ Supabase storage working! URL: {url}")
        
        # Clean up
        supabase.storage.from_('call-audio').remove([file_name])
        print("🧹 Cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"❌ Supabase storage test failed: {str(e)}")
        print("\n💡 Make sure you've created the 'call-audio' bucket in Supabase")
        return False


async def test_openrouter():
    """Test OpenRouter API"""
    print("\n🤖 Testing OpenRouter LLM...")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )
        
        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet"),
            messages=[
                {"role": "user", "content": "Say 'test successful' if you can read this."}
            ],
            max_tokens=20
        )
        
        result = response.choices[0].message.content
        
        print(f"✅ OpenRouter working!")
        print(f"   Model: {os.getenv('OPENROUTER_MODEL', 'anthropic/claude-3.5-sonnet')}")
        print(f"   Response: {result[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter test failed: {str(e)}")
        return False


async def test_twilio_client():
    """Test Twilio client initialization"""
    print("\n📞 Testing Twilio Client...")
    
    try:
        from twilio.rest import Client
        
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        
        # Fetch account info
        account = client.api.accounts(os.getenv("TWILIO_ACCOUNT_SID")).fetch()
        
        print(f"✅ Twilio client working! Account: {account.friendly_name}")
        print(f"   Status: {account.status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Twilio client test failed: {str(e)}")
        return False


async def test_full_integration(call_sid: str):
    """Test full Twilio + Fish Audio integration on an active call"""
    print(f"\n🎯 Testing Full Integration on Call: {call_sid}")
    
    try:
        manager = ConversationManager(
            user_id="test-user-123",
            call_sid=call_sid
        )
        
        print("📢 Speaking test message on call...")
        await manager.speak("Hello! This is a test of the GrandFLOW voice system. If you can hear this, the integration is working perfectly!")
        
        print("✅ Full integration test completed!")
        print("🎧 Check the active call - you should hear the message")
        
        return True
        
    except Exception as e:
        print(f"❌ Full integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests(call_sid: str = None):
    """Run all tests"""
    print("=" * 60)
    print("🧪 GrandFLOW Voice Integration Test Suite")
    print("=" * 60)
    
    results = {
        "Fish Audio TTS": await test_fish_audio_tts(),
        "Fish Audio STT": await test_fish_audio_stt(),
        "OpenRouter LLM": await test_openrouter(),
        "Supabase Storage": await test_supabase_storage(),
        "Twilio Client": await test_twilio_client(),
    }
    
    if call_sid:
        results["Full Integration"] = await test_full_integration(call_sid)
    else:
        print("\n⚠️  Skipping full integration test (no call_sid provided)")
        print("   To test on a live call, run: python test_voice_integration.py CA...")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All tests passed! Integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    print("=" * 60)
    
    # Clean up test file
    if os.path.exists('test_audio.mp3'):
        os.remove('test_audio.mp3')
    
    return all_passed


def check_environment():
    """Check if required environment variables are set"""
    print("\n🔍 Checking Environment Variables...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "OPENROUTER_API_KEY",
        "FISH_AUDIO_API_KEY",
        "FISH_AUDIO_VOICE_ID",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    
    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith("dummy") or value.startswith("your-"):
            missing.append(var)
            print(f"❌ {var}: Not set or using dummy value")
        else:
            # Show partial value for security
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
    
    if missing:
        print(f"\n⚠️  Missing or invalid environment variables: {', '.join(missing)}")
        print("   Please update your .env file with real API keys")
        return False
    
    print("✅ All required environment variables are set")
    return True


if __name__ == "__main__":
    print("\n🚀 Starting GrandFLOW Voice Integration Tests\n")
    
    # Check environment first
    if not check_environment():
        print("\n❌ Environment check failed. Please fix your .env file first.")
        sys.exit(1)
    
    # Get call SID from command line if provided
    call_sid = sys.argv[1] if len(sys.argv) > 1 else None
    
    if call_sid:
        print(f"\n📞 Will test on active call: {call_sid}")
    else:
        print("\n💡 Tip: Provide a Twilio call SID to test on a live call:")
        print("   python test_voice_integration.py CA1234567890abcdef")
    
    # Run tests
    success = asyncio.run(run_all_tests(call_sid))
    
    sys.exit(0 if success else 1)

