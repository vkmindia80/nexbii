import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BarChart3, Mail, Lock, Zap, Database } from 'lucide-react';
import { authService } from '../services/authService';
import { demoService } from '../services/demoService';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [generatingData, setGeneratingData] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await authService.login(email, password);
      localStorage.setItem('token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      navigate('/');
      window.location.reload(); // Refresh to update auth state
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = () => {
    setEmail('admin@nexbii.demo');
    setPassword('demo123');
    setError('');
    setSuccessMessage('');
  };

  const handleGenerateDemoData = async () => {
    setGeneratingData(true);
    setError('');
    setSuccessMessage('');

    try {
      const response = await demoService.generateDemoData();
      const summary = response.summary || {};
      const dbRecords = summary.database_records || {};
      
      setSuccessMessage(
        `✨ Demo Data Generated Successfully for All Modules!\n\n` +
        `👤 Users: Demo admin account (admin@nexbii.demo / demo123)\n` +
        `🗄️ Data Sources: ${response.data.datasources} sources (SQLite with real data, PostgreSQL, MongoDB)\n` +
        `📝 Queries: ${response.data.queries} comprehensive SQL queries (sales, customers, HR, products, reviews, analytics)\n` +
        `📊 Dashboards: ${response.data.dashboards} interactive dashboards (Sales, Customer, Operations, HR, Products, Sales Targets)\n` +
        `📈 Charts: All 20 chart types (10 basic + 10 advanced visualizations)\n` +
        `💾 Database: 9 tables with comprehensive data:\n` +
        `   • ${dbRecords.products || 25} products, ${dbRecords.customers || 200} customers\n` +
        `   • ${dbRecords.orders || 1500} orders, ${dbRecords.departments || 8} departments\n` +
        `   • ~${dbRecords.employees || 80} employees, ${dbRecords.sales_targets || 48} sales targets\n` +
        `   • ${dbRecords.product_reviews || 500} reviews, ${dbRecords.user_activities || 5000} activities\n\n` +
        `🤖 AI Features: Natural language queries, query optimization, chart recommendations, automated insights\n\n` +
        `🎯 Ready to explore! Login with demo credentials and check out:\n` +
        `   • Data Sources page - Browse database schema\n` +
        `   • Queries page - Try AI-powered natural language queries\n` +
        `   • Dashboards page - Explore 6 interactive analytics dashboards`
      );
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate demo data. Please try again.');
    } finally {
      setGeneratingData(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-700 rounded-2xl mb-4">
            <BarChart3 className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
            NexBII
          </h1>
          <p className="text-gray-600 mt-2">Advanced Business Intelligence Platform</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Welcome Back</h2>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4" data-testid="error-message">
              {error}
            </div>
          )}

          {successMessage && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg mb-4 whitespace-pre-line" data-testid="success-message">
              {successMessage}
            </div>
          )}

          {/* Demo Credentials Banner */}
          <div className="mb-6 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
              <Zap className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-amber-900 mb-1">Try Demo Account</h3>
                <p className="text-xs text-amber-700 mb-2">
                  Explore the platform with pre-configured demo credentials
                </p>
                <div className="flex flex-wrap gap-2">
                  <button
                    type="button"
                    onClick={handleDemoLogin}
                    className="inline-flex items-center space-x-2 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
                    data-testid="demo-login-button"
                  >
                    <Zap className="w-4 h-4" />
                    <span>Fill Demo Credentials</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleGenerateDemoData}
                    disabled={generatingData}
                    className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    data-testid="generate-demo-data-button"
                  >
                    <Database className="w-4 h-4" />
                    <span>{generatingData ? 'Generating...' : 'Generate Demo Data'}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="you@example.com"
                  required
                  data-testid="email-input"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="••••••••"
                  required
                  data-testid="password-input"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-primary-600 text-white py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              data-testid="login-button"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-600">
              Don't have an account?{' '}
              <Link to="/register" className="text-primary-600 font-medium hover:text-primary-700">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;