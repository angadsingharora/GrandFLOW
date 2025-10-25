-- Enable RLS (Row Level Security)
ALTER DATABASE postgres SET "app.jwt_secret" TO 'your-jwt-secret';

-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  role TEXT CHECK (role IN ('senior', 'family_member', 'doctor')) NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create diet_reports table
CREATE TABLE IF NOT EXISTS diet_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  macronutrients JSONB NOT NULL DEFAULT '[]',
  calories INTEGER NOT NULL,
  meals INTEGER NOT NULL,
  vitamins JSONB NOT NULL DEFAULT '[]',
  recommendations TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create medical_adherence table
CREATE TABLE IF NOT EXISTS medical_adherence (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  medicines_prescribed JSONB NOT NULL DEFAULT '[]',
  medicines_taken JSONB NOT NULL DEFAULT '[]',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create physical_mental_wellness_reports table
CREATE TABLE IF NOT EXISTS physical_mental_wellness_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  exercise BOOLEAN NOT NULL,
  steps_walking INTEGER NOT NULL,
  calories_burned INTEGER NOT NULL,
  sleep_duration DECIMAL(4,2) NOT NULL,
  recommendations TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create cognitive_test_reports table
CREATE TABLE IF NOT EXISTS cognitive_test_reports (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL,
  tics_score JSONB NOT NULL,
  recommendations JSONB NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create rideshare_tasks table
CREATE TABLE IF NOT EXISTS rideshare_tasks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  company TEXT NOT NULL,
  location TEXT NOT NULL,
  time_booked TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')) DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create delivery_tasks table
CREATE TABLE IF NOT EXISTS delivery_tasks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  item TEXT NOT NULL,
  time_booked TIMESTAMP WITH TIME ZONE NOT NULL,
  status TEXT CHECK (status IN ('pending', 'confirmed', 'completed', 'cancelled')) DEFAULT 'pending',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE diet_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE medical_adherence ENABLE ROW LEVEL SECURITY;
ALTER TABLE physical_mental_wellness_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE cognitive_test_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE rideshare_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE delivery_tasks ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Users can read their own data
CREATE POLICY "Users can read own data" ON users FOR SELECT USING (auth.uid()::text = id::text);

-- Family members and doctors can read senior data
CREATE POLICY "Family and doctors can read senior data" ON users FOR SELECT USING (
  EXISTS (
    SELECT 1 FROM users u 
    WHERE u.id = auth.uid()::uuid 
    AND u.role IN ('family_member', 'doctor')
  )
);

-- Similar policies for all health data tables
CREATE POLICY "Users can read own diet reports" ON diet_reports FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own diet reports" ON diet_reports FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own diet reports" ON diet_reports FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can read own medical adherence" ON medical_adherence FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own medical adherence" ON medical_adherence FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own medical adherence" ON medical_adherence FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can read own wellness reports" ON physical_mental_wellness_reports FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own wellness reports" ON physical_mental_wellness_reports FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own wellness reports" ON physical_mental_wellness_reports FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can read own cognitive reports" ON cognitive_test_reports FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own cognitive reports" ON cognitive_test_reports FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own cognitive reports" ON cognitive_test_reports FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can read own rideshare tasks" ON rideshare_tasks FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own rideshare tasks" ON rideshare_tasks FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own rideshare tasks" ON rideshare_tasks FOR UPDATE USING (auth.uid()::text = user_id::text);

CREATE POLICY "Users can read own delivery tasks" ON delivery_tasks FOR SELECT USING (auth.uid()::text = user_id::text);
CREATE POLICY "Users can insert own delivery tasks" ON delivery_tasks FOR INSERT WITH CHECK (auth.uid()::text = user_id::text);
CREATE POLICY "Users can update own delivery tasks" ON delivery_tasks FOR UPDATE USING (auth.uid()::text = user_id::text);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_diet_reports_user_date ON diet_reports(user_id, date);
CREATE INDEX IF NOT EXISTS idx_medical_adherence_user_date ON medical_adherence(user_id, date);
CREATE INDEX IF NOT EXISTS idx_wellness_reports_user_date ON physical_mental_wellness_reports(user_id, date);
CREATE INDEX IF NOT EXISTS idx_cognitive_reports_user_date ON cognitive_test_reports(user_id, date);
CREATE INDEX IF NOT EXISTS idx_rideshare_tasks_user_date ON rideshare_tasks(user_id, time_booked);
CREATE INDEX IF NOT EXISTS idx_delivery_tasks_user_date ON delivery_tasks(user_id, time_booked);
