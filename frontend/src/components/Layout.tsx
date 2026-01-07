import { Outlet, NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Briefcase,
  Search,
  Bell,
  Newspaper,
  Settings as SettingsIcon,
  TrendingUp,
} from 'lucide-react'

const navigation = [
  { name: 'Dashboard', to: '/', icon: LayoutDashboard },
  { name: 'Portfolio', to: '/portfolio', icon: Briefcase },
  { name: 'Search', to: '/search', icon: Search },
  { name: 'Alerts', to: '/alerts', icon: Bell },
  { name: 'News', to: '/news', icon: Newspaper },
  { name: 'Settings', to: '/settings', icon: SettingsIcon },
]

export default function Layout() {
  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <TrendingUp className="w-8 h-8 text-primary-600" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">Stonk Bro</h1>
              <p className="text-xs text-gray-500">Stock Research Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </NavLink>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            v0.1.0 • Self-hosted
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <Outlet />
      </div>
    </div>
  )
}
