import { useQuery } from '@tanstack/react-query'
import { format } from 'date-fns'
import { Clock, TrendingUp, Newspaper } from 'lucide-react'
import Modal from './Modal'
import Loader from './Loader'
import { getAlertHistory } from '../lib/api'

interface AlertHistoryModalProps {
  isOpen: boolean
  onClose: () => void
  alertId: number
}

interface HistoryEvent {
  id: number
  alert_id: number
  triggered_at: string
  trigger_price?: number
  trigger_sentiment?: number
  trigger_volume?: number
  message?: string
}

export default function AlertHistoryModal({ isOpen, onClose, alertId }: AlertHistoryModalProps) {
  const { data: historyData, isLoading } = useQuery({
    queryKey: ['alert-history', alertId],
    queryFn: async () => {
      const res = await getAlertHistory(alertId)
      return res.data
    },
    enabled: isOpen && !!alertId,
  })

  const history: HistoryEvent[] = historyData || []

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Alert History" size="lg">
      {isLoading ? (
        <div className="py-8">
          <Loader />
        </div>
      ) : history.length === 0 ? (
        <div className="text-center py-12">
          <Clock className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No trigger history</h3>
          <p className="text-gray-600">This alert has not been triggered yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Showing {history.length} trigger event{history.length !== 1 ? 's' : ''}
          </p>

          <div className="space-y-3">
            {history.map((event) => (
              <div
                key={event.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      {event.trigger_sentiment !== undefined ? (
                        <Newspaper className="w-4 h-4 text-primary-600" />
                      ) : (
                        <TrendingUp className="w-4 h-4 text-primary-600" />
                      )}
                      <span className="font-semibold text-gray-900">
                        {format(new Date(event.triggered_at), 'MMM d, yyyy h:mm a')}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {event.trigger_price !== undefined && (
                        <div>
                          <span className="text-gray-600">Trigger Price:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            ${event.trigger_price.toFixed(2)}
                          </span>
                        </div>
                      )}

                      {event.trigger_sentiment !== undefined && (
                        <div>
                          <span className="text-gray-600">Trigger Sentiment:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {event.trigger_sentiment.toFixed(3)}
                          </span>
                        </div>
                      )}

                      {event.trigger_volume !== undefined && (
                        <div>
                          <span className="text-gray-600">Trigger Volume:</span>
                          <span className="ml-2 font-medium text-gray-900">
                            {event.trigger_volume.toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>

                    {event.message && (
                      <div className="mt-3 p-3 bg-blue-50 border border-blue-100 rounded text-sm text-blue-900">
                        {event.message}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-end pt-4 border-t border-gray-200 mt-6">
        <button
          onClick={onClose}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
        >
          Close
        </button>
      </div>
    </Modal>
  )
}
