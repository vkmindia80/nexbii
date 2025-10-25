/**
 * Custom hook for tenant branding
 * Loads and applies tenant branding on component mount
 */

import { useState, useEffect } from 'react';
import tenantService, { TenantBranding } from '../services/tenantService';

export const useTenantBranding = () => {
  const [branding, setBranding] = useState<TenantBranding | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadBranding();
  }, []);

  const loadBranding = async () => {
    try {
      // Check if user is authenticated
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      // Try to load from storage first (fast)
      const storedBranding = tenantService.getTenantBrandingFromStorage();
      if (storedBranding) {
        setBranding(storedBranding);
        tenantService.applyTenantBranding(storedBranding);
      }

      // Load from API (authoritative)
      try {
        const tenant = await tenantService.getCurrentTenant();
        if (tenant.branding && Object.keys(tenant.branding).length > 0) {
          setBranding(tenant.branding);
          tenantService.applyTenantBranding(tenant.branding);
          tenantService.saveTenantBrandingToStorage(tenant.branding);
        }
      } catch (err: any) {
        // If tenant API fails, use stored branding
        console.warn('Failed to load tenant branding from API:', err);
        if (!storedBranding) {
          setError('Failed to load branding');
        }
      }
    } catch (err) {
      console.error('Error loading tenant branding:', err);
      setError('Failed to load branding');
    } finally {
      setLoading(false);
    }
  };

  const updateBranding = (newBranding: TenantBranding) => {
    setBranding(newBranding);
    tenantService.applyTenantBranding(newBranding);
    tenantService.saveTenantBrandingToStorage(newBranding);
  };

  return {
    branding,
    loading,
    error,
    updateBranding,
    reloadBranding: loadBranding
  };
};
