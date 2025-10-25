import { OpenAI } from 'openai';

// Voice Integration Service
export class VoiceService {
  private openai: OpenAI;
  private audioContext: AudioContext | null = null;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  // Text-to-Speech using Fish Audio (simulated with OpenAI TTS)
  async textToSpeech(text: string): Promise<AudioBuffer> {
    try {
      const response = await this.openai.audio.speech.create({
        model: 'tts-1',
        voice: 'alloy',
        input: text,
      });

      const arrayBuffer = await response.arrayBuffer();
      const audioContext = new AudioContext();
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
      
      return audioBuffer;
    } catch (error) {
      console.error('Error in text-to-speech:', error);
      throw error;
    }
  }

  // Speech-to-Text using Whisper
  async speechToText(audioBlob: Blob): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.wav');
      formData.append('model', 'whisper-1');
      formData.append('language', 'en');

      const response = await this.openai.audio.transcriptions.create({
        file: audioBlob as any,
        model: 'whisper-1',
        language: 'en',
      });

      return response.text;
    } catch (error) {
      console.error('Error in speech-to-text:', error);
      throw error;
    }
  }

  // Play audio buffer
  async playAudio(audioBuffer: AudioBuffer): Promise<void> {
    if (!this.audioContext) {
      this.audioContext = new AudioContext();
    }

    const source = this.audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(this.audioContext.destination);
    source.start();
  }

  // Start recording
  async startRecording(): Promise<MediaRecorder> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      return mediaRecorder;
    } catch (error) {
      console.error('Error starting recording:', error);
      throw error;
    }
  }

  // Stop recording and get audio blob
  async stopRecording(mediaRecorder: MediaRecorder): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const chunks: BlobPart[] = [];
      
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        resolve(blob);
      };

      mediaRecorder.onerror = (error) => {
        reject(error);
      };

      mediaRecorder.stop();
    });
  }
}

// Voice Call Manager
export class VoiceCallManager {
  private voiceService: VoiceService;
  private isCallActive: boolean = false;
  private mediaRecorder: MediaRecorder | null = null;

  constructor() {
    this.voiceService = new VoiceService();
  }

  async startCall(): Promise<void> {
    if (this.isCallActive) {
      throw new Error('Call is already active');
    }

    this.isCallActive = true;
    this.mediaRecorder = await this.voiceService.startRecording();
    
    // Start recording
    this.mediaRecorder.start();
    
    // Greet the user
    await this.speakToUser("Hello! I'm here to help you with your health monitoring and daily tasks. How are you feeling today?");
  }

  async endCall(): Promise<void> {
    if (!this.isCallActive) {
      throw new Error('No active call');
    }

    this.isCallActive = false;
    
    if (this.mediaRecorder) {
      await this.voiceService.stopRecording(this.mediaRecorder);
      this.mediaRecorder = null;
    }

    await this.speakToUser("Thank you for talking with me today. Take care!");
  }

  async processUserSpeech(): Promise<string> {
    if (!this.mediaRecorder || !this.isCallActive) {
      throw new Error('No active call or recording');
    }

    const audioBlob = await this.voiceService.stopRecording(this.mediaRecorder);
    const transcription = await this.voiceService.speechToText(audioBlob);
    
    // Restart recording for continuous conversation
    this.mediaRecorder = await this.voiceService.startRecording();
    this.mediaRecorder.start();
    
    return transcription;
  }

  async speakToUser(text: string): Promise<void> {
    const audioBuffer = await this.voiceService.textToSpeech(text);
    await this.voiceService.playAudio(audioBuffer);
  }

  isCallInProgress(): boolean {
    return this.isCallActive;
  }
}
