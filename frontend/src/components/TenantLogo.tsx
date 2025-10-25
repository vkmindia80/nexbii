/**
 * Tenant Logo Component
 * Displays tenant's custom logo or default NexBII logo
 */

import React, { useEffect, useState } from 'react';
import { BarChart3 } from 'lucide-react';
import tenantService from '../services/tenantService';

interface TenantLogoProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
}

const TenantLogo: React.FC<TenantLogoProps> = ({
  className = '',
  size = 'md',
  showText = true
}) => {
  const [logoUrl, setLogoUrl] = useState<string | null>(null);
  const [companyName, setCompanyName] = useState('NexBII');
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    loadLogo();
    
    // Detect dark mode
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    setIsDarkMode(darkModeMediaQuery.matches);
    
    const handleDarkModeChange = (e: MediaQueryListEvent) => {
      setIsDarkMode(e.matches);
    };
    
    darkModeMediaQuery.addEventListener('change', handleDarkModeChange);
    
    return () => {
      darkModeMediaQuery.removeEventListener('change', handleDarkModeChange);
    };
  }, []);

  const loadLogo = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const tenant = await tenantService.getCurrentTenant();
      if (tenant.branding) {
        const url = isDarkMode 
          ? (tenant.branding.logo_dark_url || tenant.branding.logo_url)
          : tenant.branding.logo_url;
        
        setLogoUrl(url || null);
      }
      setCompanyName(tenant.name || 'NexBII');
    } catch (err) {
      console.error('Failed to load tenant logo:', err);
    }
  };

  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-8 w-8',
    lg: 'h-10 w-10'
  };

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-xl',
    lg: 'text-2xl'
  };

  if (logoUrl) {
    return (
      <div className={`flex items-center space-x-2 ${className}`}>
        <img
          src={logoUrl}
          alt={companyName}
          className={`${sizeClasses[size]} object-contain`}
          onError={() => setLogoUrl(null)}
        />
        {showText && (
          <span className={`font-bold ${textSizeClasses[size]} text-gray-900 dark:text-white`}>
            {companyName}
          </span>
        )}
      </div>
    );
  }

  // Default logo
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <BarChart3 className={`${sizeClasses[size]} text-purple-600 dark:text-purple-400`} />
      {showText && (
        <span className={`font-bold ${textSizeClasses[size]} bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent`}>
          {companyName}
        </span>
      )}
    </div>
  );
};

export default TenantLogo;
