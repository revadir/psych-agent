import React, { useState, useRef, useCallback } from 'react';

interface NewNoteProps {
  onCancel: () => void;
  onNoteCreated: (note: any) => void;
}

const NewNote: React.FC<NewNoteProps> = ({ onCancel, onNoteCreated }) => {
  const [patientName, setPatientName] = useState('');
  const [noteTemplate, setNoteTemplate] = useState('psychotherapy');
  const [selectedMicrophone, setSelectedMicrophone] = useState('default');
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const noteTemplates = [
    { value: 'psychotherapy', label: 'Psychotherapy Note' },
    { value: 'progress', label: 'Psych Progress Note' },
    { value: 'consult', label: 'Consult Note' },
    { value: 'meeting', label: 'Meeting Note' },
    { value: 'general_progress', label: 'Progress Note' }
  ];

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        } 
      });
      
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      chunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        setAudioBlob(blob);
        stream.getTracks().forEach(track => track.stop());
        await processRecording(blob);
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
    }
  }, []);

  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }, [isRecording]);

  const processRecording = async (blob: Blob) => {
    setIsProcessing(true);
    
    try {
      // Transcribe audio
      const formData = new FormData();
      formData.append('file', blob, 'recording.webm');
      
      const transcribeResponse = await fetch('/api/asr/transcribe-file', {
        method: 'POST',
        body: formData,
      });
      
      const transcribeResult = await transcribeResponse.json();
      
      if (!transcribeResult.success) {
        throw new Error(transcribeResult.error);
      }

      // Generate clinical note
      const noteResponse = await fetch('/api/asr/generate-note', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcript: transcribeResult.transcript,
          patient_name: patientName,
          note_template: noteTemplate
        }),
      });
      
      const noteResult = await noteResponse.json();
      
      if (noteResult.success) {
        // Create new note entry
        const newNote = {
          id: Date.now().toString(),
          patientId: `PT-${Date.now().toString().slice(-3)}`,
          patientName: patientName,
          date: new Date().toLocaleString(),
          duration: '~5 min', // Estimate based on recording
          content: {
            chiefComplaint: noteResult.note.chief_complaint,
            historyOfPresentIllness: noteResult.note.history_present_illness,
            reviewOfSystems: noteResult.note.review_systems,
            assessmentAndPlan: noteResult.note.assessment_plan,
            followUpDisposition: noteResult.note.followup_disposition
          }
        };
        
        onNoteCreated(newNote);
      } else {
        throw new Error(noteResult.error);
      }
    } catch (error) {
      console.error('Processing error:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Take a New Note</h1>
          <button
            onClick={onCancel}
            className="flex items-center space-x-2 px-4 py-2 text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-100"
          >
            <span>🗑️</span>
            <span>Cancel</span>
          </button>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start space-x-2">
            <span className="text-blue-500 text-lg">ℹ️</span>
            <div>
              <h3 className="font-medium text-blue-900 mb-1">Important Notice</h3>
              <p className="text-blue-800 text-sm">
                Please ensure you have obtained proper patient consent before recording any clinical session. 
                All recordings are processed securely and in compliance with HIPAA regulations.
              </p>
            </div>
          </div>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
          {/* Patient Name */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Patient Name *
            </label>
            <input
              type="text"
              value={patientName}
              onChange={(e) => setPatientName(e.target.value)}
              placeholder="Enter patient name"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              required
            />
          </div>

          {/* Note Template */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Note Template
            </label>
            <select
              value={noteTemplate}
              onChange={(e) => setNoteTemplate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              {noteTemplates.map((template) => (
                <option key={template.value} value={template.value}>
                  {template.label}
                </option>
              ))}
            </select>
          </div>

          {/* Microphone Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Microphone
            </label>
            <select
              value={selectedMicrophone}
              onChange={(e) => setSelectedMicrophone(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="default">Default Microphone</option>
              <option value="external">External Microphone</option>
            </select>
          </div>

          {/* Recording Controls */}
          <div className="text-center py-8">
            {!isRecording && !isProcessing && (
              <button
                onClick={startRecording}
                disabled={!patientName.trim()}
                className="flex flex-col items-center space-y-3 mx-auto p-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-full transition-colors"
              >
                <div className="text-4xl">🎤</div>
                <span className="font-medium">Start Recording</span>
              </button>
            )}

            {isRecording && (
              <button
                onClick={stopRecording}
                className="flex flex-col items-center space-y-3 mx-auto p-6 bg-red-600 hover:bg-red-700 text-white rounded-full transition-colors animate-pulse"
              >
                <div className="text-4xl">⏹️</div>
                <span className="font-medium">Stop Recording</span>
              </button>
            )}

            {isProcessing && (
              <div className="flex flex-col items-center space-y-4">
                <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
                <div className="text-center">
                  <h3 className="text-lg font-medium text-gray-900 mb-2">
                    Generating notes...
                  </h3>
                  <p className="text-gray-600">
                    Please check back in the scribe page in a couple of minutes
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewNote;
