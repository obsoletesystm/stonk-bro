import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { Search, TrendingUp, TrendingDown, ArrowRight, BarChart3 } from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import { searchStocks, getStockQuote } from '../lib/api'
import type { StockSearchResult, StockQuote } from '../types'

export default function StockSearch() {
  const navigate = useNavigate()
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')

  // Debounce search input
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(searchQuery)
    }, 300)

    return () => clearTimeout(timer)
  }, [searchQuery])

  const { data: searchResults, isLoading: isSearching } = useQuery({
    queryKey: ['stock-search', debouncedQuery],
    queryFn: async () => {
      if (!debouncedQuery || debouncedQuery.length < 1) return []
      const res = await searchStocks(debouncedQuery)
      return res.data
    },
    enabled: debouncedQuery.length >= 1,
  })

  const results: StockSearchResult[] = searchResults || []

  const popularStocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'BRK.B']

  const handleStockClick = (symbol: string) => {
    navigate(`/stock/${symbol}`)
  }

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value)
  }

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Stock Search</h1>
        <p className="text-gray-600 mt-2">Search for stocks to view details, predictions, and sentiment</p>
      </div>

      {/* Search Input */}
      <div className="mb-8">
        <div className="relative max-w-2xl">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="w-5 h-5 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchQuery}
            onChange={handleSearchChange}
            placeholder="Search by symbol or company name (e.g., AAPL or Apple)"
            className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      {/* Search Results */}
      {searchQuery && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Search Results</h2>
          {isSearching ? (
            <div className="py-8">
              <Loader />
            </div>
          ) : results.length === 0 ? (
            <Card>
              <div className="text-center py-12">
                <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No results found</h3>
                <p className="text-gray-600">Try searching with a different symbol or company name</p>
              </div>
            </Card>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((stock) => (
                <StockResultCard
                  key={stock.symbol}
                  stock={stock}
                  onClick={() => handleStockClick(stock.symbol)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Popular Stocks */}
      {!searchQuery && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Popular Stocks</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {popularStocks.map((symbol) => (
              <PopularStockCard
                key={symbol}
                symbol={symbol}
                onClick={() => handleStockClick(symbol)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

interface StockResultCardProps {
  stock: StockSearchResult
  onClick: () => void
}

function StockResultCard({ stock, onClick }: StockResultCardProps) {
  return (
    <button
      onClick={onClick}
      className="bg-white rounded-lg border border-gray-200 p-6 hover:border-primary-500 hover:shadow-md transition-all text-left group"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
            {stock.symbol}
          </h3>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{stock.name}</p>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all flex-shrink-0 ml-2" />
      </div>
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">{stock.exchange}</span>
        {stock.type && (
          <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
            {stock.type}
          </span>
        )}
      </div>
    </button>
  )
}

interface PopularStockCardProps {
  symbol: string
  onClick: () => void
}

function PopularStockCard({ symbol, onClick }: PopularStockCardProps) {
  const { data: quoteData, isLoading } = useQuery({
    queryKey: ['stock-quote', symbol],
    queryFn: async () => {
      const res = await getStockQuote(symbol)
      return res.data
    },
  })

  const quote: StockQuote | undefined = quoteData

  return (
    <button
      onClick={onClick}
      className="bg-white rounded-lg border border-gray-200 p-6 hover:border-primary-500 hover:shadow-md transition-all text-left group"
    >
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : quote ? (
        <>
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                {symbol}
              </h3>
              <p className="text-sm text-gray-600 mt-1 line-clamp-1">{quote.name}</p>
            </div>
            <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-1 transition-all flex-shrink-0 ml-2" />
          </div>

          <div className="flex items-end justify-between">
            <div>
              <p className="text-2xl font-bold text-gray-900">${quote.price.toFixed(2)}</p>
              <div className="flex items-center mt-1">
                {quote.change >= 0 ? (
                  <TrendingUp className="w-4 h-4 text-green-600 mr-1" />
                ) : (
                  <TrendingDown className="w-4 h-4 text-red-600 mr-1" />
                )}
                <span
                  className={`text-sm font-medium ${
                    quote.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {quote.change >= 0 ? '+' : ''}
                  {quote.change.toFixed(2)} ({quote.change >= 0 ? '+' : ''}
                  {quote.change_percent.toFixed(2)}%)
                </span>
              </div>
            </div>
            <BarChart3 className="w-6 h-6 text-gray-400" />
          </div>
        </>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-500 text-sm">Unable to load quote</p>
        </div>
      )}
    </button>
  )
}
