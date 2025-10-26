# 🗄️ GrandFLOW Database Migrations

## 📋 What's in This Folder

This folder contains **SQL migration files** that create the complete database schema for GrandFLOW.

---

## ✅ **Migration Files (Use These!)**

### **Proper Migration Files** ✨

These are the **correct, conflict-free** migration files to use:

1. **`001_core_schema.sql`** - Users, patients, and relationships
2. **`002_health_tracking.sql`** - Health monitoring tables
3. **`003_cognitive_and_services.sql`** - Cognitive tests and service requests
4. **`004_call_logs.sql`** - Call tracking and logging
5. **`005_storage_and_rls.sql`** - Storage buckets and security policies

### **Quick Setup File** ⚡

- **`QUICK_SETUP.sql`** - Run this ONE file to set up everything at once!

### **Documentation** 📚

- **`SETUP_GUIDE.md`** - Detailed step-by-step instructions
- **`README.md`** - This file

---

## 🚀 Quick Start

### **Option 1: Run All-In-One File (Easiest)**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard) → **SQL Editor**
2. Open `QUICK_SETUP.sql`
3. Copy **entire file**
4. Paste in SQL Editor
5. Click **Run**
6. Done! ✅

### **Option 2: Run Individual Migrations (Recommended for production)**

Run each file in order (001 → 005):

```bash
# In Supabase SQL Editor, run these in sequence:
1. 001_core_schema.sql
2. 002_health_tracking.sql
3. 003_cognitive_and_services.sql
4. 004_call_logs.sql
5. 005_storage_and_rls.sql
```

See `SETUP_GUIDE.md` for detailed instructions.

---

## 📊 What Gets Created

### **Tables** (12 total)

#### Core:
- `users` - Caregivers and family members
- `patients` - Elderly individuals receiving care
- `patient_caregivers` - Many-to-many relationships

#### Health Tracking:
- `diet_reports` - Daily diet check-ins
- `medication_adherence` - Medication tracking
- `wellness_reports` - Exercise, sleep, mood
- `symptom_reports` - Symptom tracking and severity

#### Cognitive & Services:
- `cognitive_test_reports` - Weekly TICS/MMSE tests
- `rideshare_tasks` - Uber/Lyft bookings
- `delivery_tasks` - DoorDash/Instacart orders
- `vitals_timeseries` - Wearable device data

#### Call Management:
- `call_logs` - Complete call history and AI agent activity

### **Storage Buckets** (2 total)

- `call-audio` (public) - Fish Audio TTS/STT files for Twilio
- `patient-documents` (private) - Patient documents and files

### **Views** (3 total)

- `daily_health_summary` - Aggregated health metrics by day
- `cognitive_history` - Cognitive test scores over time
- `patient_call_summary` - Call statistics per patient

### **Functions** (3 total)

- `update_updated_at_column()` - Auto-update timestamps
- `calculate_call_duration()` - Compute call duration
- `update_call_agents()` - Track AI agent involvement

---

## 🔗 How This Connects to Your Code

### **database_tools.py** uses these tables:

```python
# Tools insert data into:
- diet_reports
- medication_adherence
- wellness_reports
- symptom_reports
- cognitive_test_reports
- rideshare_tasks
- delivery_tasks
- call_logs
```

### **API endpoints** (dashboard.py) query:

```python
# Endpoints read from:
- patients
- patient_caregivers
- all health tracking tables
- call_logs
- service tables
```

### **CallOrchestrator** logs to:

```python
# Orchestrator writes to:
- call_logs (start, end, agent activity)
- Links to health entries via call_id
```

---

## ⚠️ Important Notes

### **Do NOT Use These Old Files:**

- `001_initial_schema.sql` (OLD - has conflicts)
- `002_initial_schema.sql` (OLD - has conflicts)

These files had duplicate table definitions and would cause errors. They've been replaced by the new migration files.

---

## ✅ After Running Migrations

### **1. Verify Setup**

```sql
-- Check all tables exist
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Check storage buckets
SELECT * FROM storage.buckets;
```

### **2. Add Test Data**

```sql
-- Add yourself as a test patient
INSERT INTO patients (
    first_name, 
    last_name, 
    date_of_birth, 
    phone_number
)
VALUES (
    'Your Name',
    'Last Name',
    '1950-01-15',
    '+1234567890'  -- YOUR ACTUAL PHONE NUMBER
);
```

### **3. Get API Keys**

In Supabase Dashboard → **Settings** → **API**:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbG...  # Copy anon key
SUPABASE_SERVICE_KEY=eyJhbG...  # Copy service_role key
```

### **4. Update Backend .env**

```bash
cd ../../backend
nano .env

# Add the Supabase credentials
```

---

## 🐛 Troubleshooting

### **Error: "relation already exists"**

**Cause**: Table was already created in a previous run

**Fix**: Either skip (safe to ignore) or drop and recreate:
```sql
DROP TABLE IF EXISTS table_name CASCADE;
```

### **Error: "permission denied"**

**Cause**: Need admin/owner permissions

**Fix**: Ensure you're logged in as project owner

### **Storage bucket errors**

**Cause**: Bucket already exists

**Fix**: Check existing buckets:
```sql
SELECT * FROM storage.buckets;
```

### **RLS blocking backend access**

**Cause**: Using wrong API key

**Fix**: Use `service_role` key in backend .env (it bypasses RLS)

---

## 📚 Documentation

- **Detailed Setup**: See `SETUP_GUIDE.md`
- **Quick Reference**: This file
- **All-in-one**: Use `QUICK_SETUP.sql`

---

## 🎯 Migration Summary

| File | Tables Created | Purpose |
|------|----------------|---------|
| 001 | 3 | Core users and patients |
| 002 | 4 | Health tracking |
| 003 | 4 | Cognitive tests and services |
| 004 | 1 | Call logs and tracking |
| 005 | 0 | Storage and security |

**Total**: 12 tables, 2 storage buckets, 3 views, 3 functions

---

## ✨ You're All Set!

After running these migrations:

1. ✅ Database schema is complete
2. ✅ Storage buckets are configured
3. ✅ Security policies are set
4. ✅ Your code will work with the database

**Next**: Add API keys to `.env` and start your backend! 🚀

---

**Last Updated**: October 2025  
**Version**: 1.0  
**Status**: ✅ Production Ready

