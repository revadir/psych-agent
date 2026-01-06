import { useAuth } from '../contexts/AuthContext'
import { useChat } from '../contexts/ChatContext'

interface HeaderProps {
  onToggleSidebar: () => void
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  const { user, logout } = useAuth()
  const { createSession } = useChat()

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Mobile menu button */}
          <button
            onClick={onToggleSidebar}
            className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          
          <h1 className="text-lg lg:text-xl font-bold text-gray-900 truncate">
            <span className="hidden sm:inline">Psychiatric Clinical Decision Support</span>
            <span className="sm:hidden">Psych Support</span>
          </h1>
          
          <button
            onClick={() => createSession()}
            className="hidden sm:inline-flex px-3 py-1 text-sm rounded-md bg-indigo-600 text-white hover:bg-indigo-700 transition-colors font-medium"
          >
            New Chat
          </button>
        </div>
        
        <div className="flex items-center space-x-2 lg:space-x-4">
          <div className="text-sm text-gray-700 hidden sm:block font-medium">
            {user?.email}
            {user?.is_admin && (
              <span className="ml-2 px-2 py-1 text-xs bg-indigo-100 text-indigo-700 rounded-full border border-indigo-200">
                Admin
              </span>
            )}
          </div>
          <button
            onClick={logout}
            className="text-sm text-gray-600 hover:text-gray-900 transition-colors px-2 py-1 font-medium"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
