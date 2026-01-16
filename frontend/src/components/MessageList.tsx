import { useEffect, useRef, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { Message } from '../contexts/ChatContext'

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8001'

// Extend window interface for scroll function
declare global {
  interface Window {
    scrollToBottom?: () => void
  }
}

interface MessageListProps {
  messages: Message[]
  loading: boolean
}

export default function MessageList({ messages, loading }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const responseStartRef = useRef<HTMLDivElement>(null)

  // Scroll to response start when response is complete
  useEffect(() => {
    const completedResponse = messages.find(msg => msg.role === 'assistant' && !msg.streaming && !msg.thinking)
    if (completedResponse && responseStartRef.current) {
      setTimeout(() => {
        responseStartRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }, 100)
    }
  }, [messages.find(msg => msg.role === 'assistant' && !msg.streaming && !msg.thinking)])

  // Scroll to show new messages and progress indicator
  useEffect(() => {
    const hasThinkingOrStreaming = messages.some(msg => msg.thinking || msg.streaming)
    if (hasThinkingOrStreaming) {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  }, [messages.length, messages.some(msg => msg.thinking || msg.streaming)])

  // Expose scroll to bottom function for external use
  useEffect(() => {
    window.scrollToBottom = () => {
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
    return () => {
      delete window.scrollToBottom
    }
  }, [])

  return (
    <div 
      ref={containerRef}
      className="flex-1 overflow-y-auto bg-gray-50"
      style={{ 
        maxHeight: 'calc(100vh - 180px)',
      }}
    >
      <div className="max-w-4xl mx-auto px-4 py-6 space-y-4">
      {messages.map(message => (
        <MessageBubble key={message.id} message={message} responseStartRef={responseStartRef} />
      ))}
      {(loading || messages.some(msg => msg.thinking)) && (
        <div className="flex justify-start">
          <div className="bg-white border border-gray-200 shadow-sm px-4 py-3 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-600 rounded-full">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="white">
                  {/* 4-pointed star with sharp points and curved inward sides */}
                  <path d="M12 2 L14 10 Q12 8 10 10 L12 2 Z M22 12 L14 10 Q16 12 14 14 L22 12 Z M12 22 L10 14 Q12 16 14 14 L12 22 Z M2 12 L10 14 Q8 12 10 10 L2 12 Z"/>
                </svg>
              </div>
              <div className="flex flex-col">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-purple-500 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
                <span className="text-sm text-gray-600 mt-1">
                  {messages.find(msg => msg.thinking)?.content || 'Processing...'}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
      <div ref={messagesEndRef} />
      </div>
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
  responseStartRef: React.RefObject<HTMLDivElement>
}

function MessageBubble({ message, responseStartRef }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  const [copied, setCopied] = useState(false)
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null)
  const [expandedCitations, setExpandedCitations] = useState<Set<number>>(new Set())
  const [showFeedbackForm, setShowFeedbackForm] = useState(false)
  const [textFeedback, setTextFeedback] = useState('')
  const [submittingFeedback, setSubmittingFeedback] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(message.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleFeedback = async (type: 'up' | 'down') => {
    setFeedback(type)
    setSubmittingFeedback(true)
    
    try {
      const token = localStorage.getItem('token')
      await fetch(`${API_BASE_URL}/api/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message_id: message.id,
          rating: type
        })
      })
    } catch (error) {
      console.error('Failed to submit feedback:', error)
    } finally {
      setSubmittingFeedback(false)
    }
  }

  const handleTextFeedback = async () => {
    if (!textFeedback.trim()) return
    
    setSubmittingFeedback(true)
    try {
      const token = localStorage.getItem('token')
      await fetch(`${API_BASE_URL}/api/feedback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message_id: message.id,
          rating: feedback,
          text_feedback: textFeedback
        })
      })
      setShowFeedbackForm(false)
      setTextFeedback('')
    } catch (error) {
      console.error('Failed to submit text feedback:', error)
    } finally {
      setSubmittingFeedback(false)
    }
  }

  const handleCitationClick = (citationNum: number) => {
    // Scroll to citation in THIS message
    const citationElement = document.getElementById(`citation-${message.id}-${citationNum}`)
    if (citationElement) {
      citationElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
      // Expand citation
      setExpandedCitations(prev => new Set([...prev, citationNum]))
    }
  }
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      {/* Don't render thinking messages as they're handled by the progress indicator */}
      {!message.thinking && (
        <div
          ref={!isUser && (message.streaming || (!message.streaming && !message.thinking)) ? responseStartRef : undefined}
          className={`max-w-xs lg:max-w-2xl px-4 py-2 rounded-lg ${
            isUser
              ? 'bg-indigo-600 text-white'
              : message.error
              ? 'bg-red-50 text-red-900 border border-red-200'
              : 'bg-white text-gray-900 border border-gray-200 shadow-sm'
          }`}
        >
        {/* Regular message content */}
        <div className="text-base leading-relaxed">
          {isUser ? (
            <div className="whitespace-pre-wrap">{message.content}</div>
          ) : (
            <div className="prose prose-base max-w-none prose-headings:text-slate-800 prose-strong:text-slate-700">
              <ReactMarkdown
                components={{
                  // Process all text to convert ^N to clickable citations
                  p: ({ children }) => {
                    const processChildren = (child: any): any => {
                      if (typeof child === 'string') {
                        return child.split(/(\^\d+)/g).map((part, idx) => {
                          const match = part.match(/^\^(\d+)$/)
                          if (match) {
                            const citationNum = parseInt(match[1])
                            return (
                              <sup key={`cite-${idx}`}>
                                <button
                                  onClick={() => handleCitationClick(citationNum)}
                                  className="text-blue-600 hover:text-blue-800 font-medium underline decoration-dotted underline-offset-2 bg-blue-50 hover:bg-blue-100 px-1 rounded transition-colors"
                                >
                                  [{citationNum}]
                                </button>
                              </sup>
                            )
                          }
                          return part
                        })
                      }
                      if (Array.isArray(child)) {
                        return child.map(processChildren)
                      }
                      if (child?.props?.children) {
                        return {
                          ...child,
                          props: {
                            ...child.props,
                            children: processChildren(child.props.children)
                          }
                        }
                      }
                      return child
                    }

                    return <p>{processChildren(children)}</p>
                  },
                  strong: ({ children }) => {
                    const processChildren = (child: any): any => {
                      if (typeof child === 'string') {
                        return child.split(/(\^\d+)/g).map((part, idx) => {
                          const match = part.match(/^\^(\d+)$/)
                          if (match) {
                            const citationNum = parseInt(match[1])
                            return (
                              <sup key={`cite-${idx}`}>
                                <button
                                  onClick={() => handleCitationClick(citationNum)}
                                  className="text-blue-600 hover:text-blue-800 font-medium underline decoration-dotted underline-offset-2 bg-blue-50 hover:bg-blue-100 px-1 rounded transition-colors"
                                >
                                  [{citationNum}]
                                </button>
                              </sup>
                            )
                          }
                          return part
                        })
                      }
                      return child
                    }

                    return <strong>{processChildren(children)}</strong>
                  },
                  li: ({ children }) => {
                    const processChildren = (child: any): any => {
                      if (typeof child === 'string') {
                        return child.split(/(\^\d+)/g).map((part, idx) => {
                          const match = part.match(/^\^(\d+)$/)
                          if (match) {
                            const citationNum = parseInt(match[1])
                            return (
                              <sup key={`cite-${idx}`}>
                                <button
                                  onClick={() => handleCitationClick(citationNum)}
                                  className="text-blue-600 hover:text-blue-800 font-medium underline decoration-dotted underline-offset-2 bg-blue-50 hover:bg-blue-100 px-1 rounded transition-colors"
                                >
                                  [{citationNum}]
                                </button>
                              </sup>
                            )
                          }
                          return part
                        })
                      }
                      if (Array.isArray(child)) {
                        return child.map(processChildren)
                      }
                      if (child?.props?.children) {
                        return {
                          ...child,
                          props: {
                            ...child.props,
                            children: processChildren(child.props.children)
                          }
                        }
                      }
                      return child
                    }

                    return <li>{processChildren(children)}</li>
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            </div>
          )}
          {message.streaming && (
            <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1"></span>
          )}
        </div>
            
            {/* Citations */}
            {message.citations && message.citations.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-200">
                <div className="flex items-center mb-3">
                  <svg className="w-4 h-4 text-gray-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0v12h8V4H6z" clipRule="evenodd"/>
                  </svg>
                  <span className="text-sm font-medium text-gray-700">Sources</span>
                </div>
                <div className="space-y-3">
                  {message.citations.map((citation: any, index: number) => {
                    const citationId = citation.id || index + 1;
                    const isExpanded = expandedCitations.has(citationId);
                    const fullContent = citation.full_content || citation.content;
                    const previewContent = citation.preview || (citation.content?.length > 200 ? citation.content.substring(0, 200) + '...' : citation.content);
                    const hasMore = fullContent && fullContent.length > 200;
                    
                    return (
                      <div 
                        key={`citation-${citationId}`} 
                        id={`citation-${message.id}-${citationId}`}
                        className="border border-gray-200 rounded-lg bg-gray-50"
                      >
                        {/* Citation Header */}
                        <div className="px-4 py-3 border-b border-gray-200 bg-white rounded-t-lg">
                          <div className="flex items-start justify-between">
                            <div className="flex items-start space-x-3">
                              <span className="inline-flex items-center justify-center w-6 h-6 text-xs font-medium text-gray-600 bg-gray-100 rounded-full border border-gray-300">
                                {citationId}
                              </span>
                              <div className="flex-1">
                                {/* Source Document */}
                                <div className="flex items-center mb-2">
                                  <svg className="w-4 h-4 text-blue-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0v12h8V4H6z" clipRule="evenodd"/>
                                  </svg>
                                  <span className="text-sm font-medium text-gray-900">
                                    Diagnostic and Statistical Manual (DSM-5-TR)
                                  </span>
                                </div>
                                
                                {/* Hierarchical path with clear labels */}
                                {citation.hierarchy_path && (
                                  <div className="mb-3">
                                    {citation.hierarchy_path.split(' > ').map((part, index, array) => {
                                      if (index === 0) return null; // Skip "DSM-5-TR" as it's shown above
                                      const isLast = index === array.length - 1;
                                      return (
                                        <div key={index} className="flex items-center text-xs text-gray-600 mb-1">
                                          <div className="flex items-center">
                                            {index === 1 && (
                                              <>
                                                <svg className="w-3 h-3 text-green-600 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.293l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd"/>
                                                </svg>
                                                <span className="font-medium text-green-700">Mental Health Condition:</span>
                                              </>
                                            )}
                                            {index === 2 && (
                                              <>
                                                <svg className="w-3 h-3 text-purple-600 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                                  <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"/>
                                                </svg>
                                                <span className="font-medium text-purple-700">Section:</span>
                                              </>
                                            )}
                                            <span className={`ml-1 ${isLast ? 'font-medium text-gray-800' : 'text-gray-600'}`}>
                                              {part}
                                            </span>
                                          </div>
                                        </div>
                                      );
                                    })}
                                  </div>
                                )}
                                
                                {/* Metadata badges with clear labels */}
                                <div className="flex flex-wrap gap-2">
                                  {citation.icd_code && (
                                    <div className="inline-flex items-center px-2 py-1 text-xs bg-blue-50 border border-blue-200 rounded">
                                      <svg className="w-3 h-3 text-blue-600 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M17.707 9.293a1 1 0 010 1.414l-7 7a1 1 0 01-1.414 0l-7-7A.997.997 0 012 10V5a3 3 0 013-3h5c.256 0 .512.098.707.293l7 7zM5 6a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd"/>
                                      </svg>
                                      <span className="font-medium text-blue-700">Diagnostic Code (ICD-10-CM):</span>
                                      <span className="ml-1 text-blue-800">{citation.icd_code}</span>
                                    </div>
                                  )}
                                  {citation.chunk_type && (
                                    <div className="inline-flex items-center px-2 py-1 text-xs bg-gray-50 border border-gray-200 rounded">
                                      <svg className="w-3 h-3 text-gray-600 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" clipRule="evenodd"/>
                                      </svg>
                                      <span className="font-medium text-gray-700">Content Type:</span>
                                      <span className="ml-1 text-gray-800">
                                        {citation.chunk_type === 'parent' ? 'Complete Entry' : 'Specific Section'}
                                      </span>
                                    </div>
                                  )}
                                  {citation.page && citation.page !== 'Unknown' && citation.page !== null && (
                                    <div className="inline-flex items-center px-2 py-1 text-xs bg-amber-50 border border-amber-200 rounded">
                                      <svg className="w-3 h-3 text-amber-600 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 0v12h8V4H6z" clipRule="evenodd"/>
                                      </svg>
                                      <span className="font-medium text-amber-700">Page:</span>
                                      <span className="ml-1 text-amber-800">{citation.page}</span>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </div>
                            
                            {hasMore && (
                              <button
                                onClick={() => {
                                  const newExpanded = new Set(expandedCitations)
                                  if (newExpanded.has(citationId)) {
                                    newExpanded.delete(citationId)
                                  } else {
                                    newExpanded.add(citationId)
                                  }
                                  setExpandedCitations(newExpanded)
                                }}
                                className="text-xs text-gray-500 hover:text-gray-700 font-medium flex items-center px-2 py-1 rounded hover:bg-gray-100 transition-colors"
                              >
                                {isExpanded ? (
                                  <>
                                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                                    </svg>
                                    Collapse
                                  </>
                                ) : (
                                  <>
                                    <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                                    </svg>
                                    Expand
                                  </>
                                )}
                              </button>
                            )}
                          </div>
                        </div>
                        
                        {/* Citation Content */}
                        <div className="px-4 py-3">
                          <div className="text-sm text-gray-700 leading-relaxed">
                            {(() => {
                              const content = isExpanded ? fullContent : previewContent;
                              // Parse structured content if it starts with DOCUMENT:
                              if (content.startsWith('DOCUMENT:')) {
                                const parts = content.split(';');
                                const textPart = parts.find(p => p.trim().startsWith('TEXT:'));
                                const criteriaPart = parts.find(p => p.trim().startsWith('CRITERIA:'));
                                const actualContent = textPart ? textPart.replace('TEXT:', '').trim() : 
                                                    criteriaPart ? criteriaPart.replace('CRITERIA:', '').trim() : content;
                                return actualContent;
                              }
                              return content;
                            })()}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
            
            {/* Disclaimer for assistant messages - removed from here */}
            
            {/* Message controls for assistant messages */}
            {!isUser && !message.streaming && (
              <div className="flex items-center justify-end mt-2 pt-2 border-t border-gray-100">
                <div className="flex items-center space-x-1">
                  <button
                    onClick={handleCopy}
                    className={`p-1 transition-colors rounded relative ${
                      copied ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-gray-600'
                    }`}
                    title={copied ? 'Copied!' : 'Copy'}
                  >
                    {copied ? (
                      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    )}
                    {copied && (
                      <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                        Response copied!
                      </div>
                    )}
                  </button>
                  <button
                    onClick={() => handleFeedback('up')}
                    disabled={submittingFeedback}
                    className={`p-1 rounded transition-colors ${
                      feedback === 'up' 
                        ? 'text-green-600 bg-green-50' 
                        : 'text-gray-400 hover:text-green-600'
                    } ${submittingFeedback ? 'opacity-50' : ''}`}
                  >
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleFeedback('down')}
                    disabled={submittingFeedback}
                    className={`p-1 rounded transition-colors ${
                      feedback === 'down' 
                        ? 'text-red-600 bg-red-50' 
                        : 'text-gray-400 hover:text-red-600'
                    } ${submittingFeedback ? 'opacity-50' : ''}`}
                  >
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M18 9.5a1.5 1.5 0 11-3 0v-6a1.5 1.5 0 013 0v6zM14 9.667v-5.43a2 2 0 00-1.106-1.79l-.05-.025A4 4 0 0011.057 2H5.64a2 2 0 00-1.962 1.608l-1.2 6A2 2 0 004.44 12H8v4a2 2 0 002 2 1 1 0 001-1v-.667a4 4 0 01.8-2.4l1.4-1.866a4 4 0 00.8-2.4z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => setShowFeedbackForm(!showFeedbackForm)}
                    className="p-1 text-gray-400 hover:text-gray-600 transition-colors rounded"
                    title="Feedback"
                  >
                    <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                  </button>
                </div>
              </div>
            )}
            
            {/* Text Feedback Form */}
            {!isUser && !message.streaming && showFeedbackForm && (
              <div className="mt-3 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <label className="block text-xs font-medium text-gray-700 mb-2">
                  Additional feedback (optional):
                </label>
                <textarea
                  value={textFeedback}
                  onChange={(e) => setTextFeedback(e.target.value)}
                  placeholder="Help us improve by sharing specific feedback about this response..."
                  className="w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none"
                  rows={3}
                />
                <div className="flex justify-end space-x-2 mt-2">
                  <button
                    onClick={() => {
                      setShowFeedbackForm(false)
                      setTextFeedback('')
                    }}
                    className="px-3 py-1 text-xs text-gray-600 hover:text-gray-800 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleTextFeedback}
                    disabled={submittingFeedback || !textFeedback.trim()}
                    className="px-3 py-1 text-xs bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {submittingFeedback ? 'Submitting...' : 'Submit'}
                  </button>
                </div>
              </div>
            )}
          {/* Timestamp - only show when not streaming */}
          {!message.streaming && (
            <div className={`text-xs mt-1 ${isUser ? 'text-indigo-200' : 'text-gray-500'}`}>
              {new Date(message.created_at).toLocaleTimeString()}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
