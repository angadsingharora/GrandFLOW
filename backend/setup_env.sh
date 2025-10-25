#!/bin/bash

# GrandFLOW Backend Environment Setup Script

echo "🚀 Setting up GrandFLOW Backend Environment..."
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled."
        exit 1
    fi
fi

# Copy env.example to .env
if [ -f "env.example" ]; then
    cp env.example .env
    echo "✅ Created .env file from env.example"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Edit .env and replace dummy values with your actual API keys:"
    echo "      - SUPABASE_URL and SUPABASE_KEY"
    echo "      - OPENAI_API_KEY"
    echo "      - FISH_AUDIO_API_KEY and FISH_AUDIO_VOICE_ID"
    echo "      - TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER"
    echo ""
    echo "   2. Create a 'call-audio' storage bucket in your Supabase project"
    echo "      (required for storing audio files during calls)"
    echo ""
    echo "   3. Install dependencies: pip install -r requirements.txt"
    echo "   4. Run the server: python -m app.main"
    echo ""
else
    echo "❌ env.example file not found!"
    exit 1
fi

