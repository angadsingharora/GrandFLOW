-- ============================================================================
-- GRANDFLOW COMPLETE DATABASE SETUP
-- Run this file in Supabase SQL Editor to set up everything at once
-- ============================================================================
-- 
-- INSTRUCTIONS:
-- 1. Go to Supabase Dashboard → SQL Editor
-- 2. Copy and paste this ENTIRE file
-- 3. Click Run (or press Cmd/Ctrl + Enter)
-- 4. Wait for "Success" message
-- 5. Scroll down to "ADD TEST DATA" section and customize with your info
--
-- ============================================================================

-- ============================================================================
-- PART 1: CORE TABLES (Users, Patients, Relationships)
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Users (Caregivers)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    user_type VARCHAR(20) DEFAULT 'caregiver',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- Patients (Elderly)
CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255),
    address_line1 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    emergency_contacts JSONB DEFAULT '[]'::JSONB,
    conditions TEXT[] DEFAULT ARRAY[]::TEXT[],
    allergies TEXT[] DEFAULT ARRAY[]::TEXT[],
    medications JSONB DEFAULT '[]'::JSONB,
    preferred_call_times TIME[] DEFAULT ARRAY['09:00:00', '14:00:00']::TIME[],
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone_number);

-- Relationships
CREATE TABLE IF NOT EXISTS patient_caregivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    caregiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,
    access_level VARCHAR(20) DEFAULT 'full',
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(patient_id, caregiver_id)
);

-- ============================================================================
-- PART 2: HEALTH TRACKING TABLES
-- ============================================================================

CREATE TABLE IF NOT EXISTS diet_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    macronutrients JSONB DEFAULT '{}'::JSONB,
    calories INTEGER,
    meals_count INTEGER DEFAULT 0,
    water_intake INTEGER,
    vitamins TEXT[] DEFAULT ARRAY[]::TEXT[],
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    diet_quality_score INTEGER CHECK (diet_quality_score BETWEEN 0 AND 100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS medication_adherence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    medicines_prescribed JSONB DEFAULT '[]'::JSONB,
    medicines_taken JSONB DEFAULT '[]'::JSONB,
    adherence_rate NUMERIC(5,2),
    medications_missed TEXT[] DEFAULT ARRAY[]::TEXT[],
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS wellness_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    exercise_completed BOOLEAN DEFAULT false,
    exercise_type VARCHAR(100),
    exercise_duration INTEGER,
    steps INTEGER DEFAULT 0,
    calories_burned INTEGER DEFAULT 0,
    sleep_duration INTEGER,
    sleep_quality VARCHAR(20),
    mood VARCHAR(50),
    exercise_quality_score INTEGER CHECK (exercise_quality_score BETWEEN 0 AND 100),
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS symptom_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    symptoms_reported TEXT[] DEFAULT ARRAY[]::TEXT[],
    severity_scores JSONB DEFAULT '{}'::JSONB,
    body_areas TEXT[] DEFAULT ARRAY[]::TEXT[],
    symptom_quality_score INTEGER CHECK (symptom_quality_score BETWEEN 0 AND 100),
    urgency_level VARCHAR(20),
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    requires_medical_attention BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PART 3: COGNITIVE & SERVICES
-- ============================================================================

CREATE TABLE IF NOT EXISTS cognitive_test_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    test_date DATE DEFAULT CURRENT_DATE,
    tics_score JSONB DEFAULT '{}'::JSONB,
    tics_total INTEGER,
    mmse_equivalent INTEGER,
    orientation_score INTEGER,
    memory_score INTEGER,
    attention_score INTEGER,
    language_score INTEGER,
    cognitive_quality_score INTEGER CHECK (cognitive_quality_score BETWEEN 0 AND 100),
    risk_level VARCHAR(20) DEFAULT 'normal',
    baseline_comparison JSONB,
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rideshare_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    company VARCHAR(50),
    pickup_location VARCHAR(255) NOT NULL,
    dropoff_location VARCHAR(255) NOT NULL,
    pickup_time TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS delivery_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    service_provider VARCHAR(50),
    delivery_type VARCHAR(50),
    items_ordered JSONB DEFAULT '[]'::JSONB,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS vitals_timeseries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(20),
    source VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PART 4: CALL LOGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_sid VARCHAR(100) UNIQUE,
    call_direction VARCHAR(30) NOT NULL,
    call_status VARCHAR(20) DEFAULT 'completed',
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    transcript TEXT,
    audio_recording_url TEXT,
    agents_involved TEXT[] DEFAULT ARRAY[]::TEXT[],
    tasks_completed JSONB DEFAULT '[]'::JSONB,
    diet_report_id UUID REFERENCES diet_reports(id),
    medication_adherence_id UUID REFERENCES medication_adherence(id),
    wellness_report_id UUID REFERENCES wellness_reports(id),
    cognitive_test_id UUID REFERENCES cognitive_test_reports(id),
    service_requests_mentioned JSONB DEFAULT '[]'::JSONB,
    patient_mood VARCHAR(30),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_call_logs_patient ON call_logs(patient_id, started_at DESC);

-- ============================================================================
-- PART 5: STORAGE BUCKETS
-- ============================================================================

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'call-audio',
    'call-audio',
    true,
    10485760,
    ARRAY['audio/mpeg', 'audio/mp3', 'audio/wav']
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'patient-documents',
    'patient-documents',
    false,
    52428800,
    ARRAY['application/pdf', 'image/jpeg', 'image/png']
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- PART 6: STORAGE POLICIES
-- ============================================================================

CREATE POLICY IF NOT EXISTS "Public read call audio"
ON storage.objects FOR SELECT TO public
USING (bucket_id = 'call-audio');

CREATE POLICY IF NOT EXISTS "Authenticated upload call audio"
ON storage.objects FOR INSERT TO authenticated
WITH CHECK (bucket_id = 'call-audio');

CREATE POLICY IF NOT EXISTS "Service role manage call audio"
ON storage.objects FOR ALL TO service_role
USING (bucket_id = 'call-audio');

-- ============================================================================
-- PART 7: ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "Service role full access - patients"
ON patients FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY IF NOT EXISTS "Service role full access - users"
ON users FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY IF NOT EXISTS "Service role full access - call_logs"
ON call_logs FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================================
-- ✅ SETUP COMPLETE!
-- ============================================================================
-- Now scroll down to add your test data...
-- ============================================================================



-- ============================================================================
-- 🎯 ADD TEST DATA BELOW (Customize with your information!)
-- ============================================================================

-- ADD YOUR TEST PATIENT (Use YOUR phone number!)
/*
INSERT INTO patients (
    first_name, 
    last_name, 
    date_of_birth, 
    phone_number,
    conditions,
    medications
)
VALUES (
    'John',                          -- Change to your first name
    'Doe',                           -- Change to your last name
    '1950-01-15',                    -- Birth date
    '+1234567890',                   -- ⚠️ CHANGE TO YOUR ACTUAL PHONE NUMBER
    ARRAY['hypertension'],
    '[{"name": "Lisinopril", "dosage": "10mg"}]'::JSONB
)
RETURNING id, first_name, last_name, phone_number;
*/

-- ADD A CAREGIVER USER (Optional)
/*
INSERT INTO users (
    email,
    first_name,
    last_name,
    phone_number
)
VALUES (
    'you@example.com',               -- Your email
    'Jane',                          -- Your name
    'Smith',
    '+1234567891'
)
RETURNING id, email, first_name;
*/

-- ============================================================================
-- VERIFY SETUP
-- ============================================================================

SELECT 'Setup Complete! ✅' as status;

-- Check tables created
SELECT COUNT(*) as table_count 
FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check storage buckets
SELECT name, public FROM storage.buckets;

-- Show test patients
SELECT id, first_name, last_name, phone_number 
FROM patients;

