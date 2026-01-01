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
    <form onSubmit={handleSubmit} className="p-4 border-t walnut-card border-amber-600/30">
      <div className="flex space-x-2">
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Describe the patient's symptoms or ask a clinical question..."
          className="flex-1 px-3 py-2 bg-white text-black border border-amber-600/30 rounded-md focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-amber-500 resize-none font-['Exo_2']"
          rows={2}
          disabled={loading || disabled}
        />
        <button
          type="submit"
          disabled={loading || disabled || !message.trim()}
          className="sci-fi-button px-6 py-2 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
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
      <div className="mt-2 text-xs text-amber-400 font-['Exo_2']">
        Press Enter to send, Shift+Enter for new line
      </div>
    </form>
  )
}
