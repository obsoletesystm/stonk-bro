import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import {
  User,
  Bell,
  Palette,
  DollarSign,
  Save,
  CheckCircle,
  AlertCircle,
  Shield,
  Calculator,
} from 'lucide-react'
import Card from '../components/Card'
import Loader from '../components/Loader'
import { getTFSARoom, getPortfolios } from '../lib/api'

export default function Settings() {
  const [activeTab, setActiveTab] = useState<'profile' | 'notifications' | 'display' | 'tfsa'>('profile')

  const tabs = [
    { id: 'profile' as const, label: 'Profile', icon: User },
    { id: 'notifications' as const, label: 'Notifications', icon: Bell },
    { id: 'display' as const, label: 'Display', icon: Palette },
    { id: 'tfsa' as const, label: 'TFSA Calculator', icon: Calculator },
  ]

  return (
    <div className="p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account and application preferences</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Tabs */}
        <div className="lg:col-span-1">
          <div className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors text-left ${
                    activeTab === tab.id
                      ? 'bg-primary-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {activeTab === 'profile' && <ProfileSettings />}
          {activeTab === 'notifications' && <NotificationSettings />}
          {activeTab === 'display' && <DisplaySettings />}
          {activeTab === 'tfsa' && <TFSASettings />}
        </div>
      </div>
    </div>
  )
}

function ProfileSettings() {
  const [formData, setFormData] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [saveSuccess, setSaveSuccess] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Simulate save
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
  }

  return (
    <div className="space-y-6">
      <Card title="Profile Information">
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              Full Name
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div className="pt-4 border-t border-gray-200">
            <button
              type="submit"
              className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
            >
              <Save className="w-4 h-4" />
              <span>Save Changes</span>
            </button>

            {saveSuccess && (
              <span className="ml-4 text-green-600 inline-flex items-center space-x-1">
                <CheckCircle className="w-4 h-4" />
                <span>Saved successfully!</span>
              </span>
            )}
          </div>
        </form>
      </Card>

      <Card title="Change Password">
        <form className="space-y-4">
          <div>
            <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-1">
              Current Password
            </label>
            <input
              type="password"
              id="currentPassword"
              name="currentPassword"
              value={formData.currentPassword}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
              New Password
            </label>
            <input
              type="password"
              id="newPassword"
              name="newPassword"
              value={formData.newPassword}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
              Confirm New Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div className="pt-4 border-t border-gray-200">
            <button
              type="submit"
              className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
            >
              <Shield className="w-4 h-4" />
              <span>Update Password</span>
            </button>
          </div>
        </form>
      </Card>
    </div>
  )
}

function NotificationSettings() {
  const [settings, setSettings] = useState({
    emailAlerts: true,
    pushAlerts: false,
    priceAlerts: true,
    sentimentAlerts: true,
    newsDigest: true,
    weeklyReport: false,
  })
  const [saveSuccess, setSaveSuccess] = useState(false)

  const handleToggle = (key: keyof typeof settings) => {
    setSettings((prev) => ({
      ...prev,
      [key]: !prev[key],
    }))
  }

  const handleSave = () => {
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
  }

  return (
    <div className="space-y-6">
      <Card title="Alert Notifications">
        <div className="space-y-4">
          <ToggleSetting
            label="Email Alerts"
            description="Receive email notifications when alerts are triggered"
            checked={settings.emailAlerts}
            onChange={() => handleToggle('emailAlerts')}
          />

          <ToggleSetting
            label="Push Notifications"
            description="Receive push notifications in your browser"
            checked={settings.pushAlerts}
            onChange={() => handleToggle('pushAlerts')}
          />

          <ToggleSetting
            label="Price Alerts"
            description="Get notified when price alerts trigger"
            checked={settings.priceAlerts}
            onChange={() => handleToggle('priceAlerts')}
          />

          <ToggleSetting
            label="Sentiment Alerts"
            description="Get notified when sentiment alerts trigger"
            checked={settings.sentimentAlerts}
            onChange={() => handleToggle('sentimentAlerts')}
          />
        </div>
      </Card>

      <Card title="Digest & Reports">
        <div className="space-y-4">
          <ToggleSetting
            label="Daily News Digest"
            description="Receive a daily summary of relevant news"
            checked={settings.newsDigest}
            onChange={() => handleToggle('newsDigest')}
          />

          <ToggleSetting
            label="Weekly Performance Report"
            description="Get a weekly report of your portfolio performance"
            checked={settings.weeklyReport}
            onChange={() => handleToggle('weeklyReport')}
          />
        </div>
      </Card>

      <div>
        <button
          onClick={handleSave}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
        >
          <Save className="w-4 h-4" />
          <span>Save Preferences</span>
        </button>

        {saveSuccess && (
          <span className="ml-4 text-green-600 inline-flex items-center space-x-1">
            <CheckCircle className="w-4 h-4" />
            <span>Saved successfully!</span>
          </span>
        )}
      </div>
    </div>
  )
}

function DisplaySettings() {
  const { data: portfoliosData } = useQuery({
    queryKey: ['portfolios'],
    queryFn: async () => {
      const res = await getPortfolios()
      return res.data
    },
  })

  const portfolios = portfoliosData || []

  const [settings, setSettings] = useState({
    defaultPortfolio: '1',
    currency: 'USD',
    dateFormat: 'MMM d, yyyy',
    chartType: 'line',
    theme: 'light',
  })
  const [saveSuccess, setSaveSuccess] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSettings((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }))
  }

  const handleSave = () => {
    setSaveSuccess(true)
    setTimeout(() => setSaveSuccess(false), 3000)
  }

  return (
    <div className="space-y-6">
      <Card title="General Preferences">
        <div className="space-y-4">
          <div>
            <label htmlFor="defaultPortfolio" className="block text-sm font-medium text-gray-700 mb-1">
              Default Portfolio
            </label>
            <select
              id="defaultPortfolio"
              name="defaultPortfolio"
              value={settings.defaultPortfolio}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {portfolios.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name}
                </option>
              ))}
              {portfolios.length === 0 && <option value="1">My Portfolio</option>}
            </select>
            <p className="text-xs text-gray-500 mt-1">
              This portfolio will be used by default when adding holdings
            </p>
          </div>

          <div>
            <label htmlFor="currency" className="block text-sm font-medium text-gray-700 mb-1">
              Currency
            </label>
            <select
              id="currency"
              name="currency"
              value={settings.currency}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="USD">USD ($)</option>
              <option value="CAD">CAD ($)</option>
              <option value="EUR">EUR (€)</option>
              <option value="GBP">GBP (£)</option>
            </select>
          </div>

          <div>
            <label htmlFor="dateFormat" className="block text-sm font-medium text-gray-700 mb-1">
              Date Format
            </label>
            <select
              id="dateFormat"
              name="dateFormat"
              value={settings.dateFormat}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="MMM d, yyyy">Jan 1, 2024</option>
              <option value="dd/MM/yyyy">01/01/2024</option>
              <option value="MM/dd/yyyy">01/01/2024</option>
              <option value="yyyy-MM-dd">2024-01-01</option>
            </select>
          </div>
        </div>
      </Card>

      <Card title="Chart Preferences">
        <div className="space-y-4">
          <div>
            <label htmlFor="chartType" className="block text-sm font-medium text-gray-700 mb-1">
              Default Chart Type
            </label>
            <select
              id="chartType"
              name="chartType"
              value={settings.chartType}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="line">Line Chart</option>
              <option value="candlestick">Candlestick Chart</option>
              <option value="area">Area Chart</option>
            </select>
          </div>

          <div>
            <label htmlFor="theme" className="block text-sm font-medium text-gray-700 mb-1">
              Theme
            </label>
            <select
              id="theme"
              name="theme"
              value={settings.theme}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto (System)</option>
            </select>
          </div>
        </div>
      </Card>

      <div>
        <button
          onClick={handleSave}
          className="px-6 py-2 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center space-x-2"
        >
          <Save className="w-4 h-4" />
          <span>Save Preferences</span>
        </button>

        {saveSuccess && (
          <span className="ml-4 text-green-600 inline-flex items-center space-x-1">
            <CheckCircle className="w-4 h-4" />
            <span>Saved successfully!</span>
          </span>
        )}
      </div>
    </div>
  )
}

function TFSASettings() {
  const [birthYear, setBirthYear] = useState<string>('1990')
  const [hasCalculated, setHasCalculated] = useState(false)

  const { data: tfsaData, isLoading, refetch } = useQuery({
    queryKey: ['tfsa-room', birthYear],
    queryFn: async () => {
      const res = await getTFSARoom(parseInt(birthYear))
      return res.data
    },
    enabled: false,
  })

  const handleCalculate = () => {
    setHasCalculated(true)
    refetch()
  }

  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 70 }, (_, i) => currentYear - 18 - i)

  return (
    <div className="space-y-6">
      <Card title="TFSA Contribution Room Calculator">
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="font-medium text-blue-900 mb-1">About TFSA Calculator</h4>
                <p className="text-sm text-blue-800">
                  Calculate your total Tax-Free Savings Account (TFSA) contribution room based on your
                  birth year. This tool considers the annual contribution limits from the year you turned
                  18 onwards.
                </p>
              </div>
            </div>
          </div>

          <div>
            <label htmlFor="birthYear" className="block text-sm font-medium text-gray-700 mb-1">
              Birth Year *
            </label>
            <select
              id="birthYear"
              value={birthYear}
              onChange={(e) => setBirthYear(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              {years.map((year) => (
                <option key={year} value={year}>
                  {year}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleCalculate}
            className="w-full px-6 py-3 bg-primary-600 text-white rounded-lg font-medium hover:bg-primary-700 transition-colors inline-flex items-center justify-center space-x-2"
          >
            <Calculator className="w-5 h-5" />
            <span>Calculate Contribution Room</span>
          </button>
        </div>
      </Card>

      {hasCalculated && (
        <>
          {isLoading ? (
            <div className="py-12">
              <Loader />
            </div>
          ) : tfsaData ? (
            <Card title="Your TFSA Contribution Room">
              <div className="space-y-6">
                <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                  <div className="text-center">
                    <p className="text-sm font-medium text-green-800 mb-2">Total Contribution Room</p>
                    <p className="text-5xl font-bold text-green-900">
                      ${tfsaData.total_contribution_room?.toLocaleString() || '0'}
                    </p>
                    <p className="text-sm text-green-700 mt-2">
                      Based on birth year {birthYear}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">First Eligible Year</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {tfsaData.first_eligible_year || 'N/A'}
                    </p>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-4">
                    <p className="text-sm text-gray-600 mb-1">Years of Eligibility</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {tfsaData.years_eligible || '0'}
                    </p>
                  </div>
                </div>

                {tfsaData.annual_limits && tfsaData.annual_limits.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Annual Contribution Limits</h4>
                    <div className="max-h-64 overflow-y-auto border border-gray-200 rounded-lg">
                      <table className="w-full text-sm">
                        <thead className="bg-gray-50 sticky top-0">
                          <tr>
                            <th className="text-left py-2 px-4 font-semibold text-gray-700">Year</th>
                            <th className="text-right py-2 px-4 font-semibold text-gray-700">Limit</th>
                          </tr>
                        </thead>
                        <tbody>
                          {tfsaData.annual_limits.map((limit: any) => (
                            <tr key={limit.year} className="border-t border-gray-100">
                              <td className="py-2 px-4 text-gray-900">{limit.year}</td>
                              <td className="py-2 px-4 text-right font-medium text-gray-900">
                                ${limit.limit.toLocaleString()}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-yellow-900 mb-1">Important Note</h4>
                      <p className="text-sm text-yellow-800">
                        This calculation assumes you have been a Canadian resident since age 18 and have
                        never contributed to a TFSA. Your actual contribution room may differ based on
                        previous contributions and withdrawals.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ) : (
            <Card>
              <div className="text-center py-12">
                <AlertCircle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to calculate</h3>
                <p className="text-gray-600">Please try again or check your birth year</p>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  )
}

interface ToggleSettingProps {
  label: string
  description: string
  checked: boolean
  onChange: () => void
}

function ToggleSetting({ label, description, checked, onChange }: ToggleSettingProps) {
  return (
    <div className="flex items-start justify-between py-3 border-b border-gray-100 last:border-0">
      <div className="flex-1">
        <h4 className="font-medium text-gray-900">{label}</h4>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </div>
      <button
        onClick={onChange}
        className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
          checked ? 'bg-primary-600' : 'bg-gray-200'
        }`}
      >
        <span
          className={`inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
    </div>
  )
}
