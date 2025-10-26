import api from './api';

// OAuth Provider Types
export interface OAuthProvider {
  id: string;
  provider_name: string;
  display_name: string;
  client_id: string;
  authorize_url: string;
  token_url: string;
  user_info_url: string;
  scopes: string[];
  is_enabled: boolean;
  tenant_id: string;
  created_at: string;
}

export interface SAMLConfig {
  id: string;
  idp_entity_id: string;
  sso_url: string;
  x509_cert: string;
  name_id_format: string;
  is_enabled: boolean;
  tenant_id: string;
  created_at: string;
}

export interface LDAPConfig {
  id: string;
  server_url: string;
  bind_dn: string;
  search_base: string;
  user_filter: string;
  is_enabled: boolean;
  tenant_id: string;
  created_at: string;
}

export interface CreateOAuthProviderRequest {
  provider_name: string;
  display_name: string;
  client_id: string;
  client_secret: string;
  authorize_url?: string;
  token_url?: string;
  user_info_url?: string;
  scopes?: string[];
}

export interface CreateSAMLConfigRequest {
  idp_entity_id: string;
  sso_url: string;
  x509_cert: string;
  name_id_format?: string;
}

export interface CreateLDAPConfigRequest {
  server_url: string;
  bind_dn: string;
  bind_password: string;
  search_base: string;
  user_filter: string;
}

class SSOService {
  // OAuth Providers
  async getProviders(): Promise<OAuthProvider[]> {
    const response = await api.get('/api/sso/providers');
    return response.data;
  }

  async getProvider(id: string): Promise<OAuthProvider> {
    const response = await api.get(`/api/sso/providers/${id}`);
    return response.data;
  }

  async createProvider(data: CreateOAuthProviderRequest): Promise<OAuthProvider> {
    const response = await api.post('/api/sso/providers', data);
    return response.data;
  }

  async updateProvider(id: string, data: Partial<OAuthProvider>): Promise<OAuthProvider> {
    const response = await api.put(`/api/sso/providers/${id}`, data);
    return response.data;
  }

  async deleteProvider(id: string): Promise<void> {
    await api.delete(`/api/sso/providers/${id}`);
  }

  // SAML Configuration
  async getSAMLConfig(): Promise<SAMLConfig> {
    const response = await api.get('/api/sso/saml/config');
    return response.data;
  }

  async createSAMLConfig(data: CreateSAMLConfigRequest): Promise<SAMLConfig> {
    const response = await api.post('/api/sso/saml/config', data);
    return response.data;
  }

  async getSAMLMetadata(): Promise<string> {
    const response = await api.get('/api/sso/saml/metadata');
    return response.data;
  }

  // LDAP Configuration
  async getLDAPConfig(): Promise<LDAPConfig> {
    const response = await api.get('/api/sso/ldap/config');
    return response.data;
  }

  async createLDAPConfig(data: CreateLDAPConfigRequest): Promise<LDAPConfig> {
    const response = await api.post('/api/sso/ldap/config', data);
    return response.data;
  }

  async testLDAPConnection(): Promise<{ success: boolean; message: string }> {
    const response = await api.post('/api/sso/ldap/test');
    return response.data;
  }

  async syncLDAPUsers(): Promise<{ synced_count: number; message: string }> {
    const response = await api.post('/api/sso/ldap/sync');
    return response.data;
  }
}

export default new SSOService();
