import { useQuery } from '@tanstack/react-query'
import { TrendingUp, TrendingDown, DollarSign, Bell, Newspaper } from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import { getHealth, getPortfolios, getAlerts, getNews } from '../lib/api'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  const { data: healthData, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await getHealth()
      return res.data
    },
  })

  const { data: portfoliosData } = useQuery({
    queryKey: ['portfolios'],
    queryFn: async () => {
      const res = await getPortfolios()
      return res.data
    },
  })

  const { data: alertsData } = useQuery({
    queryKey: ['alerts'],
    queryFn: async () => {
      const res = await getAlerts()
      return res.data
    },
  })

  const { data: newsData } = useQuery({
    queryKey: ['news'],
    queryFn: async () => {
      const res = await getNews({ limit: 5 })
      return res.data
    },
  })

  if (healthLoading) return <Loader />

  const portfolios = portfoliosData || []
  const alerts = alertsData || []
  const news = newsData?.articles || []

  const totalValue = portfolios.reduce((sum: number, p: any) => sum + (p.total_value || 0), 0)
  const totalGain = portfolios.reduce((sum: number, p: any) => sum + (p.total_return || 0), 0)
  const totalGainPercent = portfolios.reduce((sum: number, p: any) => sum + (p.total_return_percent || 0), 0) / (portfolios.length || 1)

  const activeAlerts = alerts.filter((a: any) => a.status === 'active').length
  const triggeredAlerts = alerts.filter((a: any) => a.status === 'triggered').length

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-2">Welcome back! Here's your portfolio overview.</p>
      </div>

      {/* Overview Stats */}
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
              <p className="text-sm font-medium text-gray-600">Active Alerts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{activeAlerts}</p>
              {triggeredAlerts > 0 && (
                <p className="text-sm text-orange-600 mt-1">{triggeredAlerts} triggered</p>
              )}
            </div>
            <Bell className="w-8 h-8 text-primary-600" />
          </div>
        </Card>

        <Card>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Recent News</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{news.length}</p>
              <p className="text-sm text-gray-500 mt-1">articles</p>
            </div>
            <Newspaper className="w-8 h-8 text-primary-600" />
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Status */}
        <Card title="System Status">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Database</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                healthData?.database === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {healthData?.database || 'Unknown'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Redis Cache</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                healthData?.redis === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {healthData?.redis || 'Unknown'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-600">Celery Worker</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                healthData?.celery === 'healthy' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {healthData?.celery || 'Unknown'}
              </span>
            </div>
          </div>
        </Card>

        {/* Recent Alerts */}
        <Card
          title="Recent Alerts"
          action={
            <Link to="/alerts" className="text-sm font-medium text-primary-600 hover:text-primary-700">
              View all →
            </Link>
          }
        >
          {alerts.length === 0 ? (
            <p className="text-gray-500 text-sm">No alerts configured yet</p>
          ) : (
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert: any) => (
                <div key={alert.id} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                  <div>
                    <p className="font-medium text-gray-900">{alert.symbol}</p>
                    <p className="text-sm text-gray-500">{alert.condition}</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    alert.status === 'active' ? 'bg-blue-100 text-blue-800' :
                    alert.status === 'triggered' ? 'bg-orange-100 text-orange-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {alert.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  )
}
