import { useState } from 'react'

interface MessageInputProps {
  onSendMessage: (content: string) => void
  loading: boolean
  disabled?: boolean
}

export default function MessageInput({ onSendMessage, loading, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!message.trim() || loading || disabled) return

    onSendMessage(message.trim())
    setMessage('')
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="bg-white border-t border-gray-200">
      <div className="max-w-4xl mx-auto">
        <form onSubmit={handleSubmit} className="p-4">
          <div className="flex space-x-3">
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe the patient's symptoms or ask a clinical question..."
              className="flex-1 px-4 py-3 bg-gray-50 text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none transition-colors"
              rows={2}
              disabled={loading || disabled}
            />
            <button
              type="submit"
              disabled={loading || disabled || !message.trim()}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
                  <span>Send</span>
                </div>
              ) : (
                'Send'
              )}
            </button>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Press Enter to send, Shift+Enter for new line
          </div>
        </form>
      </div>
    </div>
  )
}
