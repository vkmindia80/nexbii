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
  FileCheck,
  GitBranch,
  Table,
  Search,
  Users,
  TrendingUp,
  HardDrive,
  Cog
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
  ];

  const securityItems = [
    { path: '/security/policies', icon: Shield, label: 'Security Policies' },
    { path: '/security/sso', icon: Lock, label: 'SSO Configuration' },
    { path: '/security/mfa', icon: Smartphone, label: 'MFA Management' },
    { path: '/security/audit-logs', icon: FileText, label: 'Audit Logs' },
    { path: '/security/compliance', icon: FileCheck, label: 'Compliance' },
  ];

  const governanceItems = [
    { path: '/governance/catalog', icon: Database, label: 'Data Catalog' },
    { path: '/governance/lineage', icon: GitBranch, label: 'Data Lineage' },
    { path: '/governance/classification', icon: Shield, label: 'Classification' },
    { path: '/governance/access-requests', icon: Key, label: 'Access Requests' },
  ];

  const adminItems = [
    { path: '/admin/monitoring', icon: Activity, label: 'System Monitoring' },
    { path: '/admin/performance', icon: TrendingUp, label: 'Performance' },
    { path: '/admin/usage', icon: BarChart3, label: 'Usage Analytics' },
    { path: '/admin/users', icon: Users, label: 'User Management' },
    { path: '/admin/backups', icon: HardDrive, label: 'Backups' },
    { path: '/admin/config', icon: Cog, label: 'Configuration' },
  ];

  const settingsItems = [
    { path: '/settings/api-keys', icon: Key, label: 'API Keys' },
    { path: '/settings/webhooks', icon: Webhook, label: 'Webhooks' },
    { path: '/settings/plugins', icon: Puzzle, label: 'Plugins' },
    { path: '/profile', icon: User, label: 'Profile' },
    { path: '/tenant-settings', icon: Building2, label: 'Tenant Settings' },
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-gray-50 via-blue-50/20 to-purple-50/20">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-white/90 backdrop-blur-xl border-r border-gray-200/80 shadow-xl transition-all duration-300 flex flex-col relative z-10`}
      >
        {/* Gradient Accent */}
        <div className="absolute inset-y-0 left-0 w-1 bg-gradient-to-b from-primary-500 via-secondary-500 to-primary-500"></div>
        
        {/* Logo */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200/80 bg-gradient-to-r from-white to-gray-50/50">
          {sidebarOpen ? (
            <div className="animate-fadeIn">
              <TenantLogo size="md" showText={true} />
            </div>
          ) : (
            <TenantLogo size="md" showText={false} />
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gradient-to-br hover:from-primary-50 hover:to-secondary-50 transition-all duration-200 hover:scale-110 active:scale-95"
            data-testid="sidebar-toggle"
          >
            {sidebarOpen ? <X className="w-5 h-5 text-gray-600" /> : <Menu className="w-5 h-5 text-gray-600" />}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          {/* Main Navigation */}
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-200 relative overflow-hidden ${
                  isActive
                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/30'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 hover:shadow-md'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className={`w-5 h-5 transition-transform duration-200 ${!isActive && 'group-hover:scale-110'}`} />
                {sidebarOpen && (
                  <span className="font-medium text-sm animate-fadeIn">{item.label}</span>
                )}
                {isActive && (
                  <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 animate-shimmer"></div>
                )}
              </Link>
            );
          })}

          {/* Security Section */}
          {sidebarOpen && (
            <div className="pt-4 mt-4 border-t border-gray-200/80">
              <div className="px-3 mb-2 text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center">
                <Shield className="w-3 h-3 mr-1.5" />
                Security
              </div>
            </div>
          )}
          {securityItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-200 relative overflow-hidden ${
                  isActive
                    ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-lg shadow-red-500/30'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 hover:shadow-md'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className={`w-5 h-5 transition-transform duration-200 ${!isActive && 'group-hover:scale-110'}`} />
                {sidebarOpen && (
                  <span className="font-medium text-sm animate-fadeIn">{item.label}</span>
                )}
              </Link>
            );
          })}

          {/* Data Governance Section */}
          {sidebarOpen && (
            <div className="pt-4 mt-4 border-t border-gray-200/80">
              <div className="px-3 mb-2 text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center">
                <Database className="w-3 h-3 mr-1.5" />
                Data Governance
              </div>
            </div>
          )}
          {governanceItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-200 relative overflow-hidden ${
                  isActive
                    ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg shadow-green-500/30'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 hover:shadow-md'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className={`w-5 h-5 transition-transform duration-200 ${!isActive && 'group-hover:scale-110'}`} />
                {sidebarOpen && (
                  <span className="font-medium text-sm animate-fadeIn">{item.label}</span>
                )}
              </Link>
            );
          })}

          {/* Admin Section */}
          {sidebarOpen && (
            <div className="pt-4 mt-4 border-t border-gray-200/80">
              <div className="px-3 mb-2 text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center">
                <Cog className="w-3 h-3 mr-1.5" />
                Enterprise Admin
              </div>
            </div>
          )}
          {adminItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-200 relative overflow-hidden ${
                  isActive
                    ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-lg shadow-purple-500/30'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 hover:shadow-md'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className={`w-5 h-5 transition-transform duration-200 ${!isActive && 'group-hover:scale-110'}`} />
                {sidebarOpen && (
                  <span className="font-medium text-sm animate-fadeIn">{item.label}</span>
                )}
              </Link>
            );
          })}

          {/* Settings Section */}
          {sidebarOpen && (
            <div className="pt-4 mt-4 border-t border-gray-200/80">
              <div className="px-3 mb-2 text-xs font-bold text-gray-500 uppercase tracking-wider flex items-center">
                <Settings className="w-3 h-3 mr-1.5" />
                Settings
              </div>
            </div>
          )}
          {settingsItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`group flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-200 relative overflow-hidden ${
                  isActive
                    ? 'bg-gradient-to-r from-gray-600 to-gray-700 text-white shadow-lg shadow-gray-500/30'
                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-gray-100 hover:to-gray-50 hover:shadow-md'
                }`}
                data-testid={`nav-${item.label.toLowerCase().replace(' ', '-')}`}
              >
                <Icon className={`w-5 h-5 transition-transform duration-200 ${!isActive && 'group-hover:scale-110'}`} />
                {sidebarOpen && (
                  <span className="font-medium text-sm animate-fadeIn">{item.label}</span>
                )}
              </Link>
            );
          })}
        </nav>

        {/* Logout */}
        <div className="p-3 border-t border-gray-200/80 bg-gradient-to-r from-white to-gray-50/50">
          <button
            onClick={handleLogout}
            className="group flex items-center space-x-3 px-3 py-2.5 rounded-xl text-gray-700 hover:bg-gradient-to-r hover:from-red-50 hover:to-red-100 hover:text-red-600 w-full transition-all duration-200 hover:shadow-md"
            data-testid="logout-button"
          >
            <LogOut className="w-5 h-5 transition-transform duration-200 group-hover:scale-110" />
            {sidebarOpen && <span className="font-medium text-sm animate-fadeIn">Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Top Header Bar with Tenant Switcher */}
        <div className="sticky top-0 z-10 bg-white/80 backdrop-blur-xl border-b border-gray-200/80 px-8 py-4 shadow-sm">
          <div className="flex items-center justify-end">
            <TenantSwitcher onSettingsClick={() => navigate('/tenant-settings')} />
          </div>
        </div>
        
        <div className="p-8 animate-fadeIn">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;