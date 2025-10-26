import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  Database, 
  LayoutDashboard, 
  FileText, 
  Settings, 
  LogOut, 
  Menu, 
  X,
  BarChart3,
  PieChart,
  Bell,
  Activity,
  Plug,
  Brain,
  User,
  Building2,
  Key,
  Webhook,
  Puzzle,
  Shield,
  Lock,
  Smartphone,
  FileCheck
} from 'lucide-react';
import { authService } from '../services/authService';
import TenantSwitcher from './TenantSwitcher';
import TenantLogo from './TenantLogo';

const Layout: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    authService.logout();
    navigate('/login');
  };

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Home' },
    { path: '/datasources', icon: Database, label: 'Data Sources' },
    { path: '/queries', icon: FileText, label: 'Queries' },
    { path: '/dashboards', icon: BarChart3, label: 'Dashboards' },
    { path: '/analytics', icon: Brain, label: 'Analytics' },
    { path: '/alerts', icon: Bell, label: 'Alerts' },
    { path: '/activity', icon: Activity, label: 'Activity Feed' },
    { path: '/integrations', icon: Plug, label: 'Integrations' },
    { path: '/charts-showcase', icon: PieChart, label: 'Charts Showcase' },
    { path: '/settings/api-keys', icon: Key, label: 'API Keys' },
    { path: '/settings/webhooks', icon: Webhook, label: 'Webhooks' },
    { path: '/settings/plugins', icon: Puzzle, label: 'Plugins' },
    { path: '/profile', icon: User, label: 'Profile' },
    { path: '/tenant-settings', icon: Building2, label: 'Tenant Settings' },
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-white border-r border-gray-200 transition-all duration-300 flex flex-col`}
      >
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          {sidebarOpen ? (
            <TenantLogo size="md" showText={true} />
          ) : (
            <TenantLogo size="md" showText={false} />
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 rounded-lg hover:bg-gray-100"
            data-testid="sidebar-toggle"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className="w-5 h-5" />
                {sidebarOpen && <span className="font-medium">{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="p-3 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-700 hover:bg-red-50 hover:text-red-600 w-full transition-colors"
            data-testid="logout-button"
          >
            <LogOut className="w-5 h-5" />
            {sidebarOpen && <span className="font-medium">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Top Header Bar with Tenant Switcher */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-8 py-4 flex items-center justify-end">
          <TenantSwitcher onSettingsClick={() => navigate('/tenant-settings')} />
        </div>
        
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;