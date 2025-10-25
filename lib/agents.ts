import { Agent, Task, Crew } from 'crewai';
import { supabase } from '../lib/supabase';
import { 
  DietReport, 
  MedicalAdherence, 
  PhysicalMentalWellnessReport, 
  CognitiveTestReport, 
  RideshareTask, 
  DeliveryTask 
} from '../types';

// Health Monitoring Agent
export class HealthMonitoringAgent {
  private agent: Agent;

  constructor() {
    this.agent = new Agent({
      role: 'Health Monitoring Specialist',
      goal: 'Monitor and track senior health metrics including diet, medication adherence, and physical wellness',
      backstory: 'You are a dedicated health monitoring specialist with expertise in geriatric care. You help seniors maintain their health by tracking their daily habits and providing personalized recommendations.',
      verbose: true,
      allow_delegation: false,
    });
  }

  async processDietReport(userId: string, conversationData: string): Promise<DietReport> {
    const task = new Task({
      description: `Analyze the following conversation data to extract diet information: ${conversationData}`,
      expectedOutput: 'A structured diet report with macronutrients, calories, meals, vitamins, and recommendations',
      agent: this.agent,
    });

    const result = await task.execute();
    
    // Parse the result and create DietReport object
    const dietReport: DietReport = {
      userId,
      date: new Date().toISOString().split('T')[0],
      macronutrients: this.extractMacronutrients(result),
      calories: this.extractCalories(result),
      meals: this.extractMeals(result),
      vitamins: this.extractVitamins(result),
      recommendations: this.extractRecommendations(result),
    };

    // Save to database
    await this.saveDietReport(dietReport);
    return dietReport;
  }

  async processMedicalAdherence(userId: string, conversationData: string): Promise<MedicalAdherence> {
    const task = new Task({
      description: `Analyze the following conversation data to extract medication adherence information: ${conversationData}`,
      expectedOutput: 'A structured medical adherence report with prescribed medicines and taken medicines',
      agent: this.agent,
    });

    const result = await task.execute();
    
    const medicalAdherence: MedicalAdherence = {
      userId,
      date: new Date().toISOString().split('T')[0],
      medicinesPrescribed: this.extractPrescribedMedicines(result),
      medicinesTaken: this.extractTakenMedicines(result),
    };

    await this.saveMedicalAdherence(medicalAdherence);
    return medicalAdherence;
  }

  async processPhysicalMentalWellness(userId: string, conversationData: string): Promise<PhysicalMentalWellnessReport> {
    const task = new Task({
      description: `Analyze the following conversation data to extract physical and mental wellness information: ${conversationData}`,
      expectedOutput: 'A structured wellness report with exercise, steps, sleep duration, and recommendations',
      agent: this.agent,
    });

    const result = await task.execute();
    
    const wellnessReport: PhysicalMentalWellnessReport = {
      userId,
      date: new Date().toISOString().split('T')[0],
      exercise: this.extractExercise(result),
      stepsWalking: this.extractSteps(result),
      caloriesBurned: this.calculateCaloriesBurned(this.extractSteps(result)),
      sleepDuration: this.extractSleepDuration(result),
      recommendations: this.extractRecommendations(result),
    };

    await this.saveWellnessReport(wellnessReport);
    return wellnessReport;
  }

  private extractMacronutrients(result: string): Array<{name: string, amount: number, unit: string}> {
    // Implement logic to extract macronutrients from conversation
    return [
      { name: 'Protein', amount: 50, unit: 'g' },
      { name: 'Carbohydrates', amount: 200, unit: 'g' },
      { name: 'Fat', amount: 30, unit: 'g' }
    ];
  }

  private extractCalories(result: string): number {
    // Implement logic to extract calories
    return 1800;
  }

  private extractMeals(result: string): number {
    // Implement logic to extract number of meals
    return 3;
  }

  private extractVitamins(result: string): Array<{name: string, amount: number, unit: string}> {
    // Implement logic to extract vitamins
    return [
      { name: 'Vitamin D', amount: 1000, unit: 'IU' },
      { name: 'Vitamin B12', amount: 2.4, unit: 'mcg' }
    ];
  }

  private extractPrescribedMedicines(result: string): Array<{name: string, dosage: string, frequency: string}> {
    // Implement logic to extract prescribed medicines
    return [
      { name: 'Metformin', dosage: '500mg', frequency: 'twice daily' },
      { name: 'Lisinopril', dosage: '10mg', frequency: 'once daily' }
    ];
  }

  private extractTakenMedicines(result: string): Array<{name: string, taken: boolean, timeTaken?: string}> {
    // Implement logic to extract taken medicines
    return [
      { name: 'Metformin', taken: true, timeTaken: '08:00' },
      { name: 'Lisinopril', taken: true, timeTaken: '09:00' }
    ];
  }

  private extractExercise(result: string): boolean {
    // Implement logic to extract exercise information
    return true;
  }

  private extractSteps(result: string): number {
    // Implement logic to extract steps
    return 5000;
  }

  private calculateCaloriesBurned(steps: number): number {
    // Simple calculation: 0.04 calories per step
    return Math.round(steps * 0.04);
  }

  private extractSleepDuration(result: string): number {
    // Implement logic to extract sleep duration
    return 7.5;
  }

  private extractRecommendations(result: string): string[] {
    // Implement logic to extract recommendations
    return [
      'Increase water intake',
      'Add more vegetables to meals',
      'Consider light exercise'
    ];
  }

  private async saveDietReport(report: DietReport): Promise<void> {
    const { error } = await supabase
      .from('diet_reports')
      .insert(report);
    
    if (error) throw error;
  }

  private async saveMedicalAdherence(report: MedicalAdherence): Promise<void> {
    const { error } = await supabase
      .from('medical_adherence')
      .insert(report);
    
    if (error) throw error;
  }

  private async saveWellnessReport(report: PhysicalMentalWellnessReport): Promise<void> {
    const { error } = await supabase
      .from('physical_mental_wellness_reports')
      .insert(report);
    
    if (error) throw error;
  }
}

// Cognitive Testing Agent
export class CognitiveTestingAgent {
  private agent: Agent;

  constructor() {
    this.agent = new Agent({
      role: 'Cognitive Assessment Specialist',
      goal: 'Administer and evaluate cognitive tests including TICS (Telephone Interview for Cognitive Status)',
      backstory: 'You are a specialized cognitive assessment expert trained in administering and interpreting cognitive tests for seniors. You help identify early signs of cognitive decline and provide appropriate recommendations.',
      verbose: true,
      allow_delegation: false,
    });
  }

  async administerTICSTest(userId: string, conversationData: string): Promise<CognitiveTestReport> {
    const task = new Task({
      description: `Administer TICS test based on the following conversation data: ${conversationData}`,
      expectedOutput: 'A structured cognitive test report with TICS scores and recommendations',
      agent: this.agent,
    });

    const result = await task.execute();
    
    const cognitiveReport: CognitiveTestReport = {
      userId,
      date: new Date().toISOString().split('T')[0],
      TICS_score: this.calculateTICSScore(result),
      recommendations: this.generateCognitiveRecommendations(result),
    };

    await this.saveCognitiveReport(cognitiveReport);
    return cognitiveReport;
  }

  private calculateTICSScore(result: string): {
    total: number;
    orientation: number;
    registration: number;
    attention: number;
    recall: number;
    language: number;
  } {
    // Implement TICS scoring logic
    return {
      total: 35,
      orientation: 8,
      registration: 3,
      attention: 5,
      recall: 3,
      language: 16
    };
  }

  private generateCognitiveRecommendations(result: string): {
    cognitiveStatus: 'normal' | 'mild_impairment' | 'moderate_impairment' | 'severe_impairment';
    suggestions: string[];
  } {
    return {
      cognitiveStatus: 'normal',
      suggestions: [
        'Continue regular mental exercises',
        'Maintain social connections',
        'Engage in memory games'
      ]
    };
  }

  private async saveCognitiveReport(report: CognitiveTestReport): Promise<void> {
    const { error } = await supabase
      .from('cognitive_test_reports')
      .insert(report);
    
    if (error) throw error;
  }
}

// Service Concierge Agent
export class ServiceConciergeAgent {
  private agent: Agent;

  constructor() {
    this.agent = new Agent({
      role: 'Personal Concierge Assistant',
      goal: 'Help seniors with daily tasks including rideshare bookings and delivery services',
      backstory: 'You are a helpful concierge assistant specializing in helping seniors with their daily needs. You coordinate rideshare services and delivery requests efficiently.',
      verbose: true,
      allow_delegation: false,
    });
  }

  async processRideshareRequest(userId: string, conversationData: string): Promise<RideshareTask> {
    const task = new Task({
      description: `Process rideshare request from the following conversation data: ${conversationData}`,
      expectedOutput: 'A structured rideshare task with company, location, and booking time',
      agent: this.agent,
    });

    const result = await task.execute();
    
    const rideshareTask: RideshareTask = {
      userId,
      company: this.extractRideshareCompany(result),
      location: this.extractLocation(result),
      timeBooked: this.extractBookingTime(result),
      status: 'pending',
    };

    await this.saveRideshareTask(rideshareTask);
    return rideshareTask;
  }

  async processDeliveryRequest(userId: string, conversationData: string): Promise<DeliveryTask> {
    const task = new Task({
      description: `Process delivery request from the following conversation data: ${conversationData}`,
      expectedOutput: 'A structured delivery task with item and booking time',
      agent: this.agent,
    });

    const result = await task.execute();
    
    const deliveryTask: DeliveryTask = {
      userId,
      item: this.extractDeliveryItem(result),
      timeBooked: this.extractBookingTime(result),
      status: 'pending',
    };

    await this.saveDeliveryTask(deliveryTask);
    return deliveryTask;
  }

  private extractRideshareCompany(result: string): string {
    // Implement logic to extract rideshare company
    return 'Uber';
  }

  private extractLocation(result: string): string {
    // Implement logic to extract location
    return '123 Main St, City, State';
  }

  private extractDeliveryItem(result: string): string {
    // Implement logic to extract delivery item
    return 'Prescription medication';
  }

  private extractBookingTime(result: string): string {
    // Implement logic to extract booking time
    return new Date().toISOString();
  }

  private async saveRideshareTask(task: RideshareTask): Promise<void> {
    const { error } = await supabase
      .from('rideshare_tasks')
      .insert(task);
    
    if (error) throw error;
  }

  private async saveDeliveryTask(task: DeliveryTask): Promise<void> {
    const { error } = await supabase
      .from('delivery_tasks')
      .insert(task);
    
    if (error) throw error;
  }
}
