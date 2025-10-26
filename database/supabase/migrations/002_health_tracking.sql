-- ============================================================================
-- GrandFLOW Health Tracking Schema
-- Version: 1.0
-- Description: Tables for daily health check-ins and monitoring
-- ============================================================================

-- ============================================================================
-- DIET REPORTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS diet_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,  -- Links to patient
    call_id UUID,  -- Links to the call where this was recorded
    date DATE DEFAULT CURRENT_DATE,
    
    -- Nutritional data
    macronutrients JSONB DEFAULT '{}'::JSONB,  -- {protein: 80, carbs: 200, fats: 60}
    calories INTEGER,
    meals_count INTEGER DEFAULT 0,
    water_intake INTEGER,  -- in oz
    vitamins TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- AI-generated insights
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    diet_quality_score INTEGER CHECK (diet_quality_score BETWEEN 0 AND 100),
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_diet_reports_user_date ON diet_reports(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_diet_reports_call ON diet_reports(call_id);

-- ============================================================================
-- MEDICATION ADHERENCE
-- ============================================================================

CREATE TABLE IF NOT EXISTS medication_adherence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    
    -- Medication tracking
    medicines_prescribed JSONB DEFAULT '[]'::JSONB,  -- [{name: "Lisinopril", dosage: "10mg", time: "08:00"}]
    medicines_taken JSONB DEFAULT '[]'::JSONB,       -- [{name: "Lisinopril", time_taken: "08:15", taken: true}]
    
    -- Computed metrics
    adherence_rate NUMERIC(5,2),  -- Percentage (0-100)
    medications_missed TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- AI insights
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_medication_adherence_user_date ON medication_adherence(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_medication_adherence_call ON medication_adherence(call_id);

-- ============================================================================
-- WELLNESS REPORTS (Exercise, Sleep, Mood)
-- ============================================================================

CREATE TABLE IF NOT EXISTS wellness_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    
    -- Physical activity
    exercise_completed BOOLEAN DEFAULT false,
    exercise_type VARCHAR(100),  -- "walking", "yoga", "stretching", etc.
    exercise_duration INTEGER,   -- in minutes
    steps INTEGER DEFAULT 0,
    calories_burned INTEGER DEFAULT 0,
    
    -- Sleep data
    sleep_duration INTEGER,  -- in minutes
    sleep_quality VARCHAR(20),  -- "poor", "fair", "good", "excellent"
    
    -- Mental wellness
    mood VARCHAR(50),  -- "happy", "content", "anxious", "sad", etc.
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    
    -- Computed scores
    exercise_quality_score INTEGER CHECK (exercise_quality_score BETWEEN 0 AND 100),
    
    -- AI insights
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wellness_reports_user_date ON wellness_reports(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_wellness_reports_call ON wellness_reports(call_id);

-- ============================================================================
-- SYMPTOM REPORTS
-- ============================================================================

CREATE TABLE IF NOT EXISTS symptom_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    date DATE DEFAULT CURRENT_DATE,
    
    -- Symptoms tracking
    symptoms_reported TEXT[] DEFAULT ARRAY[]::TEXT[],
    severity_scores JSONB DEFAULT '{}'::JSONB,  -- {pain: 5, fatigue: 3, dizziness: 2}
    
    -- Body areas affected
    body_areas TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ["chest", "head", "legs"]
    
    -- Computed assessment
    symptom_quality_score INTEGER CHECK (symptom_quality_score BETWEEN 0 AND 100),
    urgency_level VARCHAR(20),  -- "low", "medium", "high", "emergency"
    
    -- AI insights
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    requires_medical_attention BOOLEAN DEFAULT false,
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_symptom_reports_user_date ON symptom_reports(user_id, date DESC);
CREATE INDEX IF NOT EXISTS idx_symptom_reports_urgency ON symptom_reports(urgency_level, date DESC);
CREATE INDEX IF NOT EXISTS idx_symptom_reports_call ON symptom_reports(call_id);

-- ============================================================================
-- AGGREGATE VIEW: Daily Health Summary
-- ============================================================================

CREATE OR REPLACE VIEW daily_health_summary AS
SELECT 
    user_id,
    date,
    MAX(diet_quality_score) as diet_quality,
    MAX(exercise_quality_score) as exercise_quality,
    MAX(symptom_quality_score) as symptom_quality,
    AVG(adherence_rate) as medication_adherence,
    COUNT(DISTINCT call_id) as check_ins_today
FROM (
    SELECT user_id, date, diet_quality_score, NULL::INTEGER as exercise_quality_score, 
           NULL::INTEGER as symptom_quality_score, NULL::NUMERIC as adherence_rate, call_id 
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
GROUP BY user_id, date
ORDER BY date DESC;

