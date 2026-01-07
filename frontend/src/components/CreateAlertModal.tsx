import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import Modal from './Modal'
import { createAlert } from '../lib/api'

interface CreateAlertModalProps {
  isOpen: boolean
  onClose: () => void
}

export default function CreateAlertModal({ isOpen, onClose }: CreateAlertModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    symbol: '',
    condition: 'PRICE_ABOVE',
    threshold_value: '',
    message: '',
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => createAlert(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] })
      onClose()
      setFormData({
        symbol: '',
        condition: 'PRICE_ABOVE',
        threshold_value: '',
        message: '',
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      symbol: formData.symbol.toUpperCase(),
      condition: formData.condition,
      threshold_value: parseFloat(formData.threshold_value),
      message: formData.message || undefined,
    })
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  const priceConditions = [
    { value: 'PRICE_ABOVE', label: 'Price Above' },
    { value: 'PRICE_BELOW', label: 'Price Below' },
    { value: 'PRICE_CHANGE_PERCENT', label: 'Price Change %' },
    { value: 'VOLUME_ABOVE', label: 'Volume Above' },
  ]

  const sentimentConditions = [
    { value: 'SENTIMENT_ABOVE', label: 'Sentiment Above' },
    { value: 'SENTIMENT_BELOW', label: 'Sentiment Below' },
    { value: 'SENTIMENT_CHANGE', label: 'Sentiment Change' },
    { value: 'NEWS_VOLUME_SPIKE', label: 'News Volume Spike' },
  ]

  const [alertType, setAlertType] = useState<'price' | 'sentiment'>('price')
  const conditions = alertType === 'price' ? priceConditions : sentimentConditions

  const handleAlertTypeChange = (type: 'price' | 'sentiment') => {
    setAlertType(type)
    setFormData((prev) => ({
      ...prev,
      condition: type === 'price' ? 'PRICE_ABOVE' : 'SENTIMENT_ABOVE',
    }))
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create New Alert">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Alert Type Selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Alert Type</label>
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => handleAlertTypeChange('price')}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                alertType === 'price'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              Price Alert
            </button>
            <button
              type="button"
              onClick={() => handleAlertTypeChange('sentiment')}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                alertType === 'sentiment'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              News/Sentiment Alert
            </button>
          </div>
        </div>

        {/* Symbol */}
        <div>
          <label htmlFor="symbol" className="block text-sm font-medium text-gray-700 mb-1">
            Stock Symbol *
          </label>
          <input
            type="text"
            id="symbol"
            name="symbol"
            value={formData.symbol}
            onChange={handleChange}
            placeholder="e.g., AAPL"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 uppercase"
          />
        </div>

        {/* Condition */}
        <div>
          <label htmlFor="condition" className="block text-sm font-medium text-gray-700 mb-1">
            Condition *
          </label>
          <select
            id="condition"
            name="condition"
            value={formData.condition}
            onChange={handleChange}
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            {conditions.map((cond) => (
              <option key={cond.value} value={cond.value}>
                {cond.label}
              </option>
            ))}
          </select>
        </div>

        {/* Threshold Value */}
        <div>
          <label htmlFor="threshold_value" className="block text-sm font-medium text-gray-700 mb-1">
            Threshold Value *
          </label>
          <input
            type="number"
            id="threshold_value"
            name="threshold_value"
            value={formData.threshold_value}
            onChange={handleChange}
            placeholder={
              formData.condition.includes('PERCENT') || formData.condition.includes('SENTIMENT')
                ? 'e.g., 0.75'
                : 'e.g., 150.00'
            }
            step={
              formData.condition.includes('PERCENT') || formData.condition.includes('SENTIMENT')
                ? '0.001'
                : '0.01'
            }
            min="0"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          <p className="text-xs text-gray-500 mt-1">
            {formData.condition.includes('PERCENT')
              ? 'Percentage change (e.g., 5 for 5%)'
              : formData.condition.includes('SENTIMENT')
              ? 'Sentiment score between 0 and 1'
              : 'Dollar amount'}
          </p>
        </div>

        {/* Message (Optional) */}
        <div>
          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-1">
            Message (Optional)
          </label>
          <textarea
            id="message"
            name="message"
            value={formData.message}
            onChange={handleChange}
            placeholder="Custom message for this alert"
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {createMutation.error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            Failed to create alert. Please try again.
          </div>
        )}

        <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
          <button
            type="button"
            onClick={onClose}
            className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createMutation.isPending}
            className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {createMutation.isPending ? 'Creating...' : 'Create Alert'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
