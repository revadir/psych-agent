import React, { useState, useEffect } from 'react';
import NewNote from './NewNote';

interface ScribeSession {
  id: string;
  patientId: string;
  patientName: string;
  date: string;
  duration: string;
  content: {
    chiefComplaint: string;
    historyOfPresentIllness: string;
    reviewOfSystems: string;
    assessmentAndPlan: string;
    followUpDisposition: string;
  };
}

const ScribePage: React.FC = () => {
  const [selectedSession, setSelectedSession] = useState<ScribeSession | null>(null);
  const [isHistoryCollapsed, setIsHistoryCollapsed] = useState(false);
  const [noteType, setNoteType] = useState('initial');
  const [feedback, setFeedback] = useState('');
  const [showNewNote, setShowNewNote] = useState(false);
  const [scribeSessions, setScribeSessions] = useState<ScribeSession[]>([]);
  const [loading, setLoading] = useState(true);

  // Load sessions from database on component mount
  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      const response = await fetch('/api/asr/scribe-sessions', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      
      console.log('🔍 API response:', data);
      if (data.success) {
        console.log('🔍 Sessions from API:', data.sessions);
        data.sessions.forEach((session, index) => {
          console.log(`🔍 Session ${index}: patient_name='${session.patient_name}'`);
        });
        setScribeSessions(data.sessions);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewNote = () => {
    setShowNewNote(true);
  };

  const handleNoteCreated = async (newNote: ScribeSession) => {
    console.log('ScribePage received new note:', newNote);
    console.log('Patient name in received note:', newNote.patientName);
    console.log('Patient name type:', typeof newNote.patientName);
    console.log('Patient name length:', newNote.patientName?.length);
    
    // Ensure patient name is not empty
    if (!newNote.patientName || newNote.patientName.trim() === '') {
      console.error('Patient name is empty or undefined!');
      newNote.patientName = 'Unnamed Patient';
    }
    
    // Save to database
    try {
      const requestData = {
        patient_name: newNote.patientName,
        patient_id: newNote.patientId,
        note_template: 'psychotherapy', // Default template
        duration: newNote.duration,
        content: {
          chief_complaint: newNote.content.chiefComplaint,
          history_present_illness: newNote.content.historyOfPresentIllness,
          review_systems: newNote.content.reviewOfSystems,
          assessment_plan: newNote.content.assessmentAndPlan,
          followup_disposition: newNote.content.followUpDisposition
        }
      };
      
      console.log('🔍 Sending request to database:', requestData);
      console.log('🔍 Patient name in request:', requestData.patient_name);
      
      const response = await fetch('/api/asr/scribe-sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(requestData)
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Reload sessions from database to get the saved version
        await loadSessions();
        // Select the newly created session
        const savedSession = data.session;
        setSelectedSession(savedSession);
      }
    } catch (error) {
      console.error('Failed to save session:', error);
      // Fallback to local state if database save fails
      setScribeSessions([newNote, ...scribeSessions]);
      setSelectedSession(newNote);
    }
    
    setShowNewNote(false);
  };

  const handleDeleteSession = async (sessionId: string, event: React.MouseEvent) => {
    event.stopPropagation(); // Prevent session selection when clicking delete
    
    if (!confirm('Are you sure you want to delete this session?')) {
      return;
    }
    
    try {
      const response = await fetch(`/api/asr/scribe-sessions/${sessionId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        // Remove from local state
        setScribeSessions(scribeSessions.filter(s => s.id !== sessionId));
        // Clear selection if deleted session was selected
        if (selectedSession?.id === sessionId) {
          setSelectedSession(null);
        }
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    }
  };

  const handleSendSummary = () => {
    console.log('Sending patient visit summary...');
  };

  const handleFeedbackSubmit = () => {
    console.log('Feedback submitted:', feedback);
    setFeedback('');
  };

  if (showNewNote) {
    return (
      <NewNote
        onCancel={() => setShowNewNote(false)}
        onNoteCreated={handleNoteCreated}
      />
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Panel - History */}
      <div className={`bg-white border-r border-gray-200 transition-all duration-300 ${
        isHistoryCollapsed ? 'w-12' : 'w-80'
      }`}>
        <div className="p-4">
          {/* Collapse Button */}
          <button
            onClick={() => setIsHistoryCollapsed(!isHistoryCollapsed)}
            className="mb-4 p-2 text-gray-400 hover:text-gray-600"
          >
            {isHistoryCollapsed ? '→' : '←'}
          </button>

          {!isHistoryCollapsed && (
            <>
              {/* New Note Button */}
              <button
                onClick={handleNewNote}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-3 rounded-lg font-medium mb-6 flex items-center justify-center space-x-2"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
                </svg>
                <span>🤖</span>
                <span>Take a new note</span>
              </button>

              {/* History List */}
              <div className="space-y-2">
                <h3 className="text-gray-600 text-sm font-medium mb-3">Recent Sessions</h3>
                {scribeSessions.length === 0 ? (
                  <div className="text-center text-gray-500 py-8">
                    {loading ? (
                      <div>
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                        <p className="text-sm">Loading sessions...</p>
                      </div>
                    ) : (
                      <div>
                        <div className="text-4xl mb-2">📝</div>
                        <p className="text-sm">No sessions yet</p>
                        <p className="text-xs">Create your first note above</p>
                      </div>
                    )}
                  </div>
                ) : (
                  scribeSessions.map((session) => (
                    <div
                      key={session.id}
                      onClick={() => setSelectedSession(session)}
                      className={`p-3 rounded-lg cursor-pointer transition-colors relative group ${
                        selectedSession?.id === session.id
                          ? 'bg-blue-100 border border-blue-300'
                          : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
                      }`}
                    >
                      <div className="font-medium text-gray-900">
                        {session.patientName || 'Unnamed Patient'}
                      </div>
                      <div className="text-sm text-gray-600">ID: {session.patientId}</div>
                      <div className="text-sm text-gray-600">{session.date}</div>
                      <div className="text-sm text-gray-600">{session.duration}</div>
                      
                      {/* Delete button */}
                      <button
                        onClick={(e) => handleDeleteSession(session.id, e)}
                        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 bg-red-500 hover:bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs transition-opacity"
                        title="Delete session"
                      >
                        ×
                      </button>
                    </div>
                  ))
                )}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex">
        <div className="flex-1 p-6 overflow-y-auto">
          {selectedSession ? (
            <div>
              {/* Patient Header */}
              <div className="mb-6">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {selectedSession.patientName || 'Unnamed Patient'}
                </h1>
                <div className="flex space-x-6 text-gray-600">
                  <span>ID: {selectedSession.patientId}</span>
                  <span>{selectedSession.date}</span>
                  <span>Duration: {selectedSession.duration}</span>
                </div>
              </div>

              {/* Content Sections */}
              <div className="space-y-6">
                <ContentSection
                  title="Chief Complaint"
                  content={selectedSession.content.chiefComplaint}
                />
                <ContentSection
                  title="History of Present Illness"
                  content={selectedSession.content.historyOfPresentIllness}
                />
                <ContentSection
                  title="Review of Systems"
                  content={selectedSession.content.reviewOfSystems}
                />
                <ContentSection
                  title="Assessment and Plan"
                  content={selectedSession.content.assessmentAndPlan}
                />
                <ContentSection
                  title="Follow-up/Disposition"
                  content={selectedSession.content.followUpDisposition}
                />
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-gray-500">
                <div className="text-6xl mb-4">📝</div>
                <h2 className="text-xl font-medium mb-2 text-gray-900">Select a session to view details</h2>
                <p>Choose a scribe session from the left panel or create a new note</p>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel - Actions */}
        <div className="w-80 bg-white border-l border-gray-200 p-6">
          <h3 className="text-gray-900 font-medium mb-4">Actions</h3>
          
          <div className="space-y-4">
            {/* Note Type Dropdown */}
            <div>
              <label className="block text-gray-700 text-sm mb-2">Note Type</label>
              <select
                value={noteType}
                onChange={(e) => setNoteType(e.target.value)}
                className="w-full bg-white border border-gray-300 text-gray-900 rounded-lg p-3 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="initial">Initial Visit</option>
                <option value="follow-up">Follow-up</option>
                <option value="consultation">Consultation</option>
                <option value="emergency">Emergency</option>
              </select>
            </div>

            {/* Send Summary Button */}
            <button
              onClick={handleSendSummary}
              disabled={!selectedSession}
              className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white px-4 py-3 rounded-lg font-medium"
            >
              Send Patient Visit Summary
            </button>

            {/* Feedback Section */}
            {selectedSession && (
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-gray-900 font-medium mb-3">Suggest Changes</h3>
                <textarea
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  placeholder="Enter your feedback or suggestions for improvements..."
                  className="w-full bg-gray-50 border border-gray-300 text-gray-900 rounded-lg p-3 h-24 resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
                />
                <button
                  onClick={handleFeedbackSubmit}
                  className="mt-2 w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm"
                >
                  Submit Feedback
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

interface ContentSectionProps {
  title: string;
  content: string;
}

const ContentSection: React.FC<ContentSectionProps> = ({ title, content }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4">
      <h3 className="text-blue-600 font-medium mb-3">{title}</h3>
      <p className="text-gray-800 leading-relaxed">{content}</p>
    </div>
  );
};

export default ScribePage;
