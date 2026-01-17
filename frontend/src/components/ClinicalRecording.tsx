import { useState, useRef, useEffect } from 'react'
import { AudioRecorder } from './AudioRecorder'
import { ClinicalReportView } from './ClinicalReportView'

interface RecordingState {
  isRecording: boolean
  isPaused: boolean
  duration: number
  transcript: string
}

interface ClinicalReport {
  session_summary: string;
  diagnostic_assessment: string;
  recommendations: string;
  transcript_length: number;
  key_symptoms: string[];
  risk_factors: string[];
}

export default function ClinicalRecording() {
  const [recording, setRecording] = useState<RecordingState>({
    isRecording: false,
    isPaused: false,
    duration: 0,
    transcript: ''
  })
  
  const [generatedReport, setGeneratedReport] = useState<ClinicalReport | null>(null)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)

  const handleTranscript = (newTranscript: string) => {
    setRecording(prev => ({
      ...prev,
      transcript: prev.transcript + newTranscript + " "
    }))
  }

  const handleError = (error: string) => {
    console.error('ASR Error:', error)
    alert(`Transcription error: ${error}`)
  }

  const startRecording = async () => {
    setRecording(prev => ({ ...prev, isRecording: true, duration: 0, transcript: '' }))
  }

  const stopRecording = () => {
    setRecording(prev => ({ ...prev, isRecording: false, isPaused: false }))
  }

  const pauseRecording = () => {
    setRecording(prev => ({ ...prev, isPaused: !prev.isPaused }))
  }

  const generateReport = async () => {
    if (!recording.transcript.trim()) {
      alert('No transcript available to generate report')
      return
    }

    setIsGeneratingReport(true)
    
    try {
      const response = await fetch('/api/generate-clinical-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          transcript: recording.transcript
        })
      })

      const result = await response.json()
      
      if (result.success) {
        setGeneratedReport(result.report)
      } else {
        alert(`Error generating report: ${result.error}`)
      }
    } catch (error) {
      console.error('Report generation error:', error)
      alert('Failed to generate clinical report')
    } finally {
      setIsGeneratingReport(false)
    }
  }

  return (
    <div className="flex-1 flex flex-col bg-gray-50">
      {/* Recording Controls */}
      <div className="bg-white border-b border-gray-200 p-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Clinical Session Recording</h2>
          
          <AudioRecorder 
            onTranscript={handleTranscript}
            onError={handleError}
          />
        </div>
      </div>

      {/* Transcript Area */}
      <div className="flex-1 p-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-full">
            <div className="p-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Live Transcript</h3>
              <p className="text-sm text-gray-600">Real-time transcription of the clinical session</p>
            </div>
            
            <div className="p-4 h-96 overflow-y-auto">
              {recording.transcript ? (
                <div className="prose prose-gray max-w-none">
                  <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                    {recording.transcript}
                  </p>
                </div>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <div className="text-center">
                    <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                    </svg>
                    <p>Record or upload audio to see transcription</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Generate Report Button */}
      {recording.transcript && (
        <div className="bg-white border-t border-gray-200 p-6">
          <div className="max-w-4xl mx-auto">
            <button
              onClick={generateReport}
              disabled={isGeneratingReport}
              className="flex items-center px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium disabled:opacity-50"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {isGeneratingReport ? 'Generating Report...' : 'Generate Clinical Report'}
            </button>
          </div>
        </div>
      )}
      
      {/* Clinical Report Modal */}
      {generatedReport && (
        <ClinicalReportView 
          report={generatedReport}
          onClose={() => setGeneratedReport(null)}
        />
      )}
    </div>
  )
}
