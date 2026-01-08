import { useState } from 'react'

interface MessageInputProps {
  onSendMessage: (content: string) => void
  loading: boolean
  disabled?: boolean
}

export default function MessageInput({ onSendMessage, loading, disabled }: MessageInputProps) {
  const [message, setMessage] = useState('')

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value)
    // Scroll to bottom when user starts typing
    if (e.target.value && window.scrollToBottom) {
      window.scrollToBottom()
    }
  }

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
          <div className="relative">
            <textarea
              value={message}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder="Describe the patient's symptoms or ask a clinical question..."
              className="w-full pl-4 pr-16 py-3 bg-gray-50 text-gray-900 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none transition-colors"
              rows={2}
              disabled={loading || disabled}
            />
            <button
              type="submit"
              disabled={loading || disabled || !message.trim()}
              className="absolute right-2 top-2 p-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" transform="rotate(90 12 12)" />
                </svg>
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
