-- ============================================================================
-- GrandFLOW Storage and Row Level Security (RLS)
-- Version: 1.0
-- Description: Set up storage buckets and basic RLS policies
-- ============================================================================

-- ============================================================================
-- STORAGE BUCKETS
-- ============================================================================

-- Create bucket for call audio files (Fish Audio TTS outputs)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'call-audio',
    'call-audio',
    true,  -- Public so Twilio can access audio URLs
    10485760,  -- 10MB limit per file
    ARRAY['audio/mpeg', 'audio/mp3', 'audio/wav']
)
ON CONFLICT (id) DO NOTHING;

-- Create bucket for patient documents (optional)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'patient-documents',
    'patient-documents',
    false,  -- Private - requires authentication
    52428800,  -- 50MB limit
    ARRAY['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================================
-- STORAGE POLICIES FOR CALL AUDIO
-- ============================================================================

-- Allow public read access to call audio (needed for Twilio)
CREATE POLICY "Public read access for call audio"
ON storage.objects FOR SELECT
TO public
USING (bucket_id = 'call-audio');

-- Allow authenticated users to upload call audio
CREATE POLICY "Authenticated upload for call audio"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'call-audio');

-- Allow service role to manage call audio
CREATE POLICY "Service role manage call audio"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'call-audio');

-- ============================================================================
-- STORAGE POLICIES FOR PATIENT DOCUMENTS
-- ============================================================================

-- Caregivers can read documents for their patients
CREATE POLICY "Caregivers read patient documents"
ON storage.objects FOR SELECT
TO authenticated
USING (
    bucket_id = 'patient-documents'
    AND (storage.foldername(name))[1] IN (
        SELECT patient_id::text
        FROM patient_caregivers
        WHERE caregiver_id = auth.uid()
    )
);

-- Service role can manage all documents
CREATE POLICY "Service role manage patient documents"
ON storage.objects FOR ALL
TO service_role
USING (bucket_id = 'patient-documents');

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Note: For MVP/development, we're keeping RLS permissive
-- In production, tighten these policies based on your security requirements

-- Enable RLS on tables
ALTER TABLE patients ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE patient_caregivers ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE diet_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE medication_adherence ENABLE ROW LEVEL SECURITY;
ALTER TABLE wellness_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE symptom_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE cognitive_test_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE rideshare_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE delivery_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE vitals_timeseries ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- SERVICE ROLE POLICIES (Full access for backend)
-- ============================================================================

-- Service role can do everything (for backend operations)
CREATE POLICY "Service role full access - patients"
ON patients FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - users"
ON users FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - patient_caregivers"
ON patient_caregivers FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - call_logs"
ON call_logs FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - diet_reports"
ON diet_reports FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - medication_adherence"
ON medication_adherence FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - wellness_reports"
ON wellness_reports FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - symptom_reports"
ON symptom_reports FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - cognitive_test_reports"
ON cognitive_test_reports FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - rideshare_tasks"
ON rideshare_tasks FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - delivery_tasks"
ON delivery_tasks FOR ALL TO service_role USING (true) WITH CHECK (true);

CREATE POLICY "Service role full access - vitals_timeseries"
ON vitals_timeseries FOR ALL TO service_role USING (true) WITH CHECK (true);

-- ============================================================================
-- AUTHENTICATED USER POLICIES (For caregivers accessing via frontend)
-- ============================================================================

-- Caregivers can read their assigned patients
CREATE POLICY "Caregivers read assigned patients"
ON patients FOR SELECT TO authenticated
USING (
    id IN (
        SELECT patient_id 
        FROM patient_caregivers 
        WHERE caregiver_id = auth.uid()
    )
);

-- Caregivers can read health data for their patients
CREATE POLICY "Caregivers read patient diet reports"
ON diet_reports FOR SELECT TO authenticated
USING (
    user_id IN (
        SELECT patient_id 
        FROM patient_caregivers 
        WHERE caregiver_id = auth.uid()
    )
);

CREATE POLICY "Caregivers read patient medication"
ON medication_adherence FOR SELECT TO authenticated
USING (
    user_id IN (
        SELECT patient_id 
        FROM patient_caregivers 
        WHERE caregiver_id = auth.uid()
    )
);

CREATE POLICY "Caregivers read patient wellness"
ON wellness_reports FOR SELECT TO authenticated
USING (
    user_id IN (
        SELECT patient_id 
        FROM patient_caregivers 
        WHERE caregiver_id = auth.uid()
    )
);

CREATE POLICY "Caregivers read patient symptoms"
ON symptom_reports FOR SELECT TO authenticated
USING (
    user_id IN (
        SELECT patient_id 
        FROM patient_caregivers 
        WHERE caregiver_id = auth.uid()
    )
);

CREATE POLICY "Caregivers read patient cognitive tests"
ON cognitive_test_reports FOR SELECT TO authenticated
USING (
    user_id IN (
        SELECT patient_id 
        FROM patient_caregivers 
        WHERE caregiver_id = auth.uid()
    )
);

CREATE POLICY "Caregivers read patient call logs"
ON call_logs FOR SELECT TO authenticated
USING (
    patient_id IN (
        SELECT patient_id 
        FROM patient_caregivers 
        WHERE caregiver_id = auth.uid()
    )
);

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================

-- Grant usage on schemas
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT ALL ON SCHEMA public TO service_role;

-- Grant permissions on all tables
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;

-- Grant permissions on sequences
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- Grant permissions on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated, service_role;

