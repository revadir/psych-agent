import { useEffect, useState } from 'react'
import apiClient from '../services/api'

interface FeedbackStats {
  total_feedback: number
  positive_feedback: number
  negative_feedback: number
  text_feedback_count: number
  avg_rating: number | null
  feedback_by_day: Array<{
    date: string
    total: number
    positive: number
    negative: number
  }>
}

interface FeedbackDetail {
  id: number
  session_id: number
  message_id: number
  user_email: string
  question: string
  response: string
  rating: string | null
  text_feedback: string | null
  model_used: string | null
  created_at: string
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<FeedbackStats | null>(null)
  const [details, setDetails] = useState<FeedbackDetail[]>([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState<{
    rating: string
    hasText: string
    days: number
  }>({
    rating: '',
    hasText: '',
    days: 30
  })

  const loadStats = async () => {
    try {
      const response = await apiClient.get(`/api/admin/feedback/stats?days=${filter.days}`)
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const loadDetails = async () => {
    try {
      const params = new URLSearchParams()
      if (filter.rating) params.append('rating', filter.rating)
      if (filter.hasText) params.append('has_text', filter.hasText)
      
      const response = await apiClient.get(`/api/admin/feedback/details?${params.toString()}`)
      setDetails(response.data)
    } catch (error) {
      console.error('Failed to load details:', error)
    }
  }

  const exportCSV = async () => {
    try {
      const response = await apiClient.get(`/api/admin/feedback/export?days=${filter.days}`, {
        responseType: 'blob'
      })
      
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `feedback_export_${new Date().toISOString().split('T')[0]}.csv`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to export CSV:', error)
    }
  }

  useEffect(() => {
    const loadData = async () => {
      setLoading(true)
      await Promise.all([loadStats(), loadDetails()])
      setLoading(false)
    }
    loadData()
  }, [filter])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Feedback Analytics</h1>
        <p className="text-gray-600 mt-2">Monitor and analyze user feedback on AI responses</p>
      </div>

      {/* Filters */}
      <div className="bg-white p-6 rounded-lg shadow mb-8">
        <h2 className="text-lg font-semibold mb-4">Filters</h2>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Time Period</label>
            <select
              value={filter.days}
              onChange={(e) => setFilter({...filter, days: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value={7}>Last 7 days</option>
              <option value={30}>Last 30 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Rating</label>
            <select
              value={filter.rating}
              onChange={(e) => setFilter({...filter, rating: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Ratings</option>
              <option value="up">Positive</option>
              <option value="down">Negative</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Text Feedback</label>
            <select
              value={filter.hasText}
              onChange={(e) => setFilter({...filter, hasText: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">All Feedback</option>
              <option value="true">With Text</option>
              <option value="false">Rating Only</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={exportCSV}
              className="w-full px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
            >
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Feedback</h3>
            <p className="text-3xl font-bold text-gray-900">{stats.total_feedback}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Positive</h3>
            <p className="text-3xl font-bold text-green-600">{stats.positive_feedback}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Negative</h3>
            <p className="text-3xl font-bold text-red-600">{stats.negative_feedback}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">With Text</h3>
            <p className="text-3xl font-bold text-blue-600">{stats.text_feedback_count}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Satisfaction</h3>
            <p className="text-3xl font-bold text-indigo-600">
              {stats.avg_rating ? `${Math.round(stats.avg_rating * 100)}%` : 'N/A'}
            </p>
          </div>
        </div>
      )}

      {/* Feedback Details Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Feedback</h2>
        </div>
        <div className="overflow-x-auto max-h-96 overflow-y-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50 sticky top-0">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">Rating</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Question</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Text Feedback</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {details.slice(0, 50).map((feedback) => (
                <tr key={feedback.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(feedback.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {feedback.user_email}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {feedback.rating === 'up' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        👍 Positive
                      </span>
                    )}
                    {feedback.rating === 'down' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        👎 Negative
                      </span>
                    )}
                    {!feedback.rating && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        No Rating
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {feedback.question}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs">
                    {feedback.text_feedback ? (
                      <div className="truncate" title={feedback.text_feedback}>
                        {feedback.text_feedback}
                      </div>
                    ) : (
                      <span className="text-gray-400 italic">No text feedback</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
        </div>
      </div>
    </div>
  )
}