-- ============================================================================
-- GrandFLOW Core Schema Migration
-- Version: 1.0
-- Description: Core tables for users, patients, and relationships
-- ============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- ============================================================================
-- USERS TABLE (Caregivers/Family Members)
-- ============================================================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    user_type VARCHAR(20) DEFAULT 'caregiver',  -- caregiver, admin
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);

-- ============================================================================
-- PATIENTS TABLE (Elderly individuals receiving care)
-- ============================================================================

CREATE TABLE IF NOT EXISTS patients (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,  -- For receiving AI calls
    email VARCHAR(255),
    
    -- Address information
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(50) DEFAULT 'USA',
    
    -- Emergency contacts (JSONB array)
    emergency_contacts JSONB DEFAULT '[]'::JSONB,
    
    -- Medical information
    conditions TEXT[] DEFAULT ARRAY[]::TEXT[],
    allergies TEXT[] DEFAULT ARRAY[]::TEXT[],
    medications JSONB DEFAULT '[]'::JSONB,
    dietary_restrictions TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Primary care physician info
    primary_care_physician JSONB,
    
    -- Call scheduling preferences
    preferred_call_times TIME[] DEFAULT ARRAY['09:00:00', '14:00:00']::TIME[],
    call_frequency VARCHAR(20) DEFAULT 'daily',  -- daily, weekly, on_demand
    timezone VARCHAR(50) DEFAULT 'America/Los_Angeles',
    
    -- Status
    active BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_patients_phone ON patients(phone_number);
CREATE INDEX IF NOT EXISTS idx_patients_active ON patients(active);
CREATE INDEX IF NOT EXISTS idx_patients_created ON patients(created_at DESC);

-- ============================================================================
-- PATIENT-CAREGIVER RELATIONSHIPS (Many-to-Many)
-- ============================================================================

CREATE TABLE IF NOT EXISTS patient_caregivers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    caregiver_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    relationship VARCHAR(50) NOT NULL,  -- daughter, son, spouse, professional_caregiver, etc.
    access_level VARCHAR(20) DEFAULT 'full',  -- full, limited (for HIPAA compliance)
    is_primary BOOLEAN DEFAULT false,  -- Primary contact for emergencies
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(patient_id, caregiver_id)
);

CREATE INDEX IF NOT EXISTS idx_patient_caregivers_patient ON patient_caregivers(patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_caregivers_caregiver ON patient_caregivers(caregiver_id);
CREATE INDEX IF NOT EXISTS idx_patient_caregivers_primary ON patient_caregivers(patient_id, is_primary);

-- ============================================================================
-- AUTO-UPDATE TIMESTAMPS
-- ============================================================================

-- Function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_patients_updated_at BEFORE UPDATE ON patients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA (Optional - for testing)
-- ============================================================================

-- Uncomment to insert test data
/*
INSERT INTO users (email, first_name, last_name, phone_number, user_type)
VALUES 
    ('test@example.com', 'Jane', 'Smith', '+15555551234', 'caregiver')
ON CONFLICT (email) DO NOTHING;

INSERT INTO patients (first_name, last_name, date_of_birth, phone_number)
VALUES 
    ('John', 'Doe', '1950-01-15', '+15555559999')
ON CONFLICT (phone_number) DO NOTHING;
*/

