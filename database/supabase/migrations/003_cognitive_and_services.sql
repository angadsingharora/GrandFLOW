-- ============================================================================
-- GrandFLOW Cognitive Testing and Services Schema
-- Version: 1.0
-- Description: Weekly cognitive tests and service concierge features
-- ============================================================================

-- ============================================================================
-- COGNITIVE TEST REPORTS (TICS/MMSE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS cognitive_test_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    test_date DATE DEFAULT CURRENT_DATE,
    
    -- TICS Test Results (Telephone Interview for Cognitive Status)
    tics_score JSONB DEFAULT '{}'::JSONB,  -- {total: 35, orientation: 5, registration: 3, attention: 5, ...}
    tics_total INTEGER,  -- Total TICS score (0-41)
    mmse_equivalent INTEGER,  -- Converted TICS to MMSE score (0-30)
    
    -- Cognitive domains breakdown
    orientation_score INTEGER,  -- Date, time, location awareness
    memory_score INTEGER,       -- Word recall, recognition
    attention_score INTEGER,    -- Counting, serial 7s
    language_score INTEGER,     -- Naming, repetition
    calculation_score INTEGER,  -- Simple arithmetic
    
    -- Test details
    questions_asked JSONB DEFAULT '[]'::JSONB,  -- Record of questions and answers
    test_duration_seconds INTEGER,
    
    -- Classification
    cognitive_quality_score INTEGER CHECK (cognitive_quality_score BETWEEN 0 AND 100),
    risk_level VARCHAR(20) DEFAULT 'normal',  -- "normal", "mild_impairment", "moderate_impairment", "severe"
    
    -- Comparison to baseline
    baseline_comparison JSONB,  -- {change_from_baseline: -2, trend: "declining", previous_score: 28}
    
    -- AI insights
    recommendations TEXT[] DEFAULT ARRAY[]::TEXT[],
    requires_followup BOOLEAN DEFAULT false,
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cognitive_tests_user_date ON cognitive_test_reports(user_id, test_date DESC);
CREATE INDEX IF NOT EXISTS idx_cognitive_tests_risk ON cognitive_test_reports(risk_level, test_date DESC);
CREATE INDEX IF NOT EXISTS idx_cognitive_tests_call ON cognitive_test_reports(call_id);

-- ============================================================================
-- COGNITIVE HISTORY VIEW
-- ============================================================================

CREATE OR REPLACE VIEW cognitive_history AS
SELECT 
    user_id,
    test_date,
    tics_total,
    mmse_equivalent,
    cognitive_quality_score,
    risk_level,
    LAG(cognitive_quality_score) OVER (PARTITION BY user_id ORDER BY test_date) as previous_score,
    LAG(test_date) OVER (PARTITION BY user_id ORDER BY test_date) as previous_test_date,
    cognitive_quality_score - LAG(cognitive_quality_score) OVER (PARTITION BY user_id ORDER BY test_date) as score_change
FROM cognitive_test_reports
ORDER BY user_id, test_date DESC;

-- ============================================================================
-- RIDESHARE TASKS (Uber, Lyft)
-- ============================================================================

CREATE TABLE IF NOT EXISTS rideshare_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    
    -- Booking information
    company VARCHAR(50),  -- "uber", "lyft"
    pickup_location VARCHAR(255) NOT NULL,
    dropoff_location VARCHAR(255) NOT NULL,
    pickup_time TIMESTAMPTZ,
    
    -- Ride details
    ride_type VARCHAR(50),  -- "standard", "xl", "assist" (for wheelchair accessible)
    estimated_cost NUMERIC(10,2),
    notes TEXT,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, in_progress, completed, cancelled
    external_ride_id VARCHAR(255),
    driver_name VARCHAR(100),
    driver_phone VARCHAR(20),
    vehicle_info VARCHAR(100),
    
    -- Timestamps
    booked_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    pickup_actual TIMESTAMPTZ,
    dropoff_actual TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rideshare_tasks_user ON rideshare_tasks(user_id, booked_at DESC);
CREATE INDEX IF NOT EXISTS idx_rideshare_tasks_status ON rideshare_tasks(status, pickup_time);
CREATE INDEX IF NOT EXISTS idx_rideshare_tasks_call ON rideshare_tasks(call_id);

-- ============================================================================
-- DELIVERY TASKS (DoorDash, Instacart, Pharmacy)
-- ============================================================================

CREATE TABLE IF NOT EXISTS delivery_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    call_id UUID,
    
    -- Order information
    service_provider VARCHAR(50),  -- "doordash", "instacart", "pharmacy", "amazon"
    delivery_type VARCHAR(50),  -- "food", "groceries", "medications", "supplies"
    restaurant_or_store VARCHAR(255),
    
    -- Delivery details
    delivery_address VARCHAR(255),
    items_ordered JSONB DEFAULT '[]'::JSONB,  -- [{name: "Salmon", quantity: 1, price: 12.99}]
    special_instructions TEXT,
    
    -- Cost
    subtotal NUMERIC(10,2),
    delivery_fee NUMERIC(10,2),
    tip NUMERIC(10,2),
    total_cost NUMERIC(10,2),
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, preparing, out_for_delivery, delivered, cancelled
    external_order_id VARCHAR(255),
    driver_name VARCHAR(100),
    
    -- Timestamps
    ordered_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed_at TIMESTAMPTZ,
    estimated_delivery TIMESTAMPTZ,
    actual_delivery TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_delivery_tasks_user ON delivery_tasks(user_id, ordered_at DESC);
CREATE INDEX IF NOT EXISTS idx_delivery_tasks_status ON delivery_tasks(status, estimated_delivery);
CREATE INDEX IF NOT EXISTS idx_delivery_tasks_type ON delivery_tasks(delivery_type, ordered_at DESC);
CREATE INDEX IF NOT EXISTS idx_delivery_tasks_call ON delivery_tasks(call_id);

-- ============================================================================
-- VITALS FROM WEARABLES (Time-series data)
-- ============================================================================

CREATE TABLE IF NOT EXISTS vitals_timeseries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    
    -- Vital sign data
    metric_type VARCHAR(50) NOT NULL,  -- "heart_rate", "blood_pressure_systolic", "blood_pressure_diastolic", "spo2", "steps", "weight"
    value NUMERIC NOT NULL,
    unit VARCHAR(20),  -- "bpm", "mmHg", "%", "steps", "lbs"
    
    -- Source
    source VARCHAR(50),  -- "apple_watch", "fitbit", "manual_entry", "spike_api"
    device_id VARCHAR(100),
    
    -- Additional data
    metadata JSONB,  -- Any additional context
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vitals_user_time ON vitals_timeseries(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_vitals_metric ON vitals_timeseries(metric_type, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_vitals_user_metric ON vitals_timeseries(user_id, metric_type, timestamp DESC);

-- ============================================================================
-- VITALS SUMMARY VIEW (Latest readings)
-- ============================================================================

CREATE OR REPLACE VIEW latest_vitals AS
SELECT DISTINCT ON (user_id, metric_type)
    user_id,
    metric_type,
    value,
    unit,
    timestamp,
    source
FROM vitals_timeseries
ORDER BY user_id, metric_type, timestamp DESC;

