import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Lock, AlertCircle, Loader } from 'lucide-react';
import sharingService from '../services/sharingService';
import ChartContainer from '../components/Charts/ChartContainer';

const PublicDashboardPage: React.FC = () => {
  const { shareToken } = useParams<{ shareToken: string }>();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [requiresPassword, setRequiresPassword] = useState(false);
  const [password, setPassword] = useState('');
  const [dashboard, setDashboard] = useState<any>(null);
  const [allowInteractions, setAllowInteractions] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  useEffect(() => {
    if (shareToken) {
      checkSharedDashboard();
    }
  }, [shareToken]);

  const checkSharedDashboard = async () => {
    try {
      const info = await sharingService.getSharedDashboard(shareToken!);
      setRequiresPassword(info.requires_password);
      setAllowInteractions(info.allow_interactions);
      
      if (!info.requires_password) {
        // No password needed, load dashboard immediately
        await loadDashboard();
      }
      setLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Shared dashboard not found or expired');
      setLoading(false);
    }
  };

  const loadDashboard = async (pwd?: string) => {
    try {
      setPasswordError(null);
      const data = await sharingService.accessSharedDashboard(shareToken!, pwd);
      setDashboard(data.dashboard);
      setAllowInteractions(data.allow_interactions);
      setRequiresPassword(false);
    } catch (err: any) {
      if (err.response?.status === 401) {
        setPasswordError('Invalid password. Please try again.');
      } else {
        setError(err.response?.data?.detail || 'Failed to load dashboard');
      }
    }
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadDashboard(password);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="animate-spin mx-auto mb-4 text-blue-600" size={48} />
          <p className="text-gray-600">Loading shared dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
          <div className="text-center">
            <AlertCircle className="mx-auto mb-4 text-red-600" size={48} />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => navigate('/')}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700"
            >
              Go to Home
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (requiresPassword) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full mx-4">
          <div className="text-center mb-6">
            <Lock className="mx-auto mb-4 text-blue-600" size={48} />
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Password Required</h2>
            <p className="text-gray-600">This dashboard is password protected. Please enter the password to access it.</p>
          </div>

          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
                data-testid="password-input"
              />
              {passwordError && (
                <p className="text-red-600 text-sm mt-2">{passwordError}</p>
              )}
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-medium"
              data-testid="submit-password-button"
            >
              Access Dashboard
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader className="animate-spin mx-auto mb-4 text-blue-600" size={48} />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{dashboard.name}</h1>
              {dashboard.description && (
                <p className="text-gray-600 mt-1">{dashboard.description}</p>
              )}
            </div>
            {!allowInteractions && (
              <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-2 rounded-lg text-sm">
                View-only mode
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dashboard Content */}
      <div className="max-w-7xl mx-auto px-4 py-8" data-testid="public-dashboard-content">
        {dashboard.widgets && dashboard.widgets.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {dashboard.widgets.map((widget: any, index: number) => (
              <div
                key={index}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
                data-testid={`widget-${index}`}
              >
                <ChartContainer
                  type={widget.type}
                  data={widget.data}
                  config={widget.config}
                  title={widget.title}
                  height="300px"
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No widgets to display</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-gray-500">
          Powered by NexBII - Advanced Business Intelligence Platform
        </div>
      </div>
    </div>
  );
};

export default PublicDashboardPage;