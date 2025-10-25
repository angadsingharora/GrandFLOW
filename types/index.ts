// Health Monitoring Agent Entries
export interface DietReport {
  id?: string;
  userId: string;
  date: string;
  macronutrients: Array<{
    name: string;
    amount: number;
    unit: string;
  }>;
  calories: number;
  meals: number;
  vitamins: Array<{
    name: string;
    amount: number;
    unit: string;
  }>;
  recommendations: string[];
  createdAt?: string;
}

export interface MedicalAdherence {
  id?: string;
  userId: string;
  date: string;
  medicinesPrescribed: Array<{
    name: string;
    dosage: string;
    frequency: string;
  }>;
  medicinesTaken: Array<{
    name: string;
    taken: boolean;
    timeTaken?: string;
  }>;
  createdAt?: string;
}

export interface PhysicalMentalWellnessReport {
  id?: string;
  userId: string;
  date: string;
  exercise: boolean;
  stepsWalking: number;
  caloriesBurned: number;
  sleepDuration: number; // in hours
  recommendations: string[];
  createdAt?: string;
}

// Cognitive Testing Agent
export interface CognitiveTestReport {
  id?: string;
  userId: string;
  date: string;
  TICS_score: {
    total: number;
    orientation: number;
    registration: number;
    attention: number;
    recall: number;
    language: number;
  };
  recommendations: {
    cognitiveStatus: 'normal' | 'mild_impairment' | 'moderate_impairment' | 'severe_impairment';
    suggestions: string[];
  };
  createdAt?: string;
}

// Service Concierge Agent
export interface RideshareTask {
  id?: string;
  userId: string;
  company: string;
  location: string;
  timeBooked: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  createdAt?: string;
}

export interface DeliveryTask {
  id?: string;
  userId: string;
  item: string;
  timeBooked: string;
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled';
  createdAt?: string;
}

// User types
export interface User {
  id: string;
  email: string;
  name: string;
  role: 'senior' | 'family_member' | 'doctor';
  createdAt: string;
}

// Database response types
export interface DatabaseResponse<T> {
  data: T | null;
  error: string | null;
}
