import { useEffect, useState } from 'react'
import { useChat } from '../contexts/ChatContext'

interface Session {
  id: number
  title: string
  created_at: string
  updated_at: string
}

export default function Sidebar() {
  const { sessions, currentSession, loadSession, deleteSession, loadSessions } = useChat()
  const [deleteConfirm, setDeleteConfirm] = useState<number | null>(null)

  useEffect(() => {
    loadSessions()
  }, [])

  const handleDeleteSession = async (sessionId: number) => {
    if (deleteConfirm === sessionId) {
      await deleteSession(sessionId)
      setDeleteConfirm(null)
    } else {
      setDeleteConfirm(sessionId)
      // Auto-cancel confirmation after 3 seconds
      setTimeout(() => setDeleteConfirm(null), 3000)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffTime = Math.abs(now.getTime() - date.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

    if (diffDays === 1) return 'Today'
    if (diffDays === 2) return 'Yesterday'
    if (diffDays <= 7) return `${diffDays - 1} days ago`
    return date.toLocaleDateString()
  }

  return (
    <div className="w-80 bg-gray-50 border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Chat Sessions</h2>
        <p className="text-sm text-gray-600 mt-1">
          {sessions.length} session{sessions.length !== 1 ? 's' : ''}
        </p>
      </div>
      
      <div className="flex-1 overflow-y-auto">
        {sessions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <p>No chat sessions yet.</p>
            <p className="text-sm mt-1">Create a new chat to get started.</p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {sessions.map(session => (
              <SessionItem
                key={session.id}
                session={session}
                isActive={currentSession?.id === session.id}
                onSelect={() => loadSession(session.id)}
                onDelete={() => handleDeleteSession(session.id)}
                deleteConfirm={deleteConfirm === session.id}
                formatDate={formatDate}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

interface SessionItemProps {
  session: Session
  isActive: boolean
  onSelect: () => void
  onDelete: () => void
  deleteConfirm: boolean
  formatDate: (date: string) => string
}

function SessionItem({ 
  session, 
  isActive, 
  onSelect, 
  onDelete, 
  deleteConfirm, 
  formatDate 
}: SessionItemProps) {
  return (
    <div
      className={`group p-3 rounded-lg cursor-pointer transition-colors ${
        isActive 
          ? 'bg-indigo-100 border border-indigo-200' 
          : 'hover:bg-gray-100 border border-transparent'
      }`}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <h3 className={`text-sm font-medium truncate ${
            isActive ? 'text-indigo-900' : 'text-gray-900'
          }`}>
            {session.title}
          </h3>
          <p className={`text-xs mt-1 ${
            isActive ? 'text-indigo-600' : 'text-gray-500'
          }`}>
            {formatDate(session.updated_at)}
          </p>
        </div>
        
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          className={`ml-2 p-1 rounded text-xs transition-colors ${
            deleteConfirm
              ? 'bg-red-100 text-red-700 hover:bg-red-200'
              : 'text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100'
          }`}
          title={deleteConfirm ? 'Click again to confirm' : 'Delete session'}
        >
          {deleteConfirm ? 'Confirm?' : '×'}
        </button>
      </div>
    </div>
  )
}
