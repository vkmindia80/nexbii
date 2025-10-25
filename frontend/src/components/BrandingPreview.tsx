/**
 * Branding Preview Component
 * Shows real-time preview of tenant branding changes
 */

import React from 'react';
import { TenantBranding } from '../services/tenantService';
import { Mail, Bell, User, BarChart3 } from 'lucide-react';

interface BrandingPreviewProps {
  branding: TenantBranding;
}

const BrandingPreview: React.FC<BrandingPreviewProps> = ({ branding }) => {
  const primaryColor = branding.primary_color || '#667eea';
  const secondaryColor = branding.secondary_color || '#764ba2';
  const accentColor = branding.accent_color || '#3b82f6';
  const fontFamily = branding.font_family || 'Inter, sans-serif';
  const logoUrl = branding.logo_url;

  return (
    <div className="space-y-6">
      <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        Live Preview
      </div>

      {/* Email Preview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
        <div className="text-xs text-gray-500 dark:text-gray-400 px-3 py-2 bg-gray-50 dark:bg-gray-900/50 border-b border-gray-200 dark:border-gray-700">
          Email Template Preview
        </div>
        <div
          className="p-4"
          style={{
            fontFamily: fontFamily
          }}
        >
          {/* Email Header */}
          <div
            className="rounded-t-lg p-4 text-white text-center"
            style={{
              background: `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)`
            }}
          >
            {logoUrl ? (
              <img
                src={logoUrl}
                alt="Logo"
                className="h-8 mx-auto mb-2"
                onError={(e) => {
                  (e.target as HTMLImageElement).style.display = 'none';
                }}
              />
            ) : (
              <BarChart3 className="h-8 w-8 mx-auto mb-2" />
            )}
            <h2 className="text-lg font-bold">Welcome Email</h2>
          </div>

          {/* Email Body */}
          <div className="p-4 bg-gray-50 dark:bg-gray-900/30 rounded-b-lg">
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
              Hi John,
            </p>
            <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
              Welcome to our platform! We're excited to have you on board.
            </p>
            <button
              className="px-4 py-2 rounded text-white text-sm font-medium"
              style={{ backgroundColor: primaryColor }}
            >
              Get Started
            </button>
          </div>
        </div>
      </div>

      {/* Button Styles Preview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
          Button Styles
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            className="px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ backgroundColor: primaryColor }}
          >
            Primary Button
          </button>
          <button
            className="px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ backgroundColor: secondaryColor }}
          >
            Secondary Button
          </button>
          <button
            className="px-4 py-2 rounded-lg text-white text-sm font-medium"
            style={{ backgroundColor: accentColor }}
          >
            Accent Button
          </button>
        </div>
      </div>

      {/* UI Elements Preview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
          UI Elements
        </div>
        <div className="space-y-3">
          <div className="flex items-center space-x-2">
            <Mail className="w-5 h-5" style={{ color: primaryColor }} />
            <span className="text-sm" style={{ color: primaryColor }}>Primary Icon</span>
          </div>
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5" style={{ color: secondaryColor }} />
            <span className="text-sm" style={{ color: secondaryColor }}>Secondary Icon</span>
          </div>
          <div className="flex items-center space-x-2">
            <User className="w-5 h-5" style={{ color: accentColor }} />
            <span className="text-sm" style={{ color: accentColor }}>Accent Icon</span>
          </div>
        </div>
      </div>

      {/* Color Palette */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
          Color Palette
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div>
            <div
              className="h-16 rounded-lg mb-2"
              style={{ backgroundColor: primaryColor }}
            />
            <div className="text-xs text-gray-600 dark:text-gray-400">Primary</div>
            <div className="text-xs font-mono text-gray-500">{primaryColor}</div>
          </div>
          <div>
            <div
              className="h-16 rounded-lg mb-2"
              style={{ backgroundColor: secondaryColor }}
            />
            <div className="text-xs text-gray-600 dark:text-gray-400">Secondary</div>
            <div className="text-xs font-mono text-gray-500">{secondaryColor}</div>
          </div>
          <div>
            <div
              className="h-16 rounded-lg mb-2"
              style={{ backgroundColor: accentColor }}
            />
            <div className="text-xs text-gray-600 dark:text-gray-400">Accent</div>
            <div className="text-xs font-mono text-gray-500">{accentColor}</div>
          </div>
        </div>
      </div>

      {/* Font Preview */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4">
        <div className="text-xs text-gray-500 dark:text-gray-400 mb-3">
          Typography
        </div>
        <div style={{ fontFamily: fontFamily }}>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            The Quick Brown Fox
          </h3>
          <p className="text-base text-gray-700 dark:text-gray-300 mb-2">
            The quick brown fox jumps over the lazy dog.
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Font Family: {fontFamily}
          </p>
        </div>
      </div>
    </div>
  );
};

export default BrandingPreview;
