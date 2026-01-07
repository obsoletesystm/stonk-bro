export interface Portfolio {
  id: number
  name: string
  description?: string
  created_at: string
  total_value?: number
  total_cost?: number
  total_return?: number
  total_return_percent?: number
}

export interface Holding {
  id: number
  portfolio_id: number
  symbol: string
  shares: number
  average_cost: number
  current_price?: number
  market_value?: number
  total_cost?: number
  unrealized_gain?: number
  unrealized_gain_percent?: number
}

export interface StockQuote {
  symbol: string
  name: string
  price: number
  change: number
  change_percent: number
  volume: number
  market_cap?: number
  pe_ratio?: number
  dividend_yield?: number
}

export interface Alert {
  id: number
  symbol: string
  condition: string
  threshold_value: number
  status: string
  message?: string
  created_at: string
  triggered_at?: string
}

export interface AlertHistory {
  id: number
  alert_id: number
  triggered_at: string
  price_at_trigger?: number
  sentiment_at_trigger?: number
  articles_count?: number
  trigger_details?: string
  notification_sent: boolean
}

export interface NewsArticle {
  id: number
  title: string
  description: string
  url: string
  published_at: string
  source: string
  symbols: string[]
  sentiment_score?: number
  sentiment_label?: string
}

export interface SentimentSummary {
  symbol: string
  avg_sentiment: number
  total_articles: number
  positive_count: number
  neutral_count: number
  negative_count: number
  sentiment_trend?: string
}

export interface Prediction {
  symbol: string
  model_type: string
  prediction_date: string
  predicted_price: number
  confidence_lower: number
  confidence_upper: number
  accuracy_score?: number
}

export interface StockSearchResult {
  symbol: string
  name: string
  exchange: string
  type?: string
}
