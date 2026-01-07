import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Newspaper, Search, TrendingUp, TrendingDown, Activity, ExternalLink, Calendar } from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import { getNews } from '../lib/api'
import type { NewsArticle } from '../types'
import { format } from 'date-fns'

export default function News() {
  const [symbolFilter, setSymbolFilter] = useState('')
  const [sentimentFilter, setSentimentFilter] = useState<'all' | 'positive' | 'neutral' | 'negative'>('all')
  const [page, setPage] = useState(1)
  const limit = 20

  const { data: newsData, isLoading } = useQuery({
    queryKey: ['news', symbolFilter, sentimentFilter, page],
    queryFn: async () => {
      const params: any = {
        limit,
        offset: (page - 1) * limit,
      }

      if (symbolFilter) {
        params.symbol = symbolFilter.toUpperCase()
      }

      if (sentimentFilter !== 'all') {
        params.sentiment = sentimentFilter
      }

      const res = await getNews(params)
      return res.data
    },
  })

  const articles: NewsArticle[] = newsData?.articles || []
  const total = newsData?.total || 0

  const getSentimentLabel = (score?: number) => {
    if (!score && score !== 0) return { label: 'Unknown', color: 'text-gray-600', bg: 'bg-gray-100' }
    if (score >= 0.6) return { label: 'Positive', color: 'text-green-600', bg: 'bg-green-100', icon: TrendingUp }
    if (score >= 0.4) return { label: 'Neutral', color: 'text-gray-600', bg: 'bg-gray-100', icon: Activity }
    return { label: 'Negative', color: 'text-red-600', bg: 'bg-red-100', icon: TrendingDown }
  }

  const handleSymbolSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
  }

  const handleSentimentFilter = (filter: 'all' | 'positive' | 'neutral' | 'negative') => {
    setSentimentFilter(filter)
    setPage(1)
  }

  const positiveCount = articles.filter(a => (a.sentiment_score || 0) >= 0.6).length
  const neutralCount = articles.filter(a => (a.sentiment_score || 0) >= 0.4 && (a.sentiment_score || 0) < 0.6).length
  const negativeCount = articles.filter(a => (a.sentiment_score || 0) < 0.4).length

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">News & Sentiment</h1>
        <p className="text-gray-600 mt-2">Latest market news with AI-powered sentiment analysis</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Articles</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{total}</p>
            </div>
            <Newspaper className="w-8 h-8 text-primary-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Positive</p>
              <p className="text-2xl font-bold text-green-600 mt-1">{positiveCount}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-green-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Neutral</p>
              <p className="text-2xl font-bold text-gray-600 mt-1">{neutralCount}</p>
            </div>
            <Activity className="w-8 h-8 text-gray-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Negative</p>
              <p className="text-2xl font-bold text-red-600 mt-1">{negativeCount}</p>
            </div>
            <TrendingDown className="w-8 h-8 text-red-600" />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="mb-6 space-y-4">
        {/* Symbol Search */}
        <form onSubmit={handleSymbolSearch} className="max-w-md">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="w-5 h-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={symbolFilter}
              onChange={(e) => setSymbolFilter(e.target.value)}
              placeholder="Filter by symbol (e.g., AAPL)"
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </form>

        {/* Sentiment Filter */}
        <div className="flex items-center space-x-2">
          <span className="text-sm font-medium text-gray-700">Sentiment:</span>
          {(['all', 'positive', 'neutral', 'negative'] as const).map((filter) => (
            <button
              key={filter}
              onClick={() => handleSentimentFilter(filter)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                sentimentFilter === filter
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {filter.charAt(0).toUpperCase() + filter.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* News Articles */}
      {isLoading ? (
        <div className="py-12">
          <Loader />
        </div>
      ) : articles.length === 0 ? (
        <Card>
          <div className="text-center py-12">
            <Newspaper className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No articles found</h3>
            <p className="text-gray-600">
              {symbolFilter
                ? `No news articles found for ${symbolFilter}`
                : 'No news articles available at this time'}
            </p>
          </div>
        </Card>
      ) : (
        <div className="space-y-4">
          {articles.map((article) => (
            <NewsArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-8 flex items-center justify-center space-x-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="flex items-center space-x-1">
            {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
              let pageNum
              if (totalPages <= 5) {
                pageNum = i + 1
              } else if (page <= 3) {
                pageNum = i + 1
              } else if (page >= totalPages - 2) {
                pageNum = totalPages - 4 + i
              } else {
                pageNum = page - 2 + i
              }

              return (
                <button
                  key={pageNum}
                  onClick={() => setPage(pageNum)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    page === pageNum
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {pageNum}
                </button>
              )
            })}
          </div>

          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
}

interface NewsArticleCardProps {
  article: NewsArticle
}

function NewsArticleCard({ article }: NewsArticleCardProps) {
  const sentiment = getSentimentLabel(article.sentiment_score)
  const SentimentIcon = sentiment.icon

  return (
    <Card>
      <div className="flex items-start space-x-4">
        {/* Sentiment Indicator */}
        <div className={`flex-shrink-0 w-16 h-16 rounded-lg ${sentiment.bg} flex items-center justify-center`}>
          {SentimentIcon && <SentimentIcon className={`w-8 h-8 ${sentiment.color}`} />}
        </div>

        {/* Article Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between mb-2">
            <div className="flex-1">
              <a
                href={article.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-lg font-semibold text-gray-900 hover:text-primary-600 transition-colors group inline-flex items-start"
              >
                <span className="line-clamp-2">{article.title}</span>
                <ExternalLink className="w-4 h-4 ml-2 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
              </a>
            </div>

            {article.sentiment_score !== undefined && (
              <div className="ml-4 flex-shrink-0">
                <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${sentiment.bg} ${sentiment.color}`}>
                  {sentiment.label}
                </span>
              </div>
            )}
          </div>

          {article.description && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">{article.description}</p>
          )}

          <div className="flex items-center flex-wrap gap-4 text-sm text-gray-500">
            <div className="flex items-center space-x-1">
              <Calendar className="w-4 h-4" />
              <span>{format(new Date(article.published_at), 'MMM d, yyyy h:mm a')}</span>
            </div>

            <div className="flex items-center space-x-1">
              <Newspaper className="w-4 h-4" />
              <span>{article.source}</span>
            </div>

            {article.symbols && article.symbols.length > 0 && (
              <div className="flex items-center space-x-2">
                <span className="text-gray-400">•</span>
                <div className="flex items-center space-x-1">
                  {article.symbols.slice(0, 5).map((symbol) => (
                    <span
                      key={symbol}
                      className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-xs font-medium"
                    >
                      {symbol}
                    </span>
                  ))}
                  {article.symbols.length > 5 && (
                    <span className="text-gray-500 text-xs">+{article.symbols.length - 5} more</span>
                  )}
                </div>
              </div>
            )}

            {article.sentiment_score !== undefined && (
              <>
                <span className="text-gray-400">•</span>
                <div className="flex items-center space-x-1">
                  <span className="text-gray-500">Score:</span>
                  <span className={`font-medium ${sentiment.color}`}>
                    {article.sentiment_score.toFixed(3)}
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </Card>
  )
}
