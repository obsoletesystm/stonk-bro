import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import Modal from './Modal'
import { createHolding } from '../lib/api'

interface AddHoldingModalProps {
  isOpen: boolean
  onClose: () => void
  portfolioId: number
}

export default function AddHoldingModal({ isOpen, onClose, portfolioId }: AddHoldingModalProps) {
  const queryClient = useQueryClient()
  const [formData, setFormData] = useState({
    symbol: '',
    shares: '',
    average_cost: '',
    purchase_date: new Date().toISOString().split('T')[0],
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => createHolding(portfolioId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['holdings', portfolioId] })
      queryClient.invalidateQueries({ queryKey: ['portfolios'] })
      onClose()
      setFormData({
        symbol: '',
        shares: '',
        average_cost: '',
        purchase_date: new Date().toISOString().split('T')[0],
      })
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate({
      symbol: formData.symbol.toUpperCase(),
      shares: parseFloat(formData.shares),
      average_cost: parseFloat(formData.average_cost),
      purchase_date: formData.purchase_date,
    })
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add New Holding">
      <form onSubmit={handleSubmit} className="space-y-4">
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

        <div>
          <label htmlFor="shares" className="block text-sm font-medium text-gray-700 mb-1">
            Number of Shares *
          </label>
          <input
            type="number"
            id="shares"
            name="shares"
            value={formData.shares}
            onChange={handleChange}
            placeholder="e.g., 100"
            step="0.001"
            min="0"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label htmlFor="average_cost" className="block text-sm font-medium text-gray-700 mb-1">
            Average Cost per Share *
          </label>
          <input
            type="number"
            id="average_cost"
            name="average_cost"
            value={formData.average_cost}
            onChange={handleChange}
            placeholder="e.g., 150.50"
            step="0.01"
            min="0"
            required
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        <div>
          <label htmlFor="purchase_date" className="block text-sm font-medium text-gray-700 mb-1">
            Purchase Date
          </label>
          <input
            type="date"
            id="purchase_date"
            name="purchase_date"
            value={formData.purchase_date}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>

        {createMutation.error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            Failed to add holding. Please try again.
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
            {createMutation.isPending ? 'Adding...' : 'Add Holding'}
          </button>
        </div>
      </form>
    </Modal>
  )
}
