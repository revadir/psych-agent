import { useAuth } from '../contexts/AuthContext'
import { useChat } from '../contexts/ChatContext'
import { useNavigate, useLocation } from 'react-router-dom'

interface HeaderProps {
  onToggleSidebar: () => void
}

export default function Header({ onToggleSidebar }: HeaderProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  
  const isAdminPage = location.pathname === '/admin'

  return (
    <header className="bg-white border-b border-gray-200 px-4 py-3 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-lg lg:text-xl font-bold text-gray-900 truncate">
            <span className="hidden sm:inline">
              {isAdminPage ? 'Admin Dashboard' : 'Clinical Session Recording & Analysis'}
            </span>
            <span className="sm:hidden">
              {isAdminPage ? 'Admin' : 'Clinical Recording'}
            </span>
          </h1>
        </div>
        
        <div className="flex items-center space-x-2 lg:space-x-4">
          {/* Chat Panel Toggle */}
          {!isAdminPage && (
            <button
              onClick={onToggleSidebar}
              className="flex items-center px-3 py-2 text-sm rounded-md bg-indigo-600 text-white hover:bg-indigo-700 transition-colors font-medium"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              <span className="hidden sm:inline">Clinical Support</span>
              <span className="sm:hidden">Chat</span>
            </button>
          )}
          
          {user?.is_admin && (
            <button
              onClick={() => navigate(isAdminPage ? '/' : '/admin')}
              className="px-3 py-1 text-sm rounded-md border border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors font-medium"
            >
              {isAdminPage ? '🎙️ Recording' : '📊 Admin'}
            </button>
          )}
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
