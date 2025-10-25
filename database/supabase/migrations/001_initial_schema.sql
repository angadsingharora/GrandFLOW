-- database/supabase/migrations/001_initial_schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- USERS & PROFILES
-- ========================================

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    address JSONB,
    emergency_contacts JSONB[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE medical_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    conditions TEXT[],
    allergies TEXT[],
    medications JSONB[],
    dietary_restrictions TEXT[],
    primary_care_physician JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ========================================
-- HEALTH MONITORING ENTRIES
-- ========================================

-- Diet Reports
CREATE TABLE diet_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_id UUID,  -- Links to conversation
    date DATE DEFAULT CURRENT_DATE,
    
    -- Entry data
    macronutrients JSONB,  -- {protein: 80, carbs: 200, fats: 60}
    calories INTEGER,
    meals_count INTEGER,
    vitamins TEXT[],
    recommendations TEXT[],
    
    -- Computed scores
    diet_quality_score INTEGER CHECK (diet_quality_score BETWEEN 0 AND 100),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_diet_reports_user_date ON diet_reports(user_id, date DESC);

-- Medication Adherence
CREATE TABLE medication_adherence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    
    -- Entry data
    medicines_prescribed JSONB[],  -- [{name: "Lisinopril", dosage: "10mg", time: "08:00"}]
    medicines_taken JSONB[],       -- [{name: "Lisinopril", time_taken: "08:15"}]
    
    -- Computed metrics
    adherence_rate NUMERIC(5,2),  -- Percentage
    medications_missed TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_medication_adherence_user_date ON medication_adherence(user_id, date DESC);

-- Physical/Mental Wellness Reports
CREATE TABLE wellness_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    
    -- Entry data
    exercise_completed BOOLEAN,
    steps INTEGER,
    calories_burned INTEGER,
    sleep_duration INTEGER,  -- in minutes
    recommendations TEXT[],
    
    -- Computed scores
    exercise_quality_score INTEGER CHECK (exercise_quality_score BETWEEN 0 AND 100),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_wellness_reports_user_date ON wellness_reports(user_id, date DESC);

-- Symptom Reports (separate from wellness)
CREATE TABLE symptom_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    
    symptoms_reported TEXT[],
    severity_scores JSONB,  -- {pain: 5, fatigue: 3}
    symptom_quality_score INTEGER CHECK (symptom_quality_score BETWEEN 0 AND 100),
    recommendations TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_symptom_reports_user_date ON symptom_reports(user_id, date DESC);

-- ========================================
-- COGNITIVE TESTING ENTRIES
-- ========================================

CREATE TABLE cognitive_test_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_id UUID,
    test_date DATE DEFAULT CURRENT_DATE,
    
    -- TICS Test Results
    tics_score JSONB,  -- {total: 35, orientation: 5, registration: 3, attention: 5, ...}
    mmse_equivalent INTEGER,  -- Converted TICS to MMSE score
    
    -- Cognitive domains breakdown
    orientation_score INTEGER,
    memory_score INTEGER,
    attention_score INTEGER,
    language_score INTEGER,
    
    -- Classification
    cognitive_quality_score INTEGER CHECK (cognitive_quality_score BETWEEN 0 AND 100),
    risk_level VARCHAR(20),  -- "normal", "mild_impairment", "moderate_impairment", "severe"
    recommendations TEXT[],
    
    -- Comparison to baseline
    baseline_comparison JSONB,  -- {change_from_baseline: -2, trend: "declining"}
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_cognitive_tests_user_date ON cognitive_test_reports(user_id, test_date DESC);

-- ========================================
-- SERVICE CONCIERGE ENTRIES
-- ========================================

-- Rideshare Tasks
CREATE TABLE rideshare_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_id UUID,
    
    -- Entry data
    company VARCHAR(50),  -- "uber", "lyft"
    pickup_location VARCHAR(255),
    dropoff_location VARCHAR(255),
    time_booked TIMESTAMPTZ,
    scheduled_for TIMESTAMPTZ,
    
    -- Tracking
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, completed, cancelled
    external_ride_id VARCHAR(255),
    driver_name VARCHAR(100),
    actual_pickup_time TIMESTAMPTZ,
    actual_dropoff_time TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_rideshare_tasks_user ON rideshare_tasks(user_id, time_booked DESC);

-- Delivery Tasks
CREATE TABLE delivery_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    call_id UUID,
    
    -- Entry data
    item VARCHAR(255),  -- "Groceries from Instacart", "Lunch from DoorDash"
    service_provider VARCHAR(50),  -- "doordash", "instacart", "pharmacy"
    time_booked TIMESTAMPTZ,
    scheduled_for TIMESTAMPTZ,
    
    -- Details
    items_ordered JSONB[],  -- [{name: "Salmon", quantity: 1}]
    
    -- Tracking
    status VARCHAR(20) DEFAULT 'pending',
    external_order_id VARCHAR(255),
    estimated_delivery TIMESTAMPTZ,
    actual_delivery TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_delivery_tasks_user ON delivery_tasks(user_id, time_booked DESC);

-- ========================================
-- VITALS FROM WEARABLES (Time-series)
-- ========================================

CREATE TABLE vitals_timeseries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    metric_type VARCHAR(50) NOT NULL,  -- "heart_rate", "blood_pressure", "spo2", "steps"
    value NUMERIC NOT NULL,
    unit VARCHAR(20),
    metadata JSONB,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_vitals_user_time ON vitals_timeseries(user_id, timestamp DESC);
CREATE INDEX idx_vitals_metric ON vitals_timeseries(metric_type, timestamp DESC);

-- ========================================
-- CALL LOGS (Track conversations)
-- ========================================

CREATE TABLE call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    call_sid VARCHAR(100),  -- Twilio call ID
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    
    -- Conversation data
    transcript TEXT,
    audio_recording_url TEXT,
    
    -- Agent activity
    agents_involved TEXT[],  -- ["health_monitoring", "service_concierge"]
    tasks_completed JSONB[],  -- [{agent: "health", task: "diet_report"}]
    
    -- Sentiment analysis
    user_mood VARCHAR(20),  -- "positive", "neutral", "concerned", "distressed"
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_call_logs_user ON call_logs(user_id, started_at DESC);

-- ========================================
-- AGGREGATE VIEWS FOR DASHBOARD
-- ========================================

-- Daily health summary
CREATE VIEW daily_health_summary AS
SELECT 
    user_id,
    date,
    MAX(diet_quality_score) as diet_quality,
    MAX(exercise_quality_score) as exercise_quality,
    MAX(symptom_quality_score) as symptom_quality,
    AVG(adherence_rate) as medication_adherence,
    COUNT(DISTINCT call_id) as check_ins_today
FROM (
    SELECT user_id, date, diet_quality_score, NULL as exercise_quality_score, 
           NULL as symptom_quality_score, NULL as adherence_rate, call_id 
    FROM diet_reports
    UNION ALL
    SELECT user_id, date, NULL, exercise_quality_score, NULL, NULL, call_id 
    FROM wellness_reports
    UNION ALL
    SELECT user_id, date, NULL, NULL, symptom_quality_score, NULL, call_id 
    FROM symptom_reports
    UNION ALL
    SELECT user_id, date, NULL, NULL, NULL, adherence_rate, call_id 
    FROM medication_adherence
) combined
GROUP BY user_id, date;

-- Recent cognitive scores
CREATE VIEW cognitive_history AS
SELECT 
    user_id,
    test_date,
    tics_score,
    cognitive_quality_score,
    risk_level,
    LAG(cognitive_quality_score) OVER (PARTITION BY user_id ORDER BY test_date) as previous_score
FROM cognitive_test_reports
ORDER BY user_id, test_date DESC;
