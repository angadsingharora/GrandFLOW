'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Phone, PhoneOff, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { VoiceCallManager } from '@/lib/voice';
import { 
  HealthMonitoringAgent, 
  CognitiveTestingAgent, 
  ServiceConciergeAgent 
} from '@/lib/agents';

interface VoiceCallInterfaceProps {
  userId: string;
  onCallEnd: () => void;
}

export default function VoiceCallInterface({ userId, onCallEnd }: VoiceCallInterfaceProps) {
  const [isCallActive, setIsCallActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [aiResponse, setAiResponse] = useState('');
  const [callLog, setCallLog] = useState<Array<{type: 'user' | 'ai', message: string, timestamp: Date}>>([]);
  
  const voiceManagerRef = useRef<VoiceCallManager | null>(null);
  const healthAgentRef = useRef<HealthMonitoringAgent | null>(null);
  const cognitiveAgentRef = useRef<CognitiveTestingAgent | null>(null);
  const conciergeAgentRef = useRef<ServiceConciergeAgent | null>(null);

  useEffect(() => {
    // Initialize agents
    healthAgentRef.current = new HealthMonitoringAgent();
    cognitiveAgentRef.current = new CognitiveTestingAgent();
    conciergeAgentRef.current = new ServiceConciergeAgent();
    voiceManagerRef.current = new VoiceCallManager();

    return () => {
      // Cleanup
      if (voiceManagerRef.current?.isCallInProgress()) {
        voiceManagerRef.current.endCall();
      }
    };
  }, []);

  const startCall = async () => {
    try {
      setIsCallActive(true);
      await voiceManagerRef.current?.startCall();
      
      // Add initial greeting to call log
      setCallLog(prev => [...prev, {
        type: 'ai',
        message: "Hello! I'm here to help you with your health monitoring and daily tasks. How are you feeling today?",
        timestamp: new Date()
      }]);
    } catch (error) {
      console.error('Error starting call:', error);
      setIsCallActive(false);
    }
  };

  const endCall = async () => {
    try {
      await voiceManagerRef.current?.endCall();
      setIsCallActive(false);
      setIsRecording(false);
      onCallEnd();
    } catch (error) {
      console.error('Error ending call:', error);
    }
  };

  const startRecording = async () => {
    if (!isCallActive) return;
    
    setIsRecording(true);
    // Recording is handled by the voice manager
  };

  const stopRecording = async () => {
    if (!isCallActive || !isRecording) return;
    
    setIsRecording(false);
    
    try {
      // Get user speech transcription
      const userSpeech = await voiceManagerRef.current?.processUserSpeech();
      if (userSpeech) {
        setTranscription(userSpeech);
        
        // Add user message to call log
        setCallLog(prev => [...prev, {
          type: 'user',
          message: userSpeech,
          timestamp: new Date()
        }]);

        // Process with appropriate agent
        await processUserInput(userSpeech);
      }
    } catch (error) {
      console.error('Error processing speech:', error);
    }
  };

  const processUserInput = async (input: string) => {
    try {
      let response = '';
      
      // Determine which agent to use based on user input
      const lowerInput = input.toLowerCase();
      
      if (lowerInput.includes('diet') || lowerInput.includes('food') || lowerInput.includes('meal')) {
        const dietReport = await healthAgentRef.current?.processDietReport(userId, input);
        response = `I've recorded your diet information. You consumed ${dietReport?.calories} calories across ${dietReport?.meals} meals today.`;
      } else if (lowerInput.includes('medication') || lowerInput.includes('medicine') || lowerInput.includes('pill')) {
        const medicalAdherence = await healthAgentRef.current?.processMedicalAdherence(userId, input);
        response = `I've updated your medication tracking. You've taken ${medicalAdherence?.medicinesTaken.filter(m => m.taken).length} out of ${medicalAdherence?.medicinesTaken.length} prescribed medications.`;
      } else if (lowerInput.includes('exercise') || lowerInput.includes('walk') || lowerInput.includes('sleep')) {
        const wellnessReport = await healthAgentRef.current?.processPhysicalMentalWellness(userId, input);
        response = `I've recorded your wellness activities. You walked ${wellnessReport?.stepsWalking} steps and slept ${wellnessReport?.sleepDuration} hours.`;
      } else if (lowerInput.includes('cognitive') || lowerInput.includes('memory') || lowerInput.includes('test')) {
        const cognitiveReport = await cognitiveAgentRef.current?.administerTICSTest(userId, input);
        response = `I've completed your cognitive assessment. Your TICS score is ${cognitiveReport?.TICS_score.total}/41, indicating ${cognitiveReport?.recommendations.cognitiveStatus} cognitive function.`;
      } else if (lowerInput.includes('ride') || lowerInput.includes('uber') || lowerInput.includes('lyft')) {
        const rideshareTask = await conciergeAgentRef.current?.processRideshareRequest(userId, input);
        response = `I've booked your ${rideshareTask?.company} ride to ${rideshareTask?.location}. The booking is confirmed for ${new Date(rideshareTask?.timeBooked || '').toLocaleString()}.`;
      } else if (lowerInput.includes('delivery') || lowerInput.includes('order') || lowerInput.includes('groceries')) {
        const deliveryTask = await conciergeAgentRef.current?.processDeliveryRequest(userId, input);
        response = `I've placed your order for ${deliveryTask?.item}. It will be delivered by ${new Date(deliveryTask?.timeBooked || '').toLocaleString()}.`;
      } else {
        response = "I understand. Is there anything specific about your health or daily tasks I can help you with today?";
      }

      setAiResponse(response);
      
      // Add AI response to call log
      setCallLog(prev => [...prev, {
        type: 'ai',
        message: response,
        timestamp: new Date()
      }]);

      // Speak the response
      await voiceManagerRef.current?.speakToUser(response);
      
    } catch (error) {
      console.error('Error processing user input:', error);
      const errorResponse = "I'm sorry, I encountered an error processing your request. Could you please try again?";
      setAiResponse(errorResponse);
      await voiceManagerRef.current?.speakToUser(errorResponse);
    }
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
    // Implement mute functionality
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-2xl mx-4">
        <CardHeader>
          <CardTitle className="text-center">
            {isCallActive ? 'Voice Call Active' : 'Start Voice Call'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Call Status */}
          <div className="text-center">
            <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
              isCallActive ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                isCallActive ? 'bg-green-500 animate-pulse' : 'bg-gray-400'
              }`} />
              {isCallActive ? 'Call Connected' : 'Call Disconnected'}
            </div>
          </div>

          {/* Call Controls */}
          <div className="flex justify-center space-x-4">
            {!isCallActive ? (
              <Button
                onClick={startCall}
                size="lg"
                className="bg-green-600 hover:bg-green-700 text-white px-8 py-3 rounded-full"
              >
                <Phone className="mr-2 h-5 w-5" />
                Start Call
              </Button>
            ) : (
              <>
                <Button
                  onClick={isRecording ? stopRecording : startRecording}
                  size="lg"
                  className={`px-8 py-3 rounded-full ${
                    isRecording 
                      ? 'bg-red-600 hover:bg-red-700 text-white' 
                      : 'bg-blue-600 hover:bg-blue-700 text-white'
                  }`}
                >
                  {isRecording ? (
                    <>
                      <MicOff className="mr-2 h-5 w-5" />
                      Stop Recording
                    </>
                  ) : (
                    <>
                      <Mic className="mr-2 h-5 w-5" />
                      Start Recording
                    </>
                  )}
                </Button>
                
                <Button
                  onClick={toggleMute}
                  variant="outline"
                  size="lg"
                  className="px-6 py-3 rounded-full"
                >
                  {isMuted ? (
                    <>
                      <VolumeX className="mr-2 h-5 w-5" />
                      Unmute
                    </>
                  ) : (
                    <>
                      <Volume2 className="mr-2 h-5 w-5" />
                      Mute
                    </>
                  )}
                </Button>
                
                <Button
                  onClick={endCall}
                  size="lg"
                  className="bg-red-600 hover:bg-red-700 text-white px-8 py-3 rounded-full"
                >
                  <PhoneOff className="mr-2 h-5 w-5" />
                  End Call
                </Button>
              </>
            )}
          </div>

          {/* Transcription Display */}
          {transcription && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-700 mb-2">Your Message:</h3>
              <p className="text-gray-800">{transcription}</p>
            </div>
          )}

          {/* AI Response Display */}
          {aiResponse && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-700 mb-2">AI Response:</h3>
              <p className="text-blue-800">{aiResponse}</p>
            </div>
          )}

          {/* Call Log */}
          {callLog.length > 0 && (
            <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
              <h3 className="font-semibold text-gray-700 mb-3">Call Log:</h3>
              <div className="space-y-2">
                {callLog.map((entry, index) => (
                  <div key={index} className={`p-2 rounded ${
                    entry.type === 'user' ? 'bg-blue-100' : 'bg-green-100'
                  }`}>
                    <div className="flex justify-between items-start">
                      <span className={`font-medium ${
                        entry.type === 'user' ? 'text-blue-800' : 'text-green-800'
                      }`}>
                        {entry.type === 'user' ? 'You' : 'AI Assistant'}
                      </span>
                      <span className="text-xs text-gray-500">
                        {entry.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                    <p className={`text-sm mt-1 ${
                      entry.type === 'user' ? 'text-blue-700' : 'text-green-700'
                    }`}>
                      {entry.message}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Instructions */}
          <div className="text-center text-sm text-gray-600">
            <p>Speak naturally about your health, medications, daily activities, or any tasks you need help with.</p>
            <p className="mt-1">The AI will understand and help you track your information.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
