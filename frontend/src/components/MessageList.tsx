import { useEffect, useRef, useState } from 'react'

interface Message {
  id: number
  role: string
  content: string
  created_at: string
}

interface MessageListProps {
  messages: Message[]
  loading: boolean
}

export default function MessageList({ messages, loading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  return (
    <div 
      ref={containerRef}
      className="flex-1 overflow-y-auto p-4 space-y-4"
      style={{ maxHeight: 'calc(100vh - 200px)' }}
    >
      {messages.map(message => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {loading && (
        <div className="flex justify-start">
          <div className="bg-gray-200 text-gray-900 px-4 py-2 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
              <span>Analyzing...</span>
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
    </div>
  )
}

interface MessageBubbleProps {
  message: Message & { 
    thinking?: boolean
    streaming?: boolean
    citations?: any[]
    error?: boolean
  }
}

function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null)
  const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set())

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleFeedback = (type: 'up' | 'down') => {
    setFeedback(type)
    // TODO: Send feedback to backend
  }

  const toggleCitation = (citationId: number) => {
    console.log('toggleCitation called with ID:', citationId);
    console.log('Current expandedCitations:', expandedCitations);
    const newExpanded = new Set(expandedCitations)
    if (newExpanded.has(citationId)) {
      newExpanded.delete(citationId)
      console.log('Collapsing citation', citationId);
    } else {
      newExpanded.add(citationId)
      console.log('Expanding citation', citationId);
    }
    setExpandedCitations(newExpanded)
    console.log('New expandedCitations:', newExpanded);
  }
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-xs lg:max-w-2xl px-4 py-2 rounded-lg ${
          isUser
            ? 'bg-indigo-600 text-white'
            : message.error
            ? 'bg-red-50 text-red-900 border border-red-200'
            : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
        }`}
      >
        {/* Thinking indicator */}
        {message.thinking && (
          <div className="flex items-center space-x-2 text-gray-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
            <span className="text-sm italic">{message.content || 'Thinking...'}</span>
          </div>
        )}
        
        {/* Regular message content */}
        {!message.thinking && (
          <>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {message.content}
              {message.streaming && (
                <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1"></span>
              )}
            </div>
            
            {/* Citations */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <p className="text-xs font-medium text-gray-600 mb-2">DSM-5-TR References:</p>
                {message.citations.map((citation: any, index: number) => {
                  const citationId = citation.id || index + 1;
                  const isExpanded = expandedCitations.has(citationId);
                  const fullContent = citation.full_content || citation.content;
                  const previewContent = citation.preview || (citation.content?.length > 150 ? citation.content.substring(0, 150) + '...' : citation.content);
                  const hasMore = fullContent && fullContent.length > 150;
                  
                  console.log('Rendering citation:', {
                    citationId,
                    isExpanded,
                    hasMore,
                    fullContentLength: fullContent?.length,
                    previewLength: previewContent?.length,
                    citation
                  });
                  
                  return (
                    <div key={`citation-${citationId}`} className="mb-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                      {/* Citation Header */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex-1">
                          <div className="flex items-center mb-2">
                            <span className="text-xs font-bold text-blue-800 bg-blue-200 px-2 py-1 rounded-full mr-2">
                              [{citationId}]
                            </span>
                            <span className="text-sm font-semibold text-gray-800">
                              {citation.document || 'DSM-5-TR'}
                            </span>
                          </div>
                          
                          {/* Structured metadata */}
                          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-2">
                            {citation.chapter && (
                              <div><span className="font-medium">Chapter:</span> {citation.chapter}</div>
                            )}
                            {citation.section && (
                              <div><span className="font-medium">Section:</span> {citation.section}</div>
                            )}
                            {citation.icd_code && (
                              <div><span className="font-medium">ICD-10:</span> {citation.icd_code}</div>
                            )}
                            {citation.page && (
                              <div><span className="font-medium">Page:</span> {citation.page}</div>
                            )}
                          </div>
                        </div>
                        
                        {hasMore && (
                          <button
                            onClick={() => {
                              console.log('Toggling citation:', citationId, 'Current expanded:', expandedCitations);
                              toggleCitation(citationId);
                            }}
                            className="text-xs text-blue-700 hover:text-blue-900 font-medium flex items-center bg-white px-2 py-1 rounded border border-blue-300 hover:bg-blue-50 transition-colors"
                          >
                            {isExpanded ? (
                              <>
                                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                </svg>
                                Show Less
                              </>
                            ) : (
                              <>
                                <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                </svg>
                                Show More
                              </>
                            )}
                          </button>
                        )}
                      </div>
                      
                      {/* Citation Content */}
                      <div className="bg-white p-3 rounded border border-gray-200">
                        <div className="text-xs text-gray-800 leading-relaxed whitespace-pre-wrap">
                          {isExpanded ? fullContent : previewContent}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
            
            {/* Disclaimer for assistant messages */}
            {!isUser && !message.thinking && !message.streaming && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                <p className="text-xs text-gray-500 italic">
                  ⚠️ This is a clinical decision support tool and not a replacement for professional psychiatric evaluation.
                </p>
              </div>
            )}

            {/* Message controls for assistant messages */}
            {!isUser && !message.thinking && !message.streaming && (
              <div className="flex items-center justify-between mt-2 pt-2 border-t border-gray-100">
                <button
                  onClick={handleCopy}
                  className="flex items-center space-x-1 text-xs text-gray-500 hover:text-gray-700 transition-colors"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span>{copied ? 'Copied!' : 'Copy'}</span>
                </button>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleFeedback('up')}
                    className={`p-1 rounded transition-colors ${
                      feedback === 'up' 
                        ? 'text-green-600 bg-green-50' 
                        : 'text-gray-400 hover:text-green-600'
                    }`}
                  >
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleFeedback('down')}
                    className={`p-1 rounded transition-colors ${
                      feedback === 'down' 
                        ? 'text-red-600 bg-red-50' 
                        : 'text-gray-400 hover:text-red-600'
                    }`}
                  >
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.106-1.79l-.05-.025A4 4 0 0011.057 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </>
        )}
        
        <div className={`text-xs mt-1 ${isUser ? 'text-indigo-200' : 'text-gray-500'}`}>
          {new Date(message.created_at).toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
