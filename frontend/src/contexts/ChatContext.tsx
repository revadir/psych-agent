import React, { createContext, useContext, useState, ReactNode } from 'react'
import apiClient from '../services/api'
import { useToast } from './ToastContext'

interface Message {
  id: number
  role: string
  content: string
  created_at: string
}

interface Session {
  id: number
  title: string
  created_at: string
  updated_at: string
  messages?: Message[]
}

interface ChatContextType {
  sessions: Session[]
  currentSession: Session | null
  messages: Message[]
  loading: boolean
  createSession: (title?: string) => Promise<void>
  loadSession: (sessionId: number) => Promise<void>
  sendMessage: (content: string) => Promise<void>
  deleteSession: (sessionId: number) => Promise<void>
  loadSessions: () => Promise<void>
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export const useChat = () => {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider')
  }
  return context
}

interface ChatProviderProps {
  children: ReactNode
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [sessions, setSessions] = useState<Session[]>([])
  const [currentSession, setCurrentSession] = useState<Session | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [loading, setLoading] = useState(false)
  const { addToast } = useToast()

  const loadSessions = async () => {
    try {
      const response = await apiClient.get('/chat/sessions')
      setSessions(response.data)
    } catch (error) {
      console.error('Failed to load sessions:', error)
      addToast({
        type: 'error',
        message: 'Failed to load chat sessions'
      })
    }
  }

  const createSession = async (title?: string) => {
    try {
      const response = await apiClient.post('/chat/sessions', { 
        title: title || `Chat ${new Date().toLocaleString()}` 
      })
      const newSession = response.data
      setSessions(prev => [newSession, ...prev])
      setCurrentSession(newSession)
      setMessages([])
      addToast({
        type: 'success',
        message: 'New chat session created'
      })
    } catch (error) {
      console.error('Failed to create session:', error)
      addToast({
        type: 'error',
        message: 'Failed to create new session'
      })
    }
  }

  const loadSession = async (sessionId: number) => {
    try {
      const response = await apiClient.get(`/chat/sessions/${sessionId}`)
      const session = response.data
      setCurrentSession(session)
      setMessages(session.messages || [])
    } catch (error) {
      console.error('Failed to load session:', error)
      addToast({
        type: 'error',
        message: 'Failed to load chat session'
      })
    }
  }

  const sendMessage = async (content: string) => {
    if (!currentSession || loading) return

    setLoading(true)
    
    try {
      // Add user message immediately
      const tempUserMessage = {
        id: Date.now(),
        role: 'user',
        content,
        created_at: new Date().toISOString()
      }
      setMessages(prev => [...prev, tempUserMessage])

      // Add thinking placeholder
      const thinkingMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Retrieving DSM-5-TR criteria and analyzing...',
        created_at: new Date().toISOString(),
        thinking: true
      }
      setMessages(prev => [...prev, thinkingMessage])

      // Try streaming first
      try {
        const token = localStorage.getItem('token')
        const response = await fetch(`/api/chat/sessions/${currentSession.id}/messages/stream`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ content })
        })

        if (!response.body) throw new Error('No response body')

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let assistantMessage = ''
        let citations: any[] = []

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6))
                
                switch (data.type) {
                  case 'thinking':
                    setMessages(prev => prev.map(msg => 
                      msg.thinking ? { ...msg, content: data.data.status } : msg
                    ))
                    break
                  
                  case 'citations':
                    citations = data.data
                    break
                  
                  case 'response_start':
                    setMessages(prev => prev.filter(msg => !msg.thinking).concat([{
                      id: Date.now() + 2,
                      role: 'assistant',
                      content: '',
                      created_at: new Date().toISOString(),
                      streaming: true,
                      citations
                    }]))
                    break
                  
                  case 'response_chunk':
                    assistantMessage += (assistantMessage ? ' ' : '') + data.data.chunk
                    setMessages(prev => prev.map(msg => 
                      msg.streaming ? { ...msg, content: assistantMessage } : msg
                    ))
                    break
                  
                  case 'response_complete':
                    setMessages(prev => prev.map(msg => 
                      msg.streaming ? { 
                        ...msg, 
                        id: data.data.id,
                        content: data.data.full_response,
                        streaming: false,
                        citations: data.data.citations || citations
                      } : msg
                    ))
                    break
                  
                  case 'error':
                    setMessages(prev => prev.filter(msg => !msg.thinking && !msg.streaming).concat([{
                      id: data.data.id,
                      role: 'assistant',
                      content: data.data.message,
                      created_at: new Date().toISOString(),
                      error: true
                    }]))
                    break
                }
              } catch (e) {
                console.error('Error parsing SSE data:', e)
              }
            }
          }
        }
      } catch (streamError) {
        console.log('Streaming failed, falling back to regular API:', streamError)
        
        // Fallback to regular API
        const response = await apiClient.post(`/chat/sessions/${currentSession.id}/messages`, {
          content
        })
        
        const { user_message, assistant_message, agent_response } = response.data
        
        setMessages(prev => prev.filter(msg => !msg.thinking).concat([{
          ...assistant_message,
          citations: agent_response?.citations || []
        }]))
      }
      
      // Update session timestamp
      setSessions(prev => prev.map(s => 
        s.id === currentSession.id 
          ? { ...s, updated_at: new Date().toISOString() }
          : s
      ))
      
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => prev.filter(msg => !msg.thinking))
      addToast({
        type: 'error',
        message: 'Failed to send message. Please try again.'
      })
    } finally {
      setLoading(false)
    }
  }

  const deleteSession = async (sessionId: number) => {
    try {
      await apiClient.delete(`/chat/sessions/${sessionId}`)
      setSessions(prev => prev.filter(s => s.id !== sessionId))
      
      if (currentSession?.id === sessionId) {
        setCurrentSession(null)
        setMessages([])
      }
      
      addToast({
        type: 'success',
        message: 'Chat session deleted'
      })
    } catch (error) {
      console.error('Failed to delete session:', error)
      addToast({
        type: 'error',
        message: 'Failed to delete session'
      })
    }
  }

  const value: ChatContextType = {
    sessions,
    currentSession,
    messages,
    loading,
    createSession,
    loadSession,
    sendMessage,
    deleteSession,
    loadSessions,
  }

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>
}
