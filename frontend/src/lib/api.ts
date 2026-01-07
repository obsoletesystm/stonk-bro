import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Health check
export const getHealth = () => api.get('/health/detailed')

// Portfolio endpoints
export const getPortfolios = () => api.get('/portfolios')
export const getPortfolio = (id: number) => api.get(`/portfolios/${id}`)
export const createPortfolio = (data: any) => api.post('/portfolios', data)
export const updatePortfolio = (id: number, data: any) => api.put(`/portfolios/${id}`, data)
export const deletePortfolio = (id: number) => api.delete(`/portfolios/${id}`)

// Holdings endpoints
export const getHoldings = (portfolioId: number) => api.get(`/portfolios/${portfolioId}/holdings`)
export const createHolding = (portfolioId: number, data: any) =>
  api.post(`/portfolios/${portfolioId}/holdings`, data)
export const updateHolding = (portfolioId: number, holdingId: number, data: any) =>
  api.put(`/portfolios/${portfolioId}/holdings/${holdingId}`, data)
export const deleteHolding = (portfolioId: number, holdingId: number) =>
  api.delete(`/portfolios/${portfolioId}/holdings/${holdingId}`)

// Stock endpoints
export const searchStocks = (query: string) => api.get(`/stocks/search/${query}`)
export const getStockQuote = (symbol: string) => api.get(`/stocks/quote/${symbol}`)
export const getStockHistory = (symbol: string, period = '1mo') =>
  api.get(`/stocks/history/${symbol}`, { params: { period } })
export const getStockPrediction = (symbol: string) => api.get(`/predictions/${symbol}`)

// Alert endpoints
export const getAlerts = () => api.get('/alerts')
export const createAlert = (data: any) => api.post('/alerts', data)
export const deleteAlert = (id: number) => api.delete(`/alerts/${id}`)
export const getAlertHistory = (id: number) => api.get(`/alerts/${id}/history`)

// News endpoints
export const getNews = (params?: any) => api.get('/news', { params })
export const getNewsSentiment = (symbol: string) => api.get(`/news/${symbol}/sentiment`)

// TFSA endpoints
export const getTFSARoom = (birthYear: number) =>
  api.get(`/tfsa/contribution-room/${birthYear}`)

export default api
