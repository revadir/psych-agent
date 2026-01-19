import React, { useState } from 'react';
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
  const [scribeSessions, setScribeSessions] = useState<ScribeSession[]>([
    {
      id: '1',
      patientId: 'PT-001',
      patientName: 'John Doe',
      date: '2026-01-19 09:30',
      duration: '45 min',
      content: {
        chiefComplaint: 'Patient reports feeling anxious and having difficulty sleeping for the past 2 weeks.',
        historyOfPresentIllness: 'Patient describes onset of anxiety symptoms following job loss. Reports racing thoughts, restlessness, and insomnia. No previous psychiatric history.',
        reviewOfSystems: 'Denies chest pain, palpitations, or shortness of breath. Reports decreased appetite and fatigue.',
        assessmentAndPlan: 'Generalized Anxiety Disorder (F41.1). Recommend CBT therapy and consider short-term anxiolytic if symptoms persist.',
        followUpDisposition: 'Follow-up in 2 weeks. Patient education on anxiety management techniques provided.'
      }
    },
    {
      id: '2',
      patientId: 'PT-002',
      patientName: 'Jane Smith',
      date: '2026-01-18 14:15',
      duration: '30 min',
      content: {
        chiefComplaint: 'Follow-up for depression treatment.',
        historyOfPresentIllness: 'Patient on sertraline 50mg for 6 weeks. Reports improved mood and energy levels.',
        reviewOfSystems: 'Sleep improved, appetite returning to normal. No side effects from medication.',
        assessmentAndPlan: 'Major Depressive Disorder (F32.1) - responding well to treatment. Continue current medication.',
        followUpDisposition: 'Continue sertraline. Follow-up in 4 weeks or sooner if symptoms worsen.'
      }
    }
  ]);

  const handleNewNote = () => {
    setShowNewNote(true);
  };

  const handleNoteCreated = (newNote: ScribeSession) => {
    setScribeSessions([newNote, ...scribeSessions]);
    setSelectedSession(newNote);
    setShowNewNote(false);
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
                {scribeSessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => setSelectedSession(session)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedSession?.id === session.id
                        ? 'bg-blue-100 border border-blue-300'
                        : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
                    }`}
                  >
                    <div className="font-medium text-gray-900">{session.patientName}</div>
                    <div className="text-sm text-gray-600">ID: {session.patientId}</div>
                    <div className="text-sm text-gray-600">{session.date}</div>
                    <div className="text-sm text-gray-600">{session.duration}</div>
                  </div>
                ))}
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
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{selectedSession.patientName}</h1>
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
