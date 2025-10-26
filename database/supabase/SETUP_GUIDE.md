# 🗄️ Supabase Database Setup Guide

## 📋 Overview

This guide will help you set up your Supabase database for the GrandFLOW project. The migrations are organized in a logical order and must be run sequentially.

---

## 🚀 Quick Start (5 Steps)

### Step 1: Access Supabase SQL Editor

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Click **SQL Editor** in the left sidebar
4. You'll use this to run all migration files

---

### Step 2: Run Migrations in Order

**IMPORTANT**: Run these files **IN ORDER** from 001 to 005!

#### **Migration 001: Core Schema** ✅

**File**: `001_core_schema.sql`

**What it creates**:
- `users` table (caregivers/family members)
- `patients` table (elderly individuals)
- `patient_caregivers` table (relationships)
- Auto-update triggers for timestamps

**How to run**:
1. In SQL Editor, click **+ New Query**
2. Copy entire contents of `001_core_schema.sql`
3. Paste into editor
4. Click **Run** (or press Cmd/Ctrl + Enter)
5. Wait for "Success" message

---

#### **Migration 002: Health Tracking** ✅

**File**: `002_health_tracking.sql`

**What it creates**:
- `diet_reports` table
- `medication_adherence` table
- `wellness_reports` table
- `symptom_reports` table
- `daily_health_summary` view

**How to run**:
1. New Query in SQL Editor
2. Copy entire contents of `002_health_tracking.sql`
3. Paste and **Run**

---

#### **Migration 003: Cognitive & Services** ✅

**File**: `003_cognitive_and_services.sql`

**What it creates**:
- `cognitive_test_reports` table
- `rideshare_tasks` table
- `delivery_tasks` table
- `vitals_timeseries` table
- Views for cognitive history and latest vitals

**How to run**:
1. New Query in SQL Editor
2. Copy entire contents of `003_cognitive_and_services.sql`
3. Paste and **Run**

---

#### **Migration 004: Call Logs** ✅

**File**: `004_call_logs.sql`

**What it creates**:
- `call_logs` table (tracks all voice calls)
- Views for call summaries
- Functions for call duration calculation
- Helper functions for agent tracking

**How to run**:
1. New Query in SQL Editor
2. Copy entire contents of `004_call_logs.sql`
3. Paste and **Run**

---

#### **Migration 005: Storage & Security** ✅

**File**: `005_storage_and_rls.sql`

**What it creates**:
- Storage buckets (`call-audio`, `patient-documents`)
- Storage policies (for public/authenticated access)
- Row Level Security (RLS) policies
- Permission grants

**How to run**:
1. New Query in SQL Editor
2. Copy entire contents of `005_storage_and_rls.sql`
3. Paste and **Run**

---

### Step 3: Verify Setup

After running all migrations, verify everything is created:

```sql
-- Check tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Should show:
-- call_logs
-- cognitive_test_reports
-- delivery_tasks
-- diet_reports
-- medication_adherence
-- patient_caregivers
-- patients
-- rideshare_tasks
-- symptom_reports
-- users
-- vitals_timeseries
-- wellness_reports
```

Check storage buckets:
```sql
SELECT * FROM storage.buckets;

-- Should show:
-- call-audio (public)
-- patient-documents (private)
```

---

### Step 4: Add Test Data

Add yourself as a test patient so you can make calls:

```sql
-- Insert a test patient (USE YOUR REAL PHONE NUMBER!)
INSERT INTO patients (
    first_name, 
    last_name, 
    date_of_birth, 
    phone_number,
    conditions,
    medications,
    preferred_call_times
)
VALUES (
    'John',                          -- Change to your first name
    'Doe',                           -- Change to your last name
    '1950-01-15',                    -- Change to a date (elderly person)
    '+1234567890',                   -- ⚠️ CHANGE TO YOUR ACTUAL PHONE NUMBER
    ARRAY['hypertension', 'diabetes'],
    '[{"name": "Lisinopril", "dosage": "10mg"}, {"name": "Metformin", "dosage": "500mg"}]'::JSONB,
    ARRAY['09:00:00', '14:00:00', '19:00:00']::TIME[]
)
RETURNING id, first_name, last_name, phone_number;

-- Copy the returned ID, you'll need it!
```

Optional: Add a caregiver user (for dashboard access):

```sql
-- Insert a caregiver
INSERT INTO users (
    email,
    first_name,
    last_name,
    phone_number,
    user_type
)
VALUES (
    'caregiver@example.com',         -- Change to your email
    'Jane',                          -- Change to your name
    'Smith',
    '+1234567891',                   -- Different from patient
    'caregiver'
)
RETURNING id, email, first_name;

-- Link caregiver to patient
INSERT INTO patient_caregivers (
    patient_id,
    caregiver_id,
    relationship,
    is_primary
)
VALUES (
    'PATIENT_ID_FROM_ABOVE',         -- Use the patient ID from above
    'CAREGIVER_ID_FROM_ABOVE',       -- Use the caregiver ID from above
    'daughter',                      -- Or 'son', 'spouse', etc.
    true
);
```

---

### Step 5: Get Your API Keys

1. In Supabase Dashboard, go to **Settings** → **API**
2. Copy these values to your `.env` file:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbG...  # anon/public key
SUPABASE_SERVICE_KEY=eyJhbG...  # service_role key (keep secret!)
```

---

## ✅ Verification Checklist

Before starting your backend, verify:

- [ ] All 5 migrations ran successfully (no errors)
- [ ] 12 tables exist in public schema
- [ ] 2 storage buckets exist (`call-audio`, `patient-documents`)
- [ ] Test patient added with **your actual phone number**
- [ ] API keys copied to `.env` file
- [ ] Storage policies are set (public read for `call-audio`)

---

## 🔍 Troubleshooting

### Error: "relation already exists"

**Solution**: Table already created. Safe to ignore or drop table first:
```sql
DROP TABLE IF EXISTS table_name CASCADE;
-- Then re-run migration
```

### Error: "permission denied for schema public"

**Solution**: You need to be the project owner or have admin access.

### Storage bucket creation fails

**Solution**: Buckets might already exist. Check:
```sql
SELECT * FROM storage.buckets;
```

If they exist, skip that part or delete and recreate:
```sql
DELETE FROM storage.buckets WHERE id = 'call-audio';
-- Then re-run migration
```

### RLS policies blocking access

**Solution**: Your backend uses `service_role` key which bypasses RLS. Make sure you're using the right key in `.env`:
```env
SUPABASE_KEY=eyJhbG... # Should be service_role for backend
```

---

## 📊 Database Schema Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE STRUCTURE                       │
└─────────────────────────────────────────────────────────────┘

Core Tables:
├── users (caregivers)
├── patients (elderly)
└── patient_caregivers (relationships)

Health Tracking:
├── diet_reports
├── medication_adherence
├── wellness_reports
├── symptom_reports
└── vitals_timeseries

Cognitive & Services:
├── cognitive_test_reports
├── rideshare_tasks
└── delivery_tasks

Call Management:
└── call_logs

Storage Buckets:
├── call-audio (public - for Fish Audio TTS)
└── patient-documents (private)
```

---

## 🎯 Next Steps

After completing this setup:

1. ✅ **Update your backend `.env`** with Supabase credentials
2. ✅ **Add other API keys** (OpenRouter, Fish Audio, Twilio)
3. ✅ **Run backend**: `uvicorn app.main:app --reload`
4. ✅ **Test with**: `python test_orchestrator_integration.py`
5. ✅ **Make a real call** to your Twilio number!

---

## 📚 Additional Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
- [Storage Guide](https://supabase.com/docs/guides/storage)

---

**Setup Complete!** 🎉

Your database is now ready for GrandFLOW voice calls and AI agent interactions!

