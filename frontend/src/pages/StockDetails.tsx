import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Activity,
  Building2,
  Percent,
  Plus,
  Bell,
  Calendar,
  Target,
  Newspaper,
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import Card from '../components/Card'
import Loader from '../components/Loader'
import CreateAlertModal from '../components/CreateAlertModal'
import AddHoldingModal from '../components/AddHoldingModal'
import { getStockQuote, getStockHistory, getStockPrediction, getNewsSentiment } from '../lib/api'
import type { StockQuote, Prediction, SentimentSummary } from '../types'
import { format } from 'date-fns'

export default function StockDetails() {
  const { symbol } = useParams<{ symbol: string }>()
  const navigate = useNavigate()
  const [period, setPeriod] = useState('1mo')
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false)
  const [isAddHoldingModalOpen, setIsAddHoldingModalOpen] = useState(false)

  const { data: quoteData, isLoading: isLoadingQuote } = useQuery({
    queryKey: ['stock-quote', symbol],
    queryFn: async () => {
      if (!symbol) return null
      const res = await getStockQuote(symbol)
      return res.data
    },
    enabled: !!symbol,
  })

  const { data: historyData, isLoading: isLoadingHistory } = useQuery({
    queryKey: ['stock-history', symbol, period],
    queryFn: async () => {
      if (!symbol) return []
      const res = await getStockHistory(symbol, period)
      return res.data
    },
    enabled: !!symbol,
  })

  const { data: predictionData, isLoading: isLoadingPrediction } = useQuery({
    queryKey: ['stock-prediction', symbol],
    queryFn: async () => {
      if (!symbol) return null
      const res = await getStockPrediction(symbol)
      return res.data
    },
    enabled: !!symbol,
  })

  const { data: sentimentData, isLoading: isLoadingSentiment } = useQuery({
    queryKey: ['news-sentiment', symbol],
    queryFn: async () => {
      if (!symbol) return null
      const res = await getNewsSentiment(symbol)
      return res.data
    },
    enabled: !!symbol,
  })

  const quote: StockQuote | null = quoteData || null
  const history: any[] = historyData || []
  const prediction: Prediction | null = predictionData || null
  const sentiment: SentimentSummary | null = sentimentData || null

  if (!symbol) {
    return (
      <div className="p-8">
        <p className="text-gray-600">Invalid stock symbol</p>
      </div>
    )
  }

  if (isLoadingQuote) return <Loader />

  if (!quote) {
    return (
      <div className="p-8">
        <button
          onClick={() => navigate('/search')}
          className="mb-6 inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Search</span>
        </button>
        <div className="text-center py-12">
          <p className="text-gray-600">Unable to load stock data for {symbol}</p>
        </div>
      </div>
    )
  }

  const chartData = history.map((item) => ({
    date: format(new Date(item.date), 'MMM d'),
    price: item.close,
  }))

  const getSentimentLabel = (score: number) => {
    if (score >= 0.6) return { label: 'Positive', color: 'text-green-600', bg: 'bg-green-100' }
    if (score >= 0.4) return { label: 'Neutral', color: 'text-gray-600', bg: 'bg-gray-100' }
    return { label: 'Negative', color: 'text-red-600', bg: 'bg-red-100' }
  }

  return (
    <div className="p-8">
      {/* Back Button */}
      <button
        onClick={() => navigate('/search')}
        className="mb-6 inline-flex items-center space-x-2 text-primary-600 hover:text-primary-700"
      >
        <ArrowLeft className="w-4 h-4" />
        <span>Back to Search</span>
      </button>

      {/* Stock Header */}
      <div className="mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-4xl font-bold text-gray-900">{symbol}</h1>
            <p className="text-xl text-gray-600 mt-2">{quote.name}</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={() => setIsAddHoldingModalOpen(true)}
              className="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors inline-flex items-center space-x-2"
            >
              <Plus className="w-4 h-4" />
              <span>Add to Portfolio</span>
            </button>
            <button
              onClick={() => setIsAlertModalOpen(true)}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
            >
              <Bell className="w-4 h-4" />
              <span>Create Alert</span>
            </button>
          </div>
        </div>

        {/* Price Info */}
        <div className="mt-6 flex items-end space-x-4">
          <div className="text-5xl font-bold text-gray-900">${quote.price.toFixed(2)}</div>
          <div className="flex items-center pb-2">
            {quote.change >= 0 ? (
              <TrendingUp className="w-6 h-6 text-green-600 mr-2" />
            ) : (
              <TrendingDown className="w-6 h-6 text-red-600 mr-2" />
            )}
            <span
              className={`text-2xl font-semibold ${
                quote.change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}
            >
              {quote.change >= 0 ? '+' : ''}
              {quote.change.toFixed(2)} ({quote.change >= 0 ? '+' : ''}
              {quote.change_percent.toFixed(2)}%)
            </span>
          </div>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Volume</p>
              <p className="text-xl font-bold text-gray-900 mt-1">
                {quote.volume.toLocaleString()}
              </p>
            </div>
            <Activity className="w-8 h-8 text-primary-600" />
          </div>
        </Card>

        {quote.market_cap && (
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Market Cap</p>
                <p className="text-xl font-bold text-gray-900 mt-1">
                  ${(quote.market_cap / 1e9).toFixed(2)}B
                </p>
              </div>
              <Building2 className="w-8 h-8 text-primary-600" />
            </div>
          </Card>
        )}

        {quote.pe_ratio && (
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">P/E Ratio</p>
                <p className="text-xl font-bold text-gray-900 mt-1">{quote.pe_ratio.toFixed(2)}</p>
              </div>
              <DollarSign className="w-8 h-8 text-primary-600" />
            </div>
          </Card>
        )}

        {quote.dividend_yield && (
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Dividend Yield</p>
                <p className="text-xl font-bold text-gray-900 mt-1">
                  {(quote.dividend_yield * 100).toFixed(2)}%
                </p>
              </div>
              <Percent className="w-8 h-8 text-primary-600" />
            </div>
          </Card>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
        {/* Price Chart */}
        <div className="lg:col-span-2">
          <Card title="Price History">
            {/* Period Selector */}
            <div className="mb-6 flex items-center space-x-2">
              {['1d', '5d', '1mo', '3mo', '6mo', '1y'].map((p) => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                    period === p
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {p.toUpperCase()}
                </button>
              ))}
            </div>

            {isLoadingHistory ? (
              <div className="py-12">
                <Loader />
              </div>
            ) : chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis
                    dataKey="date"
                    stroke="#9ca3af"
                    style={{ fontSize: '12px' }}
                  />
                  <YAxis
                    stroke="#9ca3af"
                    style={{ fontSize: '12px' }}
                    domain={['auto', 'auto']}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#fff',
                      border: '1px solid #e5e7eb',
                      borderRadius: '8px',
                    }}
                    formatter={(value: any) => [`$${value.toFixed(2)}`, 'Price']}
                  />
                  <Line
                    type="monotone"
                    dataKey="price"
                    stroke="#2563eb"
                    strokeWidth={2}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center py-12">
                <p className="text-gray-500">No historical data available</p>
              </div>
            )}
          </Card>
        </div>

        {/* AI Predictions */}
        <div>
          <Card title="AI Prediction">
            {isLoadingPrediction ? (
              <div className="py-12">
                <Loader />
              </div>
            ) : prediction ? (
              <div className="space-y-4">
                <div className="text-center p-6 bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg">
                  <div className="flex items-center justify-center mb-2">
                    <Target className="w-6 h-6 text-primary-600 mr-2" />
                    <span className="text-sm font-medium text-primary-900">
                      {prediction.model_type}
                    </span>
                  </div>
                  <p className="text-3xl font-bold text-primary-900">
                    ${prediction.predicted_price.toFixed(2)}
                  </p>
                  <p className="text-sm text-primary-700 mt-1">
                    {format(new Date(prediction.prediction_date), 'MMM d, yyyy')}
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Confidence Range</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">
                      ${prediction.confidence_lower.toFixed(2)}
                    </span>
                    <span className="text-xs text-gray-500">to</span>
                    <span className="text-sm font-medium text-gray-900">
                      ${prediction.confidence_upper.toFixed(2)}
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{
                        width: `${
                          ((prediction.predicted_price - prediction.confidence_lower) /
                            (prediction.confidence_upper - prediction.confidence_lower)) *
                          100
                        }%`,
                      }}
                    />
                  </div>
                </div>

                {prediction.accuracy_score && (
                  <div className="pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">Model Accuracy</span>
                      <span className="text-sm font-semibold text-gray-900">
                        {(prediction.accuracy_score * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                )}

                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Potential Change</span>
                    <span
                      className={`text-sm font-semibold ${
                        prediction.predicted_price >= quote.price
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {prediction.predicted_price >= quote.price ? '+' : ''}
                      {(
                        ((prediction.predicted_price - quote.price) / quote.price) *
                        100
                      ).toFixed(2)}
                      %
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500 text-sm">No prediction available</p>
              </div>
            )}
          </Card>
        </div>
      </div>

      {/* News & Sentiment */}
      <Card title="News & Sentiment">
        {isLoadingSentiment ? (
          <div className="py-12">
            <Loader />
          </div>
        ) : sentiment ? (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Newspaper className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">{sentiment.total_articles}</p>
                <p className="text-sm text-gray-600">Total Articles</p>
              </div>

              <div className="text-center p-4 bg-green-50 rounded-lg">
                <TrendingUp className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-green-900">{sentiment.positive_count}</p>
                <p className="text-sm text-green-700">Positive</p>
              </div>

              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <Activity className="w-8 h-8 text-gray-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-gray-900">{sentiment.neutral_count}</p>
                <p className="text-sm text-gray-600">Neutral</p>
              </div>

              <div className="text-center p-4 bg-red-50 rounded-lg">
                <TrendingDown className="w-8 h-8 text-red-600 mx-auto mb-2" />
                <p className="text-2xl font-bold text-red-900">{sentiment.negative_count}</p>
                <p className="text-sm text-red-700">Negative</p>
              </div>
            </div>

            <div className="flex items-center justify-between p-6 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-200">
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">Average Sentiment</p>
                <div className="flex items-center space-x-3">
                  <span className="text-3xl font-bold text-gray-900">
                    {sentiment.avg_sentiment.toFixed(3)}
                  </span>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      getSentimentLabel(sentiment.avg_sentiment).bg
                    } ${getSentimentLabel(sentiment.avg_sentiment).color}`}
                  >
                    {getSentimentLabel(sentiment.avg_sentiment).label}
                  </span>
                </div>
              </div>
              {sentiment.sentiment_trend && (
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-600 mb-1">Trend</p>
                  <p className="text-lg font-semibold text-gray-900 capitalize">
                    {sentiment.sentiment_trend}
                  </p>
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="text-center py-12">
            <Newspaper className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">No sentiment data available</p>
          </div>
        )}
      </Card>

      {/* Modals */}
      <CreateAlertModal isOpen={isAlertModalOpen} onClose={() => setIsAlertModalOpen(false)} />

      <AddHoldingModal
        isOpen={isAddHoldingModalOpen}
        onClose={() => setIsAddHoldingModalOpen(false)}
        portfolioId={1}
      />
    </div>
  )
}
