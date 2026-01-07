import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Plus, TrendingUp, TrendingDown, DollarSign, Percent, BarChart3 } from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import AddHoldingModal from '../components/AddHoldingModal'
import { getPortfolios, getHoldings } from '../lib/api'
import type { Portfolio, Holding } from '../types'

export default function Portfolio() {
  const [selectedPortfolio, setSelectedPortfolio] = useState<number | null>(null)
  const [isAddHoldingModalOpen, setIsAddHoldingModalOpen] = useState(false)

  const { data: portfoliosData, isLoading } = useQuery({
    queryKey: ['portfolios'],
    queryFn: async () => {
      const res = await getPortfolios()
      return res.data
    },
  })

  const portfolios: Portfolio[] = portfoliosData || []
  const portfolio = selectedPortfolio
    ? portfolios.find((p) => p.id === selectedPortfolio)
    : portfolios[0]

  const { data: holdingsData } = useQuery({
    queryKey: ['holdings', portfolio?.id],
    queryFn: async () => {
      if (!portfolio?.id) return []
      const res = await getHoldings(portfolio.id)
      return res.data
    },
    enabled: !!portfolio?.id,
  })

  const holdings: Holding[] = holdingsData || []

  if (isLoading) return <Loader />

  if (portfolios.length === 0) {
    return (
      <div className="p-8">
        <div className="text-center py-12">
          <BarChart3 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No portfolios yet</h3>
          <p className="text-gray-600 mb-6">Create your first portfolio to start tracking your investments</p>
          <button className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2">
            <Plus className="w-5 h-5" />
            <span>Create Portfolio</span>
          </button>
        </div>
      </div>
    )
  }

  const totalValue = holdings.reduce((sum, h) => sum + (h.market_value || 0), 0)
  const totalCost = holdings.reduce((sum, h) => sum + (h.total_cost || 0), 0)
  const totalGain = totalValue - totalCost
  const totalGainPercent = totalCost > 0 ? (totalGain / totalCost) * 100 : 0

  const gainers = holdings.filter((h) => (h.unrealized_gain || 0) > 0).length
  const losers = holdings.filter((h) => (h.unrealized_gain || 0) < 0).length

  return (
    <div className="p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Portfolio</h1>
          <p className="text-gray-600 mt-2">Track your holdings and performance</p>
        </div>
        <button
          onClick={() => setIsAddHoldingModalOpen(true)}
          className="px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Add Holding</span>
        </button>
      </div>

      {/* Portfolio Selector */}
      {portfolios.length > 1 && (
        <div className="mb-6">
          <select
            value={portfolio?.id || ''}
            onChange={(e) => setSelectedPortfolio(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            {portfolios.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Value</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-primary-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Gain/Loss</p>
              <p className={`text-2xl font-bold mt-1 ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalGain >= 0 ? '+' : ''}${totalGain.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </p>
              <p className={`text-sm mt-1 ${totalGain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {totalGain >= 0 ? '+' : ''}{totalGainPercent.toFixed(2)}%
              </p>
            </div>
            {totalGain >= 0 ? (
              <TrendingUp className="w-8 h-8 text-green-600" />
            ) : (
              <TrendingDown className="w-8 h-8 text-red-600" />
            )}
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Cost</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                ${totalCost.toLocaleString('en-US', { minimumFractionDigits: 2 })}
              </p>
            </div>
            <DollarSign className="w-8 h-8 text-gray-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Holdings</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{holdings.length}</p>
              <p className="text-sm text-gray-500 mt-1">
                <span className="text-green-600">{gainers}↑</span> /{' '}
                <span className="text-red-600">{losers}↓</span>
              </p>
            </div>
            <Percent className="w-8 h-8 text-primary-600" />
          </div>
        </Card>
      </div>

      {/* Holdings Table */}
      <Card title="Holdings" subtitle="Current portfolio positions">
        {holdings.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No holdings in this portfolio</p>
            <button
              onClick={() => setIsAddHoldingModalOpen(true)}
              className="mt-4 px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors"
            >
              Add Your First Holding
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold text-gray-700">Symbol</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Shares</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Avg Cost</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Current Price</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Market Value</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Total Cost</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Gain/Loss</th>
                  <th className="text-right py-3 px-4 font-semibold text-gray-700">Return %</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => (
                  <tr
                    key={holding.id}
                    className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                  >
                    <td className="py-4 px-4">
                      <button className="font-semibold text-primary-600 hover:text-primary-700">
                        {holding.symbol}
                      </button>
                    </td>
                    <td className="py-4 px-4 text-right text-gray-900">
                      {holding.shares.toLocaleString()}
                    </td>
                    <td className="py-4 px-4 text-right text-gray-900">
                      ${holding.average_cost.toFixed(2)}
                    </td>
                    <td className="py-4 px-4 text-right text-gray-900">
                      ${holding.current_price?.toFixed(2) || '-'}
                    </td>
                    <td className="py-4 px-4 text-right font-medium text-gray-900">
                      ${holding.market_value?.toLocaleString('en-US', { minimumFractionDigits: 2 }) || '-'}
                    </td>
                    <td className="py-4 px-4 text-right text-gray-600">
                      ${holding.total_cost?.toLocaleString('en-US', { minimumFractionDigits: 2 }) || '-'}
                    </td>
                    <td
                      className={`py-4 px-4 text-right font-medium ${
                        (holding.unrealized_gain || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {(holding.unrealized_gain || 0) >= 0 ? '+' : ''}$
                      {holding.unrealized_gain?.toLocaleString('en-US', { minimumFractionDigits: 2 }) || '-'}
                    </td>
                    <td
                      className={`py-4 px-4 text-right font-semibold ${
                        (holding.unrealized_gain_percent || 0) >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {(holding.unrealized_gain_percent || 0) >= 0 ? '+' : ''}
                      {holding.unrealized_gain_percent?.toFixed(2) || '-'}%
                    </td>
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-gray-300 font-semibold">
                  <td className="py-4 px-4 text-gray-900">TOTAL</td>
                  <td className="py-4 px-4"></td>
                  <td className="py-4 px-4"></td>
                  <td className="py-4 px-4"></td>
                  <td className="py-4 px-4 text-right text-gray-900">
                    ${totalValue.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-4 text-right text-gray-900">
                    ${totalCost.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td
                    className={`py-4 px-4 text-right ${
                      totalGain >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {totalGain >= 0 ? '+' : ''}${totalGain.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </td>
                  <td
                    className={`py-4 px-4 text-right ${
                      totalGainPercent >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {totalGainPercent >= 0 ? '+' : ''}{totalGainPercent.toFixed(2)}%
                  </td>
                </tr>
              </tfoot>
            </table>
          </div>
        )}
      </Card>

      {/* Add Holding Modal */}
      {portfolio && (
        <AddHoldingModal
          isOpen={isAddHoldingModalOpen}
          onClose={() => setIsAddHoldingModalOpen(false)}
          portfolioId={portfolio.id}
        />
      )}
    </div>
  )
}
