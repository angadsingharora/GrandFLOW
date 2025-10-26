-- ============================================================================
-- GrandFLOW Call Logs and Conversation Tracking
-- Version: 1.0
-- Description: Track all voice call interactions and AI agent activities
-- ============================================================================

-- ============================================================================
-- CALL LOGS
-- ============================================================================

CREATE TABLE IF NOT EXISTS call_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID REFERENCES patients(id) ON DELETE CASCADE,
    
    -- Twilio call metadata
    call_sid VARCHAR(100) UNIQUE,  -- Twilio Call SID
    call_direction VARCHAR(30) NOT NULL,  -- "outbound_scheduled", "outbound_followup", "inbound_patient"
    call_status VARCHAR(20) DEFAULT 'completed',  -- completed, missed, failed, in_progress
    
    -- Timing
    scheduled_at TIMESTAMPTZ,  -- For scheduled calls
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    duration_seconds INTEGER,
    
    -- Conversation data
    transcript TEXT,
    audio_recording_url TEXT,
    
    -- AI Agent activity tracking
    agents_involved TEXT[] DEFAULT ARRAY[]::TEXT[],  -- ["health_monitoring", "cognitive_testing", "service_concierge"]
    tasks_completed JSONB DEFAULT '[]'::JSONB,  -- [{agent: "health", task: "diet_report", status: "completed", timestamp: "..."}]
    
    -- Linked entries created during this call
    diet_report_id UUID REFERENCES diet_reports(id),
    medication_adherence_id UUID REFERENCES medication_adherence(id),
    wellness_report_id UUID REFERENCES wellness_reports(id),
    cognitive_test_id UUID REFERENCES cognitive_test_reports(id),
    symptom_report_id UUID REFERENCES symptom_reports(id),
    
    -- Service requests mentioned (may not be actually booked in MVP)
    service_requests_mentioned JSONB DEFAULT '[]'::JSONB,  -- [{type: "ride", details: "Uber to Dr. Singh"}]
    
    -- Sentiment analysis
    patient_mood VARCHAR(30),  -- "positive", "neutral", "concerned", "distressed", "happy"
    sentiment_score NUMERIC(3,2),  -- -1.0 to 1.0
    
    -- Call quality
    call_quality_rating INTEGER CHECK (call_quality_rating BETWEEN 1 AND 5),
    technical_issues TEXT[],  -- ["poor_audio", "dropped_connection", "speech_recognition_error"]
    
    -- Notes
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_call_logs_patient ON call_logs(patient_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_call_logs_direction ON call_logs(call_direction, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_call_logs_status ON call_logs(call_status);
CREATE INDEX IF NOT EXISTS idx_call_logs_started ON call_logs(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_call_logs_sid ON call_logs(call_sid);

-- ============================================================================
-- CALL SUMMARY VIEW
-- ============================================================================

CREATE OR REPLACE VIEW patient_call_summary AS
SELECT 
    patient_id,
    COUNT(*) as total_calls,
    COUNT(*) FILTER (WHERE call_direction LIKE 'outbound%') as outbound_calls,
    COUNT(*) FILTER (WHERE call_direction = 'inbound_patient') as inbound_calls,
    COUNT(*) FILTER (WHERE call_status = 'missed') as missed_calls,
    COUNT(*) FILTER (WHERE call_status = 'completed') as completed_calls,
    AVG(duration_seconds) FILTER (WHERE duration_seconds > 0) as avg_call_duration,
    MAX(started_at) as last_call_at,
    MIN(started_at) as first_call_at,
    
    -- Agent activity stats
    (SELECT COUNT(*) FROM unnest(array_agg(agents_involved)) WHERE unnest = 'health_monitoring') as health_monitoring_count,
    (SELECT COUNT(*) FROM unnest(array_agg(agents_involved)) WHERE unnest = 'cognitive_testing') as cognitive_testing_count,
    (SELECT COUNT(*) FROM unnest(array_agg(agents_involved)) WHERE unnest = 'service_concierge') as service_concierge_count
FROM call_logs
GROUP BY patient_id;

-- ============================================================================
-- RECENT CALLS VIEW (with patient info)
-- ============================================================================

CREATE OR REPLACE VIEW recent_calls_with_patients AS
SELECT 
    cl.id,
    cl.call_sid,
    cl.patient_id,
    p.first_name || ' ' || p.last_name as patient_name,
    p.phone_number as patient_phone,
    cl.call_direction,
    cl.call_status,
    cl.started_at,
    cl.ended_at,
    cl.duration_seconds,
    cl.agents_involved,
    cl.patient_mood,
    cl.created_at
FROM call_logs cl
JOIN patients p ON cl.patient_id = p.id
ORDER BY cl.started_at DESC;

-- ============================================================================
-- FUNCTION: Calculate Call Duration on End
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_call_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_call_duration
    BEFORE INSERT OR UPDATE ON call_logs
    FOR EACH ROW
    EXECUTE FUNCTION calculate_call_duration();

-- ============================================================================
-- FUNCTION: Update Call Agents Array
-- ============================================================================

CREATE OR REPLACE FUNCTION update_call_agents(
    p_call_id UUID,
    p_agent_name TEXT
)
RETURNS VOID AS $$
BEGIN
    UPDATE call_logs
    SET agents_involved = array_append(agents_involved, p_agent_name)
    WHERE id = p_call_id
    AND NOT (p_agent_name = ANY(agents_involved));  -- Avoid duplicates
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- FUNCTION: Add Task to Call Log
-- ============================================================================

CREATE OR REPLACE FUNCTION add_call_task(
    p_call_id UUID,
    p_task JSONB
)
RETURNS VOID AS $$
BEGIN
    UPDATE call_logs
    SET tasks_completed = tasks_completed || p_task
    WHERE id = p_call_id;
END;
$$ LANGUAGE plpgsql;

