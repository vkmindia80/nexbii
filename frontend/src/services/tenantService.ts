/**
 * Tenant Service
 * Handles tenant management, branding, and custom domains
 */

import api from './api';

export interface TenantBranding {
  logo_url?: string;
  logo_dark_url?: string;
  primary_color?: string;
  secondary_color?: string;
  accent_color?: string;
  font_family?: string;
  custom_css?: string;
  favicon_url?: string;
}

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  contact_email: string;
  contact_name?: string;
  plan: string;
  is_active: boolean;
  max_users: number;
  max_datasources: number;
  max_dashboards: number;
  max_queries: number;
  storage_limit_mb: number;
  storage_used_mb: number;
  features: Record<string, boolean>;
  branding: TenantBranding;
  custom_domain?: string;
  settings: Record<string, any>;
  extra_metadata: Record<string, any>;
  created_at: string;
  updated_at?: string;
  trial_ends_at?: string;
  suspended_at?: string;
}

export interface TenantDomain {
  id: string;
  tenant_id: string;
  domain: string;
  is_verified: boolean;
  is_primary: boolean;
  ssl_enabled: boolean;
  verification_token: string;
  verification_method: string;
  verified_at?: string;
  created_at: string;
}

export interface DomainVerificationInstructions {
  method: string;
  title: string;
  instructions: string;
  record_type?: string;
  host?: string;
  value?: string;
}

const tenantService = {
  // Get current user's tenant
  async getCurrentTenant(): Promise<Tenant> {
    const response = await api.get('/api/tenants/current');
    return response.data;
  },

  // Get tenant by ID
  async getTenant(tenantId: string): Promise<Tenant> {
    const response = await api.get(`/api/tenants/${tenantId}`);
    return response.data;
  },

  // Update tenant branding
  async updateBranding(tenantId: string, branding: TenantBranding): Promise<Tenant> {
    const response = await api.put(`/api/tenants/${tenantId}/branding`, {
      branding
    });
    return response.data;
  },

  // Add custom domain
  async addCustomDomain(
    tenantId: string,
    domain: string,
    isPrimary: boolean = false
  ): Promise<TenantDomain> {
    const response = await api.post(`/api/tenants/${tenantId}/domains`, {
      domain,
      is_primary: isPrimary
    });
    return response.data;
  },

  // List custom domains
  async listCustomDomains(tenantId: string): Promise<TenantDomain[]> {
    const response = await api.get(`/api/tenants/${tenantId}/domains`);
    return response.data;
  },

  // Get domain verification instructions
  async getDomainVerificationInstructions(
    tenantId: string,
    domainId: string
  ): Promise<DomainVerificationInstructions> {
    const response = await api.get(
      `/api/tenants/${tenantId}/domains/${domainId}/verification-instructions`
    );
    return response.data;
  },

  // Verify custom domain
  async verifyDomain(tenantId: string, domainId: string): Promise<any> {
    const response = await api.post(`/api/tenants/${tenantId}/domains/${domainId}/verify`);
    return response.data;
  },

  // Upload SSL certificate
  async uploadSSLCertificate(
    tenantId: string,
    domainId: string,
    certificatePem: string,
    privateKeyPem: string,
    chainPem?: string
  ): Promise<any> {
    const response = await api.post(
      `/api/tenants/${tenantId}/domains/${domainId}/ssl/upload`,
      {
        certificate_pem: certificatePem,
        private_key_pem: privateKeyPem,
        chain_pem: chainPem
      }
    );
    return response.data;
  },

  // Request Let's Encrypt certificate
  async requestLetsEncrypt(
    tenantId: string,
    domainId: string,
    email: string,
    staging: boolean = false
  ): Promise<any> {
    const response = await api.post(
      `/api/tenants/${tenantId}/domains/${domainId}/ssl/letsencrypt`,
      {
        email,
        staging
      }
    );
    return response.data;
  },

  // Get SSL certificate info
  async getSSLCertificateInfo(tenantId: string, domainId: string): Promise<any> {
    const response = await api.get(`/api/tenants/${tenantId}/domains/${domainId}/ssl/info`);
    return response.data;
  },

  // Renew Let's Encrypt certificate
  async renewSSLCertificate(tenantId: string, domainId: string): Promise<any> {
    const response = await api.post(`/api/tenants/${tenantId}/domains/${domainId}/ssl/renew`);
    return response.data;
  },

  // Apply tenant branding to document
  applyTenantBranding(branding: TenantBranding) {
    const root = document.documentElement;

    // Apply colors
    if (branding.primary_color) {
      root.style.setProperty('--tenant-primary', branding.primary_color);
    }
    if (branding.secondary_color) {
      root.style.setProperty('--tenant-secondary', branding.secondary_color);
    }
    if (branding.accent_color) {
      root.style.setProperty('--tenant-accent', branding.accent_color);
    }

    // Apply font family
    if (branding.font_family) {
      root.style.setProperty('--tenant-font', branding.font_family);
      document.body.style.fontFamily = branding.font_family;
    }

    // Apply favicon
    if (branding.favicon_url) {
      const favicon = document.querySelector("link[rel*='icon']") as HTMLLinkElement;
      if (favicon) {
        favicon.href = branding.favicon_url;
      } else {
        const newFavicon = document.createElement('link');
        newFavicon.rel = 'icon';
        newFavicon.href = branding.favicon_url;
        document.head.appendChild(newFavicon);
      }
    }

    // Apply custom CSS
    if (branding.custom_css) {
      let styleElement = document.getElementById('tenant-custom-css') as HTMLStyleElement;
      if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = 'tenant-custom-css';
        document.head.appendChild(styleElement);
      }
      styleElement.textContent = branding.custom_css;
    }
  },

  // Get tenant branding from local storage
  getTenantBrandingFromStorage(): TenantBranding | null {
    const brandingStr = localStorage.getItem('tenant_branding');
    if (brandingStr) {
      try {
        return JSON.parse(brandingStr);
      } catch {
        return null;
      }
    }
    return null;
  },

  // Save tenant branding to local storage
  saveTenantBrandingToStorage(branding: TenantBranding) {
    localStorage.setItem('tenant_branding', JSON.stringify(branding));
  }
};

export default tenantService;
