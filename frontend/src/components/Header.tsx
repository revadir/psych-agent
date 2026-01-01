import { useAuth } from '../contexts/AuthContext'
import { useChat } from '../contexts/ChatContext'

interface HeaderProps {
  onToggleSidebar: () => void
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  const { user, logout } = useAuth()
  const { createSession } = useChat()

  return (
    <header className="walnut-card border-b border-amber-600/30 px-4 py-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={onToggleSidebar}
            className="lg:hidden sci-fi-button p-2 rounded-md"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <h1 className="sci-fi-heading text-lg lg:text-xl glow-text truncate">
            <span className="hidden sm:inline">Psychiatric Clinical Decision Support</span>
            <span className="sm:hidden">Psych Support</span>
          </h1>
          
          <button
            onClick={() => createSession()}
            className="hidden sm:inline-flex sci-fi-button px-3 py-1 text-sm rounded-md transition-colors"
          >
            New Chat
          </button>
        </div>
        
        <div className="flex items-center space-x-2 lg:space-x-4">
          <div className="text-sm text-amber-300 hidden sm:block font-medium">
            {user?.email}
            {user?.is_admin && (
              <span className="ml-2 px-2 py-1 text-xs bg-amber-600/20 text-amber-300 rounded-full border border-amber-600/30">
                Admin
              </span>
            )}
          </div>
          <button
            onClick={logout}
            className="text-sm text-amber-400 hover:text-amber-300 transition-colors px-2 py-1 font-medium"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
