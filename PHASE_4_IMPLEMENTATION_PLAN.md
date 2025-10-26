# Phase 4 Enterprise Features - Complete Implementation Plan
**Created:** January 2026  
**Status:** Planning Phase  
**Target:** Complete remaining 50% of Phase 4 (Phases 4.2-4.5)

---

## 📊 Overview

**Current Status:**
- ✅ Phase 4.1: Multi-Tenancy & White-Labeling (100% Complete)
- ⏳ Phase 4.2: API & Extensibility (0%)
- ⏳ Phase 4.3: Security & Compliance (0%)
- ⏳ Phase 4.4: Data Governance (0%)
- ⏳ Phase 4.5: Enterprise Admin (0%)

**Total Estimated Time:** 10-14 weeks  
**Estimated Effort:** 400-560 hours

---

## 🎯 PHASE 4.2: API & EXTENSIBILITY

**Timeline:** 2-3 weeks  
**Estimated Effort:** 80-120 hours  
**Priority:** HIGH - Critical for developer integration

### Week 1: API Key Management System

#### Backend Implementation (3-4 days)

**1. API Key Model & Database**
- New model: `APIKey`
  - Fields: id, name, key_hash, tenant_id, user_id, scopes, rate_limit, expires_at, last_used_at
  - Indexes: key_hash (unique), tenant_id, user_id
- Generate secure API keys (32-byte random + prefix)
- Store hashed keys (bcrypt) for security

**2. API Key Authentication Middleware**
- New dependency: `get_api_key()`
- Header: `Authorization: Bearer api_key_xxx`
- Validate key, check expiration, update last_used_at
- Inject tenant context from API key

**3. API Key CRUD Endpoints**
- `POST /api/api-keys/` - Create API key with scopes
- `GET /api/api-keys/` - List user's API keys
- `GET /api/api-keys/{id}` - Get API key details
- `PUT /api/api-keys/{id}` - Update name, scopes, rate limits
- `DELETE /api/api-keys/{id}` - Revoke API key
- `POST /api/api-keys/{id}/rotate` - Rotate key (generate new)

**4. Scope-Based Permissions**
- Define scopes: `read:datasources`, `write:queries`, `read:dashboards`, etc.
- Scope validation in endpoints
- Granular permission control per API key

#### Frontend Implementation (2-3 days)

**1. API Keys Management Page**
- `/settings/api-keys` route
- List all API keys with last used, status, expiration
- Create new key modal:
  - Name, description
  - Scope selector (checkboxes)
  - Rate limit configuration
  - Expiration date picker
- Show generated key ONCE (copy to clipboard warning)
- Revoke/delete key with confirmation

**2. API Documentation Page**
- `/docs/api` route
- Interactive API documentation
- Code examples (cURL, Python, JavaScript)
- Authentication guide
- Rate limit information

#### Testing (1 day)
- API key generation and validation tests
- Scope permission tests
- Rate limiting tests
- Token rotation tests

---

### Week 2: Rate Limiting & Webhook System

#### Backend Implementation (4-5 days)

**1. Rate Limiting System**
- Redis-based rate limiter
- Per-API-key rate limits
- Configurable windows (per minute, hour, day)
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- 429 Too Many Requests error handling

**2. Webhook Model & Management**
- New model: `Webhook`
  - Fields: id, tenant_id, name, url, events, secret, is_active, retry_count, last_triggered_at
  - Events: dashboard_created, query_executed, alert_triggered, export_completed, etc.
- Webhook signature (HMAC-SHA256) for security
- Retry logic with exponential backoff (3 attempts)

**3. Webhook Endpoints**
- `POST /api/webhooks/` - Create webhook
- `GET /api/webhooks/` - List webhooks
- `GET /api/webhooks/{id}` - Get webhook details
- `PUT /api/webhooks/{id}` - Update webhook
- `DELETE /api/webhooks/{id}` - Delete webhook
- `POST /api/webhooks/{id}/test` - Test webhook with sample payload

**4. Webhook Delivery Service**
- Background worker for webhook delivery
- Queue system (Redis queue)
- Retry failed deliveries
- Log delivery attempts and responses
- Webhook event model for history

#### Frontend Implementation (2 days)

**1. Webhooks Management Page**
- `/settings/webhooks` route
- List webhooks with status, last triggered
- Create webhook form:
  - Name, URL
  - Event selector (multi-select)
  - Secret key (auto-generated or custom)
  - Active toggle
- Test webhook button
- View delivery logs

**2. Webhook Logs Page**
- View webhook delivery history
- Request/response details
- Retry status
- Filter by webhook, event type, success/failure

#### Testing (1 day)
- Rate limiting tests (exceed limits)
- Webhook delivery tests
- Webhook signature verification tests
- Retry logic tests

---

### Week 3: Plugin System

#### Backend Implementation (3-4 days)

**1. Plugin Architecture**
- Plugin manifest schema (JSON):
  - name, version, author, description
  - entry_point, dependencies
  - permissions (required scopes)
  - configuration schema
- Plugin loader service
- Plugin registry (database)
- Sandboxed plugin execution (subprocess isolation)

**2. Plugin Types**

**A. Custom Visualization Plugins**
- Plugin interface: `VisualizationPlugin`
- Methods: `render(data, config)`, `validate_config(config)`
- Return format: JSON with chart configuration
- Frontend integration via dynamic imports

**B. Custom Data Source Connectors**
- Plugin interface: `DataSourcePlugin`
- Methods: `connect(credentials)`, `get_schema()`, `execute_query(sql)`
- Standard connection format
- Credential validation

**C. Data Transformation Plugins**
- Plugin interface: `TransformationPlugin`
- Methods: `transform(data, params)`
- Pre/post query transformations

**3. Plugin Management Endpoints**
- `POST /api/plugins/` - Upload plugin (zip file)
- `GET /api/plugins/` - List installed plugins
- `GET /api/plugins/{id}` - Get plugin details
- `PUT /api/plugins/{id}/enable` - Enable plugin
- `PUT /api/plugins/{id}/disable` - Disable plugin
- `DELETE /api/plugins/{id}` - Uninstall plugin
- `GET /api/plugins/marketplace` - List available plugins (future)

#### Frontend Implementation (2-3 days)

**1. Plugin Management Page**
- `/settings/plugins` route
- List installed plugins (name, version, author, status)
- Upload plugin form (drag-and-drop zip file)
- Enable/disable toggle
- Plugin configuration modal
- Uninstall with confirmation

**2. Plugin Marketplace (Basic)**
- Browse available plugins
- Search and filter
- Plugin details page
- One-click install

**3. Dynamic Plugin Integration**
- Custom visualization loader in chart components
- Custom data source selector
- Plugin-specific configuration UI

#### Testing (1 day)
- Plugin loading tests
- Sandboxing and security tests
- Custom visualization rendering tests
- Plugin API tests

---

## 🔒 PHASE 4.3: SECURITY & COMPLIANCE

**Timeline:** 3-4 weeks  
**Estimated Effort:** 120-160 hours  
**Priority:** CRITICAL - Required for enterprise customers

### Week 1: Row-Level & Column-Level Security

#### Backend Implementation (4-5 days)

**1. Row-Level Security (RLS) Engine**
- New model: `SecurityPolicy`
  - Fields: id, tenant_id, datasource_id, table_name, policy_name, rule, role
  - Rule format: SQL WHERE clause (e.g., `department = 'Sales'`)
- Policy evaluation engine
- Inject RLS filters into queries automatically
- User context: department, region, team_id, etc.

**2. Column-Level Security**
- New model: `ColumnPermission`
  - Fields: id, tenant_id, datasource_id, table_name, column_name, roles, mask_type
  - Mask types: HIDE, REDACT, HASH
- Filter columns from query results based on user role
- Data masking functions (partial email, phone number)

**3. Security Policy Management Endpoints**
- `POST /api/security/policies/` - Create security policy
- `GET /api/security/policies/` - List policies
- `PUT /api/security/policies/{id}` - Update policy
- `DELETE /api/security/policies/{id}` - Delete policy
- `POST /api/security/policies/test` - Test policy with sample data

**4. Data Masking Functions**
- Email masking: `j***@example.com`
- Phone masking: `***-***-1234`
- SSN masking: `***-**-1234`
- Custom regex-based masking

#### Frontend Implementation (2-3 days)

**1. Security Policies Page**
- `/settings/security/policies` route
- List policies by datasource and table
- Create policy form:
  - Datasource selector
  - Table selector
  - Policy name
  - Rule builder (visual or SQL)
  - Role selector
- Test policy with sample query

**2. Column Permissions Page**
- `/settings/security/columns` route
- Table view of columns with permissions
- Set visibility and masking per role
- Bulk edit for multiple columns

#### Testing (1 day)
- RLS filter injection tests
- Column masking tests
- Policy evaluation tests
- Permission bypass prevention tests

---

### Week 2: SSO Integration

#### Backend Implementation (4-5 days)

**1. OAuth 2.0 Integration**
- Providers: Google, Microsoft, GitHub
- OAuth flow implementation
- Token exchange and validation
- User profile mapping
- Account linking (existing users)

**2. SAML 2.0 Integration**
- SAML SP (Service Provider) implementation
- IdP (Identity Provider) metadata parsing
- Assertion validation
- User provisioning from SAML attributes
- Support for Azure AD, Okta, OneLogin

**3. LDAP/Active Directory Integration**
- LDAP connection and authentication
- User search and group membership
- Automatic role mapping from AD groups
- Periodic sync for user updates

**4. SSO Configuration Endpoints**
- `POST /api/auth/sso/oauth/` - Configure OAuth provider
- `POST /api/auth/sso/saml/` - Configure SAML provider
- `POST /api/auth/sso/ldap/` - Configure LDAP
- `GET /api/auth/sso/providers` - List configured providers
- `POST /api/auth/sso/{provider}/login` - Initiate SSO login
- `POST /api/auth/sso/{provider}/callback` - Handle SSO callback

#### Frontend Implementation (2 days)

**1. SSO Configuration Pages**
- `/settings/sso/oauth` - OAuth provider setup
- `/settings/sso/saml` - SAML configuration with metadata upload
- `/settings/sso/ldap` - LDAP connection settings

**2. SSO Login Integration**
- SSO buttons on login page
- Provider selection
- Redirect handling
- Account linking flow

#### Testing (1 day)
- OAuth flow tests
- SAML assertion validation tests
- LDAP authentication tests
- Account linking tests

---

### Week 3: Multi-Factor Authentication (MFA)

#### Backend Implementation (3-4 days)

**1. TOTP (Time-based One-Time Password)**
- Generate TOTP secrets (pyotp library)
- QR code generation for authenticator apps
- TOTP validation (6-digit codes)
- Backup codes generation (10 codes)

**2. MFA Model & Storage**
- New model: `MFADevice`
  - Fields: id, user_id, device_type, secret, is_verified, backup_codes, created_at
  - Device types: TOTP, SMS (future), Email (future)

**3. MFA Endpoints**
- `POST /api/auth/mfa/enable` - Enable MFA (returns QR code)
- `POST /api/auth/mfa/verify` - Verify TOTP code (first time)
- `POST /api/auth/mfa/disable` - Disable MFA
- `POST /api/auth/mfa/backup-codes` - Regenerate backup codes
- `POST /api/auth/mfa/validate` - Validate TOTP during login

**4. MFA-Protected Login Flow**
- Login step 1: Username + password
- Login step 2: TOTP code (if MFA enabled)
- Session management with MFA status

#### Frontend Implementation (2 days)

**1. MFA Setup Page**
- `/settings/security/mfa` route
- Enable MFA button
- QR code display for authenticator app
- Manual secret key display
- Verification code input
- Backup codes display (download, print)

**2. MFA Login Flow**
- Two-step login page
- TOTP code input
- "Use backup code" option
- "Trust this device" option (30 days)

#### Testing (1 day)
- TOTP generation and validation tests
- Backup code tests
- MFA-protected login tests
- Disable MFA tests

---

### Week 4: Audit Logs & Compliance

#### Backend Implementation (3-4 days)

**1. Comprehensive Audit Logging**
- New model: `AuditLog`
  - Fields: id, tenant_id, user_id, action, resource_type, resource_id, ip_address, user_agent, changes, timestamp
  - Actions: CREATE, READ, UPDATE, DELETE, LOGIN, LOGOUT, EXPORT, SHARE
  - Changes: JSON diff of before/after state

**2. Audit Logging Middleware**
- Automatic logging for all API endpoints
- Request/response logging
- Sensitive data redaction (passwords, tokens)
- User context capture

**3. Compliance Features**

**A. GDPR Compliance**
- Data export (all user data)
- Right to be forgotten (data deletion)
- Consent management
- Data retention policies
- Cookie consent

**B. HIPAA Compliance**
- Encrypted data at rest
- Access logging (who accessed what PHI)
- Automatic session timeout
- Password complexity requirements
- Audit trail retention (6 years)

**C. SOC 2 Controls**
- Access control evidence
- Change management logs
- Security incident logging
- User activity monitoring

**4. Audit Log Endpoints**
- `GET /api/audit/logs` - List audit logs (admin only)
- `GET /api/audit/logs/{id}` - Get audit log details
- `GET /api/audit/user/{user_id}` - Get user's audit trail
- `GET /api/audit/resource/{resource_type}/{resource_id}` - Get resource history
- `POST /api/audit/export` - Export audit logs (CSV, JSON)

#### Frontend Implementation (2 days)

**1. Audit Logs Page**
- `/admin/audit-logs` route (admin only)
- Table view with filters:
  - User, action, resource type, date range
  - IP address, success/failure
- Expandable rows for details
- Export button

**2. Compliance Dashboard**
- `/admin/compliance` route
- Compliance status indicators (GDPR, HIPAA, SOC 2)
- Key metrics (active users, data exports, security events)
- Compliance reports

**3. Data Export & Deletion**
- User profile page: "Export My Data" button
- User profile page: "Delete My Account" button
- Admin page: User data management

#### Testing (1 day)
- Audit logging tests (all actions)
- Data export tests
- Data deletion tests
- Compliance report tests

---

## 📊 PHASE 4.4: DATA GOVERNANCE

**Timeline:** 2-3 weeks  
**Estimated Effort:** 80-120 hours  
**Priority:** MEDIUM - Important for data-driven organizations

### Week 1: Data Catalog & Metadata Management

#### Backend Implementation (4-5 days)

**1. Data Catalog Model**
- New model: `DataAsset`
  - Fields: id, tenant_id, datasource_id, schema_name, table_name, asset_type, description, owner_id, steward_id, classification, tags, metadata
  - Asset types: TABLE, VIEW, QUERY, DASHBOARD, REPORT
  - Classification: PUBLIC, INTERNAL, CONFIDENTIAL, RESTRICTED

**2. Metadata Management**
- Column metadata:
  - Business name, description
  - Data type, format
  - Sample values
  - Null percentage, uniqueness
- Table metadata:
  - Row count, size
  - Last updated
  - Refresh frequency
  - Quality score

**3. Automatic Metadata Discovery**
- Background job to scan datasources
- Extract schema and statistics
- Detect data types and patterns
- Generate data quality metrics

**4. Data Catalog Endpoints**
- `POST /api/governance/catalog/assets/` - Create/update asset metadata
- `GET /api/governance/catalog/assets/` - Browse catalog
- `GET /api/governance/catalog/assets/{id}` - Get asset details
- `POST /api/governance/catalog/search` - Search catalog
- `PUT /api/governance/catalog/assets/{id}/classify` - Classify asset
- `POST /api/governance/catalog/scan` - Trigger metadata scan

#### Frontend Implementation (2 days)

**1. Data Catalog Page**
- `/governance/catalog` route
- Browse by datasource, schema, table
- Search with filters (name, classification, tags, owner)
- Asset details page:
  - Metadata display
  - Sample data preview
  - Related assets
  - Usage statistics

**2. Metadata Editor**
- Edit business names and descriptions
- Add tags and classifications
- Set owner and steward
- Add custom metadata fields

#### Testing (1 day)
- Metadata extraction tests
- Search functionality tests
- Classification tests

---

### Week 2: Data Lineage & Impact Analysis

#### Backend Implementation (4-5 days)

**1. Lineage Tracking Model**
- New model: `DataLineage`
  - Fields: id, tenant_id, source_asset_id, target_asset_id, transformation, relationship_type
  - Relationship types: DERIVED_FROM, USES, FEEDS_INTO, SIMILAR_TO

**2. Automatic Lineage Discovery**
- Parse SQL queries to extract:
  - Source tables
  - Target tables/views
  - Transformations (JOIN, WHERE, GROUP BY)
- Track dashboard → query → datasource relationships
- Track query dependencies

**3. Impact Analysis Engine**
- Analyze downstream impacts of changes
- Find all dashboards using a specific table
- Find all queries affected by column removal
- Dependency graph generation

**4. Lineage Endpoints**
- `GET /api/governance/lineage/{asset_id}` - Get asset lineage
- `GET /api/governance/lineage/{asset_id}/upstream` - Get upstream dependencies
- `GET /api/governance/lineage/{asset_id}/downstream` - Get downstream dependencies
- `POST /api/governance/lineage/impact-analysis` - Analyze impact of changes
- `POST /api/governance/lineage/refresh` - Refresh lineage

#### Frontend Implementation (2-3 days)

**1. Lineage Visualization Page**
- `/governance/lineage/{asset_id}` route
- Interactive lineage graph (D3.js or vis.js)
- Upstream and downstream views
- Node details on hover/click
- Filter by relationship type

**2. Impact Analysis Tool**
- Modal/page for impact analysis
- "What if" scenarios (e.g., "What if I delete this table?")
- List affected assets
- Risk assessment

#### Testing (1 day)
- Lineage extraction tests
- Impact analysis tests
- Graph generation tests

---

### Week 3: Data Classification & Approval Workflows

#### Backend Implementation (3-4 days)

**1. PII Detection & Classification**
- Automatic PII detection:
  - Email addresses
  - Phone numbers
  - SSN, credit cards
  - Names, addresses
- Regular expression patterns
- Machine learning-based detection (optional)
- Sensitivity scoring

**2. Classification Rules**
- New model: `ClassificationRule`
  - Fields: id, tenant_id, pattern, classification_level, auto_apply
- Pattern types: REGEX, COLUMN_NAME, DATA_TYPE, VALUE_PATTERN
- Auto-classify on scan

**3. Approval Workflow System**
- New model: `ApprovalRequest`
  - Fields: id, tenant_id, user_id, resource_type, resource_id, action, status, reviewer_id, reason, created_at
  - Actions: CREATE_DATASOURCE, EXPORT_DATA, SHARE_DASHBOARD, GRANT_ACCESS
  - Status: PENDING, APPROVED, REJECTED

**4. Workflow Endpoints**
- `POST /api/governance/approvals/` - Request approval
- `GET /api/governance/approvals/` - List pending approvals
- `POST /api/governance/approvals/{id}/approve` - Approve request
- `POST /api/governance/approvals/{id}/reject` - Reject request
- `GET /api/governance/approvals/my-requests` - User's requests

**5. Classification Endpoints**
- `POST /api/governance/classification/scan` - Scan for PII
- `GET /api/governance/classification/rules` - List classification rules
- `POST /api/governance/classification/rules` - Create rule

#### Frontend Implementation (2 days)

**1. Classification Dashboard**
- `/governance/classification` route
- PII detection results
- Classified assets by level
- Classification rules management

**2. Approval Workflows Page**
- `/governance/approvals` route
- Pending approvals (for reviewers)
- My approval requests
- Approval history
- Approve/reject with comments

#### Testing (1 day)
- PII detection tests
- Classification rule tests
- Approval workflow tests

---

## 🎛️ PHASE 4.5: ENTERPRISE ADMIN

**Timeline:** 2-3 weeks  
**Estimated Effort:** 80-120 hours  
**Priority:** MEDIUM - Operational excellence

### Week 1: System Monitoring & Performance Metrics

#### Backend Implementation (4-5 days)

**1. System Metrics Collection**
- New model: `SystemMetrics`
  - Fields: timestamp, cpu_usage, memory_usage, disk_usage, active_users, api_requests, query_count, cache_hit_rate
- Background worker collecting metrics every 60 seconds
- Time-series storage (Redis or InfluxDB)

**2. Performance Monitoring**
- Query performance tracking:
  - Execution time
  - Rows returned
  - Cache hits/misses
- API endpoint performance:
  - Response time (p50, p95, p99)
  - Error rate
  - Request count
- Dashboard load times

**3. Health Check System**
- Service health endpoints:
  - Database connections
  - Redis connection
  - External integrations
  - Disk space
  - Memory usage
- Automated health checks every 5 minutes
- Alert on failures

**4. Monitoring Endpoints**
- `GET /api/admin/metrics/system` - System metrics
- `GET /api/admin/metrics/queries` - Query performance stats
- `GET /api/admin/metrics/api` - API performance stats
- `GET /api/admin/health` - Health check
- `GET /api/admin/metrics/export` - Export metrics (Prometheus format)

#### Frontend Implementation (2-3 days)

**1. System Monitoring Dashboard**
- `/admin/monitoring` route
- Real-time system metrics (charts):
  - CPU, memory, disk usage
  - Active users
  - API requests per minute
  - Query execution time trends
- Service health status (green/yellow/red indicators)

**2. Performance Analytics**
- `/admin/performance` route
- Query performance leaderboard (slowest queries)
- API endpoint performance
- Cache effectiveness
- User activity heatmap

#### Testing (1 day)
- Metrics collection tests
- Health check tests
- Alert triggering tests

---

### Week 2: Advanced User Management & Usage Analytics

#### Backend Implementation (4-5 days)

**1. Advanced User Management**
- New model: `UserActivity`
  - Fields: id, user_id, action, resource, duration, timestamp
- User session tracking
- Login history with IP and location
- Failed login attempts tracking
- Account lockout after N failed attempts

**2. User Provisioning & De-provisioning**
- Bulk user import (CSV)
- Automated user creation from SSO
- User offboarding workflow:
  - Transfer ownership of assets
  - Archive user data
  - Revoke access
  - Export user activity

**3. Usage Analytics**
- New model: `TenantUsage`
  - Fields: tenant_id, date, user_count, query_count, dashboard_count, storage_used, api_calls
- Daily usage aggregation
- Billing calculations based on usage
- Usage trends and forecasting

**4. Advanced User Endpoints**
- `POST /api/admin/users/bulk-import` - Import users
- `POST /api/admin/users/{id}/offboard` - Offboard user
- `GET /api/admin/users/{id}/activity` - User activity history
- `GET /api/admin/users/{id}/sessions` - Active sessions
- `POST /api/admin/users/{id}/lock` - Lock user account
- `GET /api/admin/usage/tenant/{tenant_id}` - Tenant usage
- `GET /api/admin/usage/billing` - Billing report

#### Frontend Implementation (2 days)

**1. Advanced User Management Page**
- `/admin/users` route (enhanced)
- User table with advanced filters:
  - Last login, activity level, role, status
- Bulk actions (activate, deactivate, change role)
- User details modal:
  - Activity history
  - Active sessions
  - Owned assets
  - Usage statistics
- Offboarding workflow UI

**2. Usage Analytics Dashboard**
- `/admin/usage` route
- Tenant usage overview (charts):
  - Users over time
  - Queries per day
  - Storage growth
  - API usage
- Per-user usage breakdown
- Billing projections

#### Testing (1 day)
- Bulk import tests
- Offboarding workflow tests
- Usage calculation tests

---

### Week 3: Backup, Restore & Configuration Management

#### Backend Implementation (3-4 days)

**1. Automated Backup System**
- Backup strategies:
  - Full database backup (daily)
  - Incremental backups (hourly)
  - Configuration backups
- Backup storage:
  - Local filesystem
  - S3 compatible storage
  - Azure Blob Storage
- Encryption of backups (AES-256)

**2. Backup Model & Scheduling**
- New model: `BackupJob`
  - Fields: id, tenant_id, backup_type, status, file_path, size, started_at, completed_at
- Scheduled backups (cron-based)
- Retention policies (keep last 30 days, weekly for 3 months)

**3. Restore Functionality**
- Point-in-time restore
- Selective restore (specific tables/data)
- Restore validation
- Restore preview (dry-run)

**4. Configuration Management**
- Export tenant configuration (JSON)
- Import configuration
- Configuration versioning
- Configuration diff and rollback

**5. Backup & Config Endpoints**
- `POST /api/admin/backups/create` - Create manual backup
- `GET /api/admin/backups/` - List backups
- `POST /api/admin/backups/{id}/restore` - Restore from backup
- `POST /api/admin/backups/schedule` - Configure backup schedule
- `GET /api/admin/config/export` - Export configuration
- `POST /api/admin/config/import` - Import configuration
- `GET /api/admin/config/versions` - List config versions

#### Frontend Implementation (2-3 days)

**1. Backup Management Page**
- `/admin/backups` route
- List backups (date, size, type, status)
- Create manual backup button
- Restore modal:
  - Select backup
  - Choose restore scope
  - Confirm restore
- Backup schedule configuration

**2. Configuration Management Page**
- `/admin/configuration` route
- Export configuration button
- Import configuration (drag-and-drop JSON)
- Configuration history with diff viewer
- Rollback to previous configuration

#### Testing (1 day)
- Backup creation tests
- Restore tests
- Configuration import/export tests

---

## 📅 IMPLEMENTATION TIMELINE

### Month 1: API & Security Foundation
- **Week 1:** API Key Management System
- **Week 2:** Rate Limiting & Webhooks
- **Week 3:** Plugin System
- **Week 4:** Row-Level & Column-Level Security

### Month 2: Authentication & Governance
- **Week 5:** SSO Integration (OAuth, SAML, LDAP)
- **Week 6:** Multi-Factor Authentication
- **Week 7:** Audit Logs & Compliance
- **Week 8:** Data Catalog & Metadata Management

### Month 3: Advanced Features & Admin Tools
- **Week 9:** Data Lineage & Impact Analysis
- **Week 10:** Data Classification & Approval Workflows
- **Week 11:** System Monitoring & Performance Metrics
- **Week 12:** User Management, Usage Analytics, Backup & Restore

---

## 🎯 SUCCESS CRITERIA

### Phase 4.2: API & Extensibility ✓
- [ ] API key generation and management working
- [ ] Rate limiting enforced (429 responses)
- [ ] Webhooks deliver events successfully
- [ ] At least 1 custom plugin type working (visualization or data source)
- [ ] API documentation accessible and accurate

### Phase 4.3: Security & Compliance ✓
- [ ] RLS filters injected automatically in queries
- [ ] Column-level masking working
- [ ] SSO login successful (at least 1 provider)
- [ ] MFA enrollment and login working
- [ ] Audit logs capturing all user actions
- [ ] GDPR data export and deletion functional

### Phase 4.4: Data Governance ✓
- [ ] Data catalog with metadata searchable
- [ ] Lineage graph displays correctly
- [ ] PII detection identifies sensitive data
- [ ] Approval workflows enforce access control
- [ ] Impact analysis shows affected assets

### Phase 4.5: Enterprise Admin ✓
- [ ] System metrics dashboard shows real-time data
- [ ] Performance analytics identify slow queries
- [ ] Backup and restore tested successfully
- [ ] Usage analytics calculate correctly
- [ ] Advanced user management functional

---

## 🔧 TECHNICAL DEPENDENCIES

### New Python Packages Required
```txt
# Phase 4.2
slowapi==0.1.9              # Rate limiting
celery==5.3.6               # Background tasks for webhooks

# Phase 4.3
python-saml==1.16.0         # SAML SSO
ldap3==2.9.1                # LDAP integration
pyotp==2.9.0                # TOTP for MFA
pyqrcode==1.2.1             # QR code generation

# Phase 4.4
spacy==3.7.2                # NLP for PII detection (optional)
networkx==3.2.1             # Graph analysis for lineage

# Phase 4.5
prometheus-client==0.19.0   # Metrics export
influxdb-client==1.40.0     # Time-series metrics (optional)
```

### New Frontend Packages Required
```json
{
  "d3": "^7.8.5",                    // Lineage graph visualization
  "vis-network": "^9.1.9",           // Alternative graph library
  "react-qr-code": "^2.0.12",        // QR codes for MFA
  "react-syntax-highlighter": "^15.5.0", // Code examples in docs
  "monaco-diff-editor": "^0.45.0"    // Configuration diff viewer
}
```

---

## 💰 COST CONSIDERATIONS

### Infrastructure Costs (Monthly)
- Redis (for rate limiting, metrics): $10-50
- S3 Storage (backups): $5-20 per TB
- Email service (MFA, notifications): $0-20 (depends on volume)
- Monitoring tools (optional): $0-100

### Third-Party Services (Optional)
- SSO provider (if not using customer's IdP): $0 (self-hosted)
- Certificate management (Let's Encrypt): $0 (free)
- Audit log storage (long-term): S3 Glacier $1-5 per TB

---

## 🚀 DEPLOYMENT STRATEGY

### Week-by-Week Deployment
- **Weeks 1-4:** Deploy to staging, test thoroughly
- **Weeks 5-8:** Deploy to staging, security audit
- **Weeks 9-12:** Deploy to staging, load testing

### Production Rollout (After Month 3)
- Deploy Phase 4.2 features (API & Webhooks)
- Deploy Phase 4.3 features (Security & SSO)
- Deploy Phase 4.4 features (Governance)
- Deploy Phase 4.5 features (Admin Tools)

### Feature Flags
- Enable features per tenant (gradual rollout)
- A/B testing for new features
- Rollback capability if issues arise

---

## 📞 NEXT STEPS

1. **Review this plan** - Any questions or concerns?
2. **Prioritize features** - Want to reorder or skip any?
3. **Set timeline** - Confirm 10-12 week timeline or adjust?
4. **Allocate resources** - Full-time on this or parallel work?
5. **Start implementation** - Begin with Phase 4.2 Week 1?

---

**Ready to build enterprise-grade features? Let's make NexBII unstoppable! 🚀**
