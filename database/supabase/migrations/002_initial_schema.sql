-- database/supabase/migrations/002_patients_caregivers.sql

-- ========================================
-- USERS (Caregivers/Family Members)
-- ========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    phone_number VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- PATIENTS (Seniors being monitored)
-- ========================================

CREATE TABLE patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,  -- For receiving calls
    address JSONB,
    emergency_contacts JSONB[],
    
    -- Medical info
    conditions TEXT[],
    allergies TEXT[],
    medications JSONB[],
    dietary_restrictions TEXT[],
    primary_care_physician JSONB,
    
    -- Call scheduling
    preferred_call_times TIME[],  -- e.g., [09:00, 14:00, 19:00]
    call_frequency VARCHAR(20) DEFAULT 'daily',  -- daily, weekly, on_demand
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_patients_phone ON patients(phone_number);

-- ========================================
-- CAREGIVERS <-> PATIENTS (Many-to-Many)
-- ========================================

CREATE TABLE patient_caregivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    caregiver_id UUID REFERENCES users(id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,  -- "daughter", "son", "spouse", "professional_caregiver"
    access_level VARCHAR(20) DEFAULT 'full',  -- full, limited (for HIPAA)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(patient_id, caregiver_id)
);

CREATE INDEX idx_patient_caregivers_patient ON patient_caregivers(patient_id);
CREATE INDEX idx_patient_caregivers_caregiver ON patient_caregivers(caregiver_id);

-- ========================================
-- CALL LOGS (Enhanced with direction tracking)
-- ========================================

CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Call metadata
    call_sid VARCHAR(100),  -- Twilio call ID
    call_direction VARCHAR(20) NOT NULL,  -- "outbound_scheduled", "outbound_followup", "inbound_patient"
    call_status VARCHAR(20) DEFAULT 'completed',  -- completed, missed, failed
    
    -- Timing
    scheduled_at TIMESTAMPTZ,  -- If outbound scheduled call
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    
    -- Conversation data
    transcript TEXT,
    audio_recording_url TEXT,
    
    -- Agent activity
    agents_involved TEXT[],  -- ["health_monitoring", "service_concierge"]
    tasks_completed JSONB[],  -- [{agent: "health", task: "diet_report", status: "completed"}]
    
    -- Entries created during this call
    diet_report_id UUID REFERENCES diet_reports(id),
    medication_adherence_id UUID REFERENCES medication_adherence(id),
    wellness_report_id UUID REFERENCES wellness_reports(id),
    cognitive_test_id UUID REFERENCES cognitive_test_reports(id),
    
    -- Service requests mentioned (not actually booked in MVP)
    service_requests_mentioned JSONB[],  -- [{type: "ride", details: "Uber to Dr. Singh"}]
    
    -- Sentiment
    patient_mood VARCHAR(20),  -- "positive", "neutral", "concerned", "distressed"
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_call_logs_patient ON call_logs(patient_id, started_at DESC);
CREATE INDEX idx_call_logs_direction ON call_logs(call_direction, started_at DESC);

-- View: Call summary by patient
CREATE VIEW patient_call_summary AS
SELECT 
    patient_id,
    COUNT(*) as total_calls,
    COUNT(*) FILTER (WHERE call_direction LIKE 'outbound%') as outbound_calls,
    COUNT(*) FILTER (WHERE call_direction = 'inbound_patient') as inbound_calls,
    COUNT(*) FILTER (WHERE call_status = 'missed') as missed_calls,
    AVG(duration_seconds) as avg_call_duration,
    MAX(started_at) as last_call_at
FROM call_logs
GROUP BY patient_id;
