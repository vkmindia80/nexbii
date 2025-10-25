/**
 * Tenant Switcher Component
 * Dropdown in header for managing tenant settings and viewing current tenant info
 */

import React, { useState, useEffect } from 'react';
import { Building2, Settings, Crown, Users, Database, LayoutDashboard, CheckCircle } from 'lucide-react';
import tenantService, { Tenant } from '../services/tenantService';

interface TenantSwitcherProps {
  onSettingsClick?: () => void;
}

const TenantSwitcher: React.FC<TenantSwitcherProps> = ({ onSettingsClick }) => {
  const [tenant, setTenant] = useState<Tenant | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTenant();
  }, []);

  const loadTenant = async () => {
    try {
      const currentTenant = await tenantService.getCurrentTenant();
      setTenant(currentTenant);
      
      // Apply branding
      if (currentTenant.branding) {
        tenantService.applyTenantBranding(currentTenant.branding);
        tenantService.saveTenantBrandingToStorage(currentTenant.branding);
      }
    } catch (error) {
      console.error('Failed to load tenant:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800">
        <div className="animate-pulse flex items-center space-x-2">
          <div className="h-4 w-4 bg-gray-300 rounded"></div>
          <div className="h-4 w-24 bg-gray-300 rounded"></div>
        </div>
      </div>
    );
  }

  if (!tenant) {
    return null;
  }

  const getPlanBadgeColor = (plan: string) => {
    switch (plan.toLowerCase()) {
      case 'free':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
      case 'starter':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      case 'professional':
        return 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200';
      case 'enterprise':
        return 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getPlanIcon = (plan: string) => {
    if (plan.toLowerCase() === 'enterprise') {
      return <Crown className="w-4 h-4" />;
    }
    return <Building2 className="w-4 h-4" />;
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        data-testid="tenant-switcher-button"
      >
        {tenant.branding?.logo_url ? (
          <img 
            src={tenant.branding.logo_url} 
            alt={tenant.name} 
            className="h-6 w-6 object-contain"
          />
        ) : (
          <Building2 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
        )}
        <div className="flex flex-col items-start">
          <span className="text-sm font-medium text-gray-900 dark:text-white truncate max-w-[150px]">
            {tenant.name}
          </span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${getPlanBadgeColor(tenant.plan)}`}>
            {tenant.plan}
          </span>
        </div>
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          ></div>
          <div
            className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-20"
            data-testid="tenant-switcher-dropdown"
          >
            {/* Tenant Header */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <div className="flex items-start space-x-3">
                {tenant.branding?.logo_url ? (
                  <img 
                    src={tenant.branding.logo_url} 
                    alt={tenant.name} 
                    className="h-10 w-10 object-contain"
                  />
                ) : (
                  <div className="h-10 w-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-white" />
                  </div>
                )}
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
                    {tenant.name}
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {tenant.slug}.nexbii.com
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className={`text-xs px-2 py-0.5 rounded-full flex items-center space-x-1 ${getPlanBadgeColor(tenant.plan)}`}>
                      {getPlanIcon(tenant.plan)}
                      <span>{tenant.plan} Plan</span>
                    </span>
                    {tenant.is_active && (
                      <span className="text-xs text-green-600 dark:text-green-400 flex items-center">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Active
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Usage Stats */}
            <div className="p-4 border-b border-gray-200 dark:border-gray-700">
              <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-3 uppercase">
                Resource Usage
              </h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                    <Users className="w-4 h-4" />
                    <span>Users</span>
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">
                    0 / {tenant.max_users}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                    <Database className="w-4 h-4" />
                    <span>Data Sources</span>
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">
                    0 / {tenant.max_datasources}
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center space-x-2 text-gray-600 dark:text-gray-400">
                    <LayoutDashboard className="w-4 h-4" />
                    <span>Dashboards</span>
                  </div>
                  <span className="font-medium text-gray-900 dark:text-white">
                    0 / {tenant.max_dashboards}
                  </span>
                </div>
              </div>
            </div>

            {/* Features */}
            {Object.keys(tenant.features).length > 0 && (
              <div className="p-4 border-b border-gray-200 dark:border-gray-700">
                <h4 className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase">
                  Features
                </h4>
                <div className="flex flex-wrap gap-1">
                  {Object.entries(tenant.features).map(([feature, enabled]) => (
                    enabled && (
                      <span
                        key={feature}
                        className="text-xs px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200 rounded-full"
                      >
                        {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    )
                  ))}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="p-2">
              {onSettingsClick && (
                <button
                  onClick={() => {
                    setIsOpen(false);
                    onSettingsClick();
                  }}
                  className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                  data-testid="tenant-settings-button"
                >
                  <Settings className="w-4 h-4" />
                  <span>Tenant Settings</span>
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default TenantSwitcher;
