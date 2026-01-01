import { useEffect, useState } from 'react'
import { useChat } from '../contexts/ChatContext'
import Header from './Header'
import Sidebar from './Sidebar'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

export default function Chat() {
  const { currentSession, messages, loading, sendMessage, createSession } = useChat()
  const [sidebarOpen, setSidebarOpen] = useState(false)

  // Close sidebar on mobile when session changes
  useEffect(() => {
    setSidebarOpen(false)
  }, [currentSession])

  return (
    <div className="h-screen flex flex-col">
      <Header onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex-1 flex overflow-hidden relative">
        {/* Mobile sidebar overlay */}
        {sidebarOpen && (
          <div 
            className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
        
        {/* Sidebar */}
        <div className={`
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0 transition-transform duration-300 ease-in-out
          fixed lg:relative z-50 lg:z-auto
          w-80 h-full lg:h-auto
        `}>
          <Sidebar />
        </div>
        
        <div className="flex-1 flex flex-col min-w-0 h-full">
          {currentSession ? (
            <div className="flex-1 flex flex-col h-full">
              <MessageList messages={messages} loading={loading} />
              <MessageInput 
                onSendMessage={sendMessage} 
                loading={loading}
                disabled={!currentSession}
              />
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center bg-gray-50 p-4">
              <div className="text-center max-w-md">
                <div className="mb-6">
                  <div className="mx-auto w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
                    <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </div>
                  <h2 className="text-xl lg:text-2xl font-semibold text-gray-900 mb-2">
                    Welcome to Clinical Decision Support
                  </h2>
                  <p className="text-gray-600 mb-6 text-sm lg:text-base">
                    Start a new chat session to get evidence-based psychiatric guidance 
                    using DSM-5-TR criteria and clinical reasoning.
                  </p>
                </div>
                
                <button
                  onClick={() => createSession()}
                  className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium w-full lg:w-auto"
                >
                  Start New Chat Session
                </button>
                
                <div className="mt-8 text-sm text-gray-500">
                  <p className="font-medium mb-2">How to use:</p>
                  <ul className="text-left space-y-1">
                    <li>• Describe patient symptoms or clinical scenarios</li>
                    <li>• Ask about diagnostic criteria or differential diagnosis</li>
                    <li>• Request guidance on treatment considerations</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
