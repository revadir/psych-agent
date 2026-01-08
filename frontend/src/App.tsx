import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ChatProvider } from './contexts/ChatContext'
import { ToastProvider } from './contexts/ToastContext'
import ErrorBoundary from './components/ErrorBoundary'
import Login from './components/Login'
import Chat from './components/Chat'
import AdminDashboard from './components/AdminDashboard'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <AuthProvider>
          <ChatProvider>
            <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-100">
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/admin" element={
                  <ProtectedRoute>
                    <AdminDashboard />
                  </ProtectedRoute>
                } />
                <Route path="/" element={
                  <ProtectedRoute>
                    <Chat />
                  </ProtectedRoute>
                } />
              </Routes>
            </div>
          </ChatProvider>
        </AuthProvider>
      </ToastProvider>
    </ErrorBoundary>
  )
}

export default App
