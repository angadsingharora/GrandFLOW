'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { 
  Heart, 
  Activity, 
  Pill, 
  Brain, 
  Car, 
  ShoppingBag, 
  Phone, 
  PhoneOff,
  ChevronDown,
  ChevronUp,
  Calendar,
  Clock,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import VoiceCallInterface from './VoiceCallInterface';
import { supabase } from '@/lib/supabase';
import { 
  DietReport, 
  MedicalAdherence, 
  PhysicalMentalWellnessReport, 
  CognitiveTestReport, 
  RideshareTask, 
  DeliveryTask 
} from '@/types';

interface DashboardProps {
  userId: string;
  userRole: 'senior' | 'family_member' | 'doctor';
}

export default function Dashboard({ userId, userRole }: DashboardProps) {
  const [showVoiceInterface, setShowVoiceInterface] = useState(false);
  const [expandedSections, setExpandedSections] = useState<{
    health: boolean;
    concierge: boolean;
  }>({
    health: false,
    concierge: false,
  });

  // Health data state
  const [dietReports, setDietReports] = useState<DietReport[]>([]);
  const [medicalAdherence, setMedicalAdherence] = useState<MedicalAdherence[]>([]);
  const [wellnessReports, setWellnessReports] = useState<PhysicalMentalWellnessReport[]>([]);
  const [cognitiveReports, setCognitiveReports] = useState<CognitiveTestReport[]>([]);

  // Concierge data state
  const [rideshareTasks, setRideshareTasks] = useState<RideshareTask[]>([]);
  const [deliveryTasks, setDeliveryTasks] = useState<DeliveryTask[]>([]);

  // Heart rate data for the graph
  const [heartRateData, setHeartRateData] = useState([
    { time: '00:00', rate: 72 },
    { time: '04:00', rate: 68 },
    { time: '08:00', rate: 75 },
    { time: '12:00', rate: 78 },
    { time: '16:00', rate: 80 },
    { time: '20:00', rate: 74 },
  ]);

  useEffect(() => {
    loadDashboardData();
  }, [userId]);

  const loadDashboardData = async () => {
    try {
      // Load health data
      const { data: dietData } = await supabase
        .from('diet_reports')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false })
        .limit(7);

      const { data: medicalData } = await supabase
        .from('medical_adherence')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false })
        .limit(7);

      const { data: wellnessData } = await supabase
        .from('physical_mental_wellness_reports')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false })
        .limit(7);

      const { data: cognitiveData } = await supabase
        .from('cognitive_test_reports')
        .select('*')
        .eq('user_id', userId)
        .order('date', { ascending: false })
        .limit(7);

      // Load concierge data
      const { data: rideshareData } = await supabase
        .from('rideshare_tasks')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(10);

      const { data: deliveryData } = await supabase
        .from('delivery_tasks')
        .select('*')
        .eq('user_id', userId)
        .order('created_at', { ascending: false })
        .limit(10);

      setDietReports(dietData || []);
      setMedicalAdherence(medicalData || []);
      setWellnessReports(wellnessData || []);
      setCognitiveReports(cognitiveData || []);
      setRideshareTasks(rideshareData || []);
      setDeliveryTasks(deliveryData || []);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    }
  };

  const toggleSection = (section: 'health' | 'concierge') => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const startCall = () => {
    setShowVoiceInterface(true);
  };

  const endCall = () => {
    setShowVoiceInterface(false);
    loadDashboardData(); // Refresh data after call
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'cancelled':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'pending':
        return 'text-yellow-600';
      case 'cancelled':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold text-gray-900">
            GrandFLOW Dashboard
          </h1>
          <p className="text-lg text-gray-600">
            Your comprehensive health and wellness companion
          </p>
          
          {/* Voice Call Button */}
          <div className="flex justify-center">
            <Button
              onClick={startCall}
              size="lg"
              className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-full shadow-lg"
            >
              <Phone className="mr-2 h-5 w-5" />
              Start Voice Call
            </Button>
          </div>
        </div>

        {/* Main Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Health Report Section */}
          <Card variant="health" className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-health rounded-full">
                    <Heart className="h-6 w-6 text-health-foreground" />
                  </div>
                  <div>
                    <CardTitle className="text-health">Health Report</CardTitle>
                    <CardDescription>
                      Monitor your health metrics and wellness
                    </CardDescription>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => toggleSection('health')}
                >
                  {expandedSections.health ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            
            {expandedSections.health && (
              <CardContent className="space-y-6">
                {/* Heart Rate Graph */}
                <div className="bg-white rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-4 flex items-center">
                    <Activity className="mr-2 h-5 w-5 text-red-500" />
                    Heart Rate (BPM)
                  </h3>
                  <div className="h-32 flex items-end space-x-2">
                    {heartRateData.map((point, index) => (
                      <div key={index} className="flex flex-col items-center space-y-2">
                        <div
                          className="bg-red-500 rounded-t w-8"
                          style={{ height: `${(point.rate / 100) * 100}px` }}
                        />
                        <span className="text-xs text-gray-600">{point.time}</span>
                        <span className="text-xs font-medium">{point.rate}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Diet Report */}
                <div className="bg-white rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <Activity className="mr-2 h-5 w-5 text-green-500" />
                    Latest Diet Report
                  </h3>
                  {dietReports.length > 0 ? (
                    <div className="space-y-2">
                      <p><span className="font-medium">Calories:</span> {dietReports[0].calories}</p>
                      <p><span className="font-medium">Meals:</span> {dietReports[0].meals}</p>
                      <p><span className="font-medium">Date:</span> {dietReports[0].date}</p>
                    </div>
                  ) : (
                    <p className="text-gray-500">No diet data available</p>
                  )}
                </div>

                {/* Medication Adherence */}
                <div className="bg-white rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <Pill className="mr-2 h-5 w-5 text-blue-500" />
                    Medication Adherence
                  </h3>
                  {medicalAdherence.length > 0 ? (
                    <div className="space-y-2">
                      <p><span className="font-medium">Prescribed:</span> {medicalAdherence[0].medicinesPrescribed.length} medications</p>
                      <p><span className="font-medium">Taken:</span> {medicalAdherence[0].medicinesTaken.filter(m => m.taken).length}/{medicalAdherence[0].medicinesTaken.length}</p>
                      <p><span className="font-medium">Date:</span> {medicalAdherence[0].date}</p>
                    </div>
                  ) : (
                    <p className="text-gray-500">No medication data available</p>
                  )}
                </div>

                {/* Cognitive Testing */}
                <div className="bg-white rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <Brain className="mr-2 h-5 w-5 text-purple-500" />
                    Cognitive Assessment
                  </h3>
                  {cognitiveReports.length > 0 ? (
                    <div className="space-y-2">
                      <p><span className="font-medium">TICS Score:</span> {cognitiveReports[0].TICS_score.total}/41</p>
                      <p><span className="font-medium">Status:</span> {cognitiveReports[0].recommendations.cognitiveStatus}</p>
                      <p><span className="font-medium">Date:</span> {cognitiveReports[0].date}</p>
                    </div>
                  ) : (
                    <p className="text-gray-500">No cognitive data available</p>
                  )}
                </div>
              </CardContent>
            )}
          </Card>

          {/* Concierge Services Section */}
          <Card variant="concierge" className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-3 bg-concierge rounded-full">
                    <ShoppingBag className="h-6 w-6 text-concierge-foreground" />
                  </div>
                  <div>
                    <CardTitle className="text-concierge">Concierge Services</CardTitle>
                    <CardDescription>
                      Manage your daily tasks and appointments
                    </CardDescription>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => toggleSection('concierge')}
                >
                  {expandedSections.concierge ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </CardHeader>
            
            {expandedSections.concierge && (
              <CardContent className="space-y-6">
                {/* Rideshare Tasks */}
                <div className="bg-white rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <Car className="mr-2 h-5 w-5 text-blue-500" />
                    Recent Rideshare Bookings
                  </h3>
                  {rideshareTasks.length > 0 ? (
                    <div className="space-y-3">
                      {rideshareTasks.slice(0, 3).map((task) => (
                        <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{task.company}</p>
                            <p className="text-sm text-gray-600">{task.location}</p>
                            <p className="text-xs text-gray-500">{new Date(task.timeBooked).toLocaleDateString()}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(task.status)}
                            <span className={`text-sm ${getStatusColor(task.status)}`}>
                              {task.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No rideshare bookings</p>
                  )}
                </div>

                {/* Delivery Tasks */}
                <div className="bg-white rounded-lg p-4">
                  <h3 className="text-lg font-semibold mb-3 flex items-center">
                    <ShoppingBag className="mr-2 h-5 w-5 text-green-500" />
                    Recent Deliveries
                  </h3>
                  {deliveryTasks.length > 0 ? (
                    <div className="space-y-3">
                      {deliveryTasks.slice(0, 3).map((task) => (
                        <div key={task.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium">{task.item}</p>
                            <p className="text-xs text-gray-500">{new Date(task.timeBooked).toLocaleDateString()}</p>
                          </div>
                          <div className="flex items-center space-x-2">
                            {getStatusIcon(task.status)}
                            <span className={`text-sm ${getStatusColor(task.status)}`}>
                              {task.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500">No delivery requests</p>
                  )}
                </div>
              </CardContent>
            )}
          </Card>
        </div>

        {/* Quick Actions */}
        <Card className="bg-white">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks you can perform right now
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button variant="health" className="h-20 flex flex-col space-y-2">
                <Heart className="h-6 w-6" />
                <span>Health Check</span>
              </Button>
              <Button variant="concierge" className="h-20 flex flex-col space-y-2">
                <Car className="h-6 w-6" />
                <span>Book Ride</span>
              </Button>
              <Button variant="concierge" className="h-20 flex flex-col space-y-2">
                <ShoppingBag className="h-6 w-6" />
                <span>Order Delivery</span>
              </Button>
              <Button variant="health" className="h-20 flex flex-col space-y-2">
                <Brain className="h-6 w-6" />
                <span>Cognitive Test</span>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Voice Call Interface Modal */}
      {showVoiceInterface && (
        <VoiceCallInterface
          userId={userId}
          onCallEnd={endCall}
        />
      )}
    </div>
  );
}
