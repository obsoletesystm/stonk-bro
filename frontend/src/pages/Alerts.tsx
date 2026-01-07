import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Bell, BellOff, Trash2, History, TrendingUp, Newspaper } from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import CreateAlertModal from '../components/CreateAlertModal'
import AlertHistoryModal from '../components/AlertHistoryModal'
import { getAlerts, deleteAlert } from '../lib/api'
import type { Alert } from '../types'
import { format } from 'date-fns'

export default function Alerts() {
  const queryClient = useQueryClient()
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [historyAlertId, setHistoryAlertId] = useState<number | null>(null)
  const [filter, setFilter] = useState<'all' | 'active' | 'triggered' | 'paused'>('all')

  const { data: alertsData, isLoading } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await getAlerts()
      return res.data
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
    },
  })

  const alerts: Alert[] = alertsData || []

  const filteredAlerts = alerts.filter((alert) => {
    if (filter === 'all') return true
    return alert.status.toLowerCase() === filter
  })

  const activeCount = alerts.filter((a) => a.status === 'active').length
  const triggeredCount = alerts.filter((a) => a.status === 'triggered').length
  const priceAlerts = alerts.filter((a) =>
    ['PRICE_ABOVE', 'PRICE_BELOW', 'PRICE_CHANGE_PERCENT', 'VOLUME_ABOVE'].includes(a.condition)
  ).length
  const newsAlerts = alerts.filter((a) =>
    ['SENTIMENT_ABOVE', 'SENTIMENT_BELOW', 'SENTIMENT_CHANGE', 'NEWS_VOLUME_SPIKE'].includes(a.condition)
  ).length

  const handleDelete = (id: number, symbol: string) => {
    if (window.confirm(`Are you sure you want to delete the alert for ${symbol}?`)) {
      deleteMutation.mutate(id)
    }
  }

  const getConditionLabel = (condition: string) => {
    const labels: Record<string, string> = {
      PRICE_ABOVE: 'Price Above',
      PRICE_BELOW: 'Price Below',
      PRICE_CHANGE_PERCENT: 'Price Change %',
      VOLUME_ABOVE: 'Volume Above',
      SENTIMENT_ABOVE: 'Sentiment Above',
      SENTIMENT_BELOW: 'Sentiment Below',
      SENTIMENT_CHANGE: 'Sentiment Change',
      NEWS_VOLUME_SPIKE: 'News Volume Spike',
    }
    return labels[condition] || condition
  }

  const getAlertTypeIcon = (condition: string) => {
    const isNews = ['SENTIMENT_ABOVE', 'SENTIMENT_BELOW', 'SENTIMENT_CHANGE', 'NEWS_VOLUME_SPIKE'].includes(condition)
    return isNews ? <Newspaper className="w-4 h-4" /> : <TrendingUp className="w-4 h-4" />
  }

  if (isLoading) return <Loader />

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Alerts</h1>
          <p className="text-gray-600 mt-2">Manage your price and sentiment alerts</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Create Alert</span>
        </button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{activeCount}</p>
            </div>
            <Bell className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Triggered</p>
              <p className="text-2xl font-bold text-orange-600 mt-1">{triggeredCount}</p>
            </div>
            <BellOff className="w-8 h-8 text-orange-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Price Alerts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{priceAlerts}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-primary-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">News Alerts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{newsAlerts}</p>
            </div>
            <Newspaper className="w-8 h-8 text-primary-600" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="mb-6 flex items-center space-x-2">
        <span className="text-sm font-medium text-gray-700">Filter:</span>
        {(['all', 'active', 'triggered', 'paused'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === status
                ? 'bg-primary-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </button>
        ))}
      </div>

      {/* Alerts Table */}
      <Card>
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-12">
            <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {filter === 'all' ? 'No alerts yet' : `No ${filter} alerts`}
            </h3>
            <p className="text-gray-600 mb-6">
              {filter === 'all'
                ? 'Create your first alert to get notified about price movements and sentiment changes'
                : `You don't have any ${filter} alerts`}
            </p>
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
            >
              <Plus className="w-5 h-5" />
              <span>Create Your First Alert</span>
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Type</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Symbol</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Condition</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Threshold</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Created</th>
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Triggered</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredAlerts.map((alert) => (
                  <tr
                    key={alert.id}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    <td className="py-4 px-4">
                      <div className="flex items-center space-x-2 text-gray-600">
                        {getAlertTypeIcon(alert.condition)}
                      </div>
                    </td>
                    <td className="py-4 px-4">
                      <span className="font-semibold text-gray-900">{alert.symbol}</span>
                    </td>
                    <td className="py-4 px-4 text-gray-700">
                      {getConditionLabel(alert.condition)}
                    </td>
                    <td className="py-4 px-4 text-right text-gray-900">
                      {alert.condition.includes('PERCENT') || alert.condition.includes('SENTIMENT')
                        ? alert.threshold_value.toFixed(3)
                        : alert.threshold_value.toLocaleString()}
                    </td>
                    <td className="py-4 px-4">
                      <span
                        className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${
                          alert.status === 'active'
                            ? 'bg-green-100 text-green-800'
                            : alert.status === 'triggered'
                            ? 'bg-orange-100 text-orange-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {alert.status}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      {format(new Date(alert.created_at), 'MMM d, yyyy')}
                    </td>
                    <td className="py-4 px-4 text-sm text-gray-600">
                      {alert.triggered_at
                        ? format(new Date(alert.triggered_at), 'MMM d, h:mm a')
                        : '-'}
                    </td>
                    <td className="py-4 px-4">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => setHistoryAlertId(alert.id)}
                          className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                          title="View history"
                        >
                          <History className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(alert.id, alert.symbol)}
                          className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete alert"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Create Alert Modal */}
      <CreateAlertModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />

      {/* Alert History Modal */}
      {historyAlertId && (
        <AlertHistoryModal
          isOpen={!!historyAlertId}
          onClose={() => setHistoryAlertId(null)}
          alertId={historyAlertId}
        />
      )}
    </div>
  )
}
