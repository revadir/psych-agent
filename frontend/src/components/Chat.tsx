import { useEffect, useState } from 'react'
import { useChat } from '../contexts/ChatContext'
import Header from './Header'
import MessageList from './MessageList'
import MessageInput from './MessageInput'
import ClinicalRecording from './ClinicalRecording'

export default function Chat() {
  const { currentSession, messages, loading, sendMessage, createSession } = useChat()
  const [chatPanelOpen, setChatPanelOpen] = useState(false)

  return (
    <div className="h-screen flex flex-col">
      <Header onToggleSidebar={() => setChatPanelOpen(!chatPanelOpen)} />
      
      <div className="flex-1 flex overflow-hidden">
        {/* Main Recording Area */}
        <div className="flex-1 flex flex-col">
          <ClinicalRecording />
        </div>
        
        {/* Chat Panel - Right Side */}
        <div className={`
          ${chatPanelOpen ? 'w-96' : 'w-0'}
          transition-all duration-300 ease-in-out overflow-hidden
          bg-white border-l border-gray-200 flex flex-col
        `}>
          {chatPanelOpen && (
            <>
              {/* Chat Header */}
              <div className="bg-indigo-50 border-b border-indigo-200 p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-semibold text-indigo-900">Clinical Decision Support</h3>
                    <p className="text-sm text-indigo-600">Ask questions about diagnosis, treatment, DSM-5-TR criteria</p>
                  </div>
                  <button
                    onClick={() => setChatPanelOpen(false)}
                    className="p-1 text-indigo-400 hover:text-indigo-600 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Chat Content */}
              {currentSession ? (
                <div className="flex-1 flex flex-col min-h-0">
                  <div className="flex-1 overflow-hidden">
                    <MessageList messages={messages} loading={loading} />
                  </div>
                  <MessageInput 
                    onSendMessage={sendMessage} 
                    loading={loading}
                    disabled={!currentSession}
                  />
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center p-4">
                  <div className="text-center">
                    <div className="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-3">
                      <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                    </div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Clinical Support Chat</h4>
                    <p className="text-xs text-gray-600 mb-4">Get evidence-based guidance using DSM-5-TR and ICD-11</p>
                    <button
                      onClick={() => createSession()}
                      className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      Start Chat Session
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
      
      {/* Chat Toggle Button - Fixed Position */}
      {!chatPanelOpen && (
        <button
          onClick={() => setChatPanelOpen(true)}
          className="fixed right-4 top-1/2 transform -translate-y-1/2 bg-indigo-600 text-white p-3 rounded-l-lg shadow-lg hover:bg-indigo-700 transition-colors z-50"
          title="Open Clinical Decision Support"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}
    </div>
  )
}
