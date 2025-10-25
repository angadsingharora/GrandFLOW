# GrandFLOW - Senior Care Platform

GrandFLOW is a comprehensive senior care platform that combines voice interaction, health monitoring, and concierge services to provide personalized care for seniors and peace of mind for their families.

## Features

### 🎤 Voice Interaction
- **Real-time Voice Calls**: Powered by Fish Audio (TTS) and Whisper (STT)
- **Natural Conversation**: AI agents that can engage in meaningful conversations
- **Multi-language Support**: Supports multiple languages for diverse senior populations

### 🏥 Health Monitoring
- **Diet Tracking**: Monitor macronutrients, calories, meals, and vitamin intake
- **Medication Adherence**: Track prescribed medications and adherence rates
- **Physical Wellness**: Monitor exercise, steps, sleep duration, and calories burned
- **Cognitive Testing**: Weekly TICS (Telephone Interview for Cognitive Status) assessments
- **Heart Rate Monitoring**: Real-time heart rate tracking with visual graphs

### 🚗 Concierge Services
- **Rideshare Booking**: Integration with Uber/Lyft for transportation needs
- **Delivery Services**: Order groceries, medications, and other essentials
- **Task Management**: Track and manage all concierge requests
- **GoGoGrandparent Integration**: Seamless integration with existing senior services

### 📊 Dashboard
- **User-friendly Interface**: Designed for seniors, family members, and doctors
- **Real-time Updates**: Live data synchronization with Supabase Realtime
- **Accessibility Focus**: Large fonts, clear icons, and intuitive navigation
- **Role-based Access**: Different views for seniors, family members, and healthcare providers

## Tech Stack

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/ui**: Modern UI component library
- **Recharts/Tremor**: Data visualization libraries

### Backend & Database
- **Supabase**: Backend-as-a-Service with PostgreSQL
- **Supabase Auth**: Authentication and user management
- **Supabase Realtime**: Real-time data synchronization
- **Row Level Security**: Secure data access policies

### AI & Voice
- **CrewAI**: Multi-agent AI framework for specialized tasks
- **OpenAI GPT**: Natural language processing
- **Fish Audio**: Text-to-speech synthesis
- **Whisper**: Speech-to-text transcription

### Deployment
- **Vercel**: Frontend deployment
- **Supabase Cloud**: Database and backend services

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Supabase account
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/grandflow.git
   cd grandflow
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env.local
   ```
   
   Fill in your environment variables:
   ```env
   NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Set up Supabase database**
   - Create a new Supabase project
   - Run the SQL schema from `supabase/schema.sql`
   - Enable Row Level Security policies

5. **Start the development server**
   ```bash
   npm run dev
   ```

6. **Open your browser**
   Navigate to `http://localhost:3000`

## Database Schema

The platform uses the following main tables:

- **users**: User profiles and roles
- **diet_reports**: Daily diet tracking data
- **medical_adherence**: Medication tracking
- **physical_mental_wellness_reports**: Exercise and wellness data
- **cognitive_test_reports**: TICS test results
- **rideshare_tasks**: Transportation bookings
- **delivery_tasks**: Delivery service requests

## AI Agents

### Health Monitoring Agent
- Processes diet, medication, and wellness data
- Provides personalized health recommendations
- Tracks adherence and progress over time

### Cognitive Testing Agent
- Administers TICS assessments
- Evaluates cognitive function
- Provides early intervention recommendations

### Service Concierge Agent
- Handles rideshare and delivery requests
- Manages task scheduling and status updates
- Integrates with external service providers

## Voice Integration

The platform includes a comprehensive voice system:

1. **Voice Call Manager**: Handles call initiation and termination
2. **Speech Recognition**: Converts speech to text using Whisper
3. **Text-to-Speech**: Converts AI responses to natural speech
4. **Real-time Processing**: Processes conversations as they happen

## User Roles

### Senior
- Primary users of the platform
- Access to health monitoring and concierge services
- Voice interaction capabilities

### Family Member
- View health reports and updates
- Monitor medication adherence
- Track concierge service usage

### Doctor
- Access to comprehensive health data
- Review cognitive assessments
- Provide medical recommendations

## Security & Privacy

- **Row Level Security**: Database-level access control
- **Encrypted Communication**: All data transmission is encrypted
- **HIPAA Compliance**: Healthcare data protection standards
- **User Consent**: Clear consent mechanisms for data collection

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, email support@grandflow.com or join our Slack channel.

## Roadmap

- [ ] Mobile app development
- [ ] Integration with wearable devices
- [ ] Advanced AI health predictions
- [ ] Multi-language support expansion
- [ ] Integration with more healthcare providers
- [ ] Advanced analytics dashboard

## Acknowledgments

- CrewAI team for the amazing multi-agent framework
- Supabase for the excellent backend platform
- OpenAI for powerful AI capabilities
- The senior care community for valuable feedback
