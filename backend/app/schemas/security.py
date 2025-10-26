"""
Pydantic Schemas for Security & Compliance (Phase 4.3)
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ===== Enums =====

class PolicyType(str, Enum):
    ROW_LEVEL = "row_level"
    COLUMN_LEVEL = "column_level"


class DataClassificationType(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    PII = "pii"
    PHI = "phi"
    PCI = "pci"


class AuditEventCategory(str, Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_CHANGE = "security_change"
    USER_MANAGEMENT = "user_management"
    SYSTEM = "system"
    COMPLIANCE = "compliance"


# ===== Security Policy Schemas =====

class SecurityPolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    policy_type: PolicyType
    rules: Dict[str, Any]
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    applies_to_users: List[str] = []
    applies_to_roles: List[str] = []
    is_active: bool = True
    priority: int = 0


class SecurityPolicyCreate(SecurityPolicyBase):
    pass


class SecurityPolicyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    applies_to_users: Optional[List[str]] = None
    applies_to_roles: Optional[List[str]] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class SecurityPolicyResponse(SecurityPolicyBase):
    id: str
    tenant_id: str
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== Data Masking Schemas =====

class DataMaskingRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    data_type: str  # email, phone, ssn, credit_card, etc.
    masking_pattern: str
    detection_regex: Optional[str] = None
    is_active: bool = True


class DataMaskingRuleCreate(DataMaskingRuleBase):
    pass


class DataMaskingRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    data_type: Optional[str] = None
    masking_pattern: Optional[str] = None
    detection_regex: Optional[str] = None
    is_active: Optional[bool] = None


class DataMaskingRuleResponse(DataMaskingRuleBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== Data Classification Schemas =====

class DataClassificationBase(BaseModel):
    datasource_id: str
    table_name: str
    column_name: str
    classification: DataClassificationType
    masking_rule_id: Optional[str] = None
    description: Optional[str] = None
    detected_by: Optional[str] = "manual"


class DataClassificationCreate(DataClassificationBase):
    pass


class DataClassificationUpdate(BaseModel):
    classification: Optional[DataClassificationType] = None
    masking_rule_id: Optional[str] = None
    description: Optional[str] = None


class DataClassificationResponse(DataClassificationBase):
    id: str
    tenant_id: str
    classified_by: str
    classified_at: datetime

    class Config:
        from_attributes = True


# ===== OAuth Provider Schemas =====

class OAuthProviderBase(BaseModel):
    provider_name: str
    display_name: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    user_info_url: str
    scopes: List[str] = ["openid", "email", "profile"]
    user_field_mapping: Dict[str, str] = {}
    is_enabled: bool = True
    allow_sign_up: bool = True


class OAuthProviderCreate(OAuthProviderBase):
    pass


class OAuthProviderUpdate(BaseModel):
    display_name: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    authorize_url: Optional[str] = None
    token_url: Optional[str] = None
    user_info_url: Optional[str] = None
    scopes: Optional[List[str]] = None
    user_field_mapping: Optional[Dict[str, str]] = None
    is_enabled: Optional[bool] = None
    allow_sign_up: Optional[bool] = None


class OAuthProviderResponse(BaseModel):
    id: str
    provider_name: str
    display_name: str
    client_id: str
    authorize_url: str
    token_url: str
    user_info_url: str
    scopes: List[str]
    user_field_mapping: Dict[str, str]
    is_enabled: bool
    allow_sign_up: bool
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== SAML Schemas =====

class SAMLConfigBase(BaseModel):
    name: str
    idp_entity_id: str
    sso_url: str
    slo_url: Optional[str] = None
    x509_cert: str
    sp_entity_id: str
    sp_acs_url: str
    sp_slo_url: Optional[str] = None
    name_id_format: str = "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress"
    attribute_mapping: Dict[str, str] = {
        "email": "email",
        "firstName": "first_name",
        "lastName": "last_name"
    }
    is_enabled: bool = True
    allow_sign_up: bool = True


class SAMLConfigCreate(SAMLConfigBase):
    pass


class SAMLConfigUpdate(BaseModel):
    name: Optional[str] = None
    idp_entity_id: Optional[str] = None
    sso_url: Optional[str] = None
    slo_url: Optional[str] = None
    x509_cert: Optional[str] = None
    sp_entity_id: Optional[str] = None
    sp_acs_url: Optional[str] = None
    sp_slo_url: Optional[str] = None
    name_id_format: Optional[str] = None
    attribute_mapping: Optional[Dict[str, str]] = None
    is_enabled: Optional[bool] = None
    allow_sign_up: Optional[bool] = None


class SAMLConfigResponse(SAMLConfigBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== LDAP Schemas =====

class LDAPConfigBase(BaseModel):
    name: str
    server_url: str
    bind_dn: str
    bind_password: str
    search_base: str
    user_filter: str = "(objectClass=person)"
    user_search_filter: str = "(uid={username})"
    attribute_mapping: Dict[str, str] = {
        "username": "uid",
        "email": "mail",
        "first_name": "givenName",
        "last_name": "sn",
        "full_name": "cn"
    }
    group_mapping: Dict[str, str] = {}
    use_ssl: bool = False
    verify_certificate: bool = True
    is_enabled: bool = True
    allow_sign_up: bool = True
    auto_sync_users: bool = False
    sync_interval_hours: int = 24


class LDAPConfigCreate(LDAPConfigBase):
    pass


class LDAPConfigUpdate(BaseModel):
    name: Optional[str] = None
    server_url: Optional[str] = None
    bind_dn: Optional[str] = None
    bind_password: Optional[str] = None
    search_base: Optional[str] = None
    user_filter: Optional[str] = None
    user_search_filter: Optional[str] = None
    attribute_mapping: Optional[Dict[str, str]] = None
    group_mapping: Optional[Dict[str, str]] = None
    use_ssl: Optional[bool] = None
    verify_certificate: Optional[bool] = None
    is_enabled: Optional[bool] = None
    allow_sign_up: Optional[bool] = None
    auto_sync_users: Optional[bool] = None
    sync_interval_hours: Optional[int] = None


class LDAPConfigResponse(LDAPConfigBase):
    id: str
    tenant_id: str
    last_sync_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ===== MFA Schemas =====

class MFAEnrollmentRequest(BaseModel):
    pass  # Just initiates enrollment


class MFAEnrollmentResponse(BaseModel):
    secret_key: str
    qr_code_url: str
    backup_codes: List[str]


class MFAVerifyEnrollmentRequest(BaseModel):
    code: str


class MFAVerifyRequest(BaseModel):
    code: str


class MFADisableRequest(BaseModel):
    password: str


class MFAStatusResponse(BaseModel):
    is_enabled: bool
    enrollment_completed: bool
    enrolled_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


class MFAEnforcementPolicyUpdate(BaseModel):
    enforce_for_roles: List[str] = []
    enforce_for_all: bool = False


# ===== Audit Log Schemas =====

class AuditLogCreate(BaseModel):
    event_type: str
    event_category: AuditEventCategory
    user_id: Optional[str] = None
    username: Optional[str] = None
    user_role: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    action: str
    status: str
    details: Dict[str, Any] = {}
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None


class AuditLogResponse(AuditLogCreate):
    id: str
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogFilters(BaseModel):
    event_category: Optional[AuditEventCategory] = None
    event_type: Optional[str] = None
    user_id: Optional[str] = None
    resource_type: Optional[str] = None
    action: Optional[str] = None
    status: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    skip: int = 0
    limit: int = 100


# ===== Consent Schemas =====

class ConsentRecordBase(BaseModel):
    consent_type: str
    version: str
    is_granted: bool


class ConsentRecordCreate(ConsentRecordBase):
    pass


class ConsentRecordUpdate(BaseModel):
    is_granted: bool


class ConsentRecordResponse(ConsentRecordBase):
    id: str
    user_id: str
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    tenant_id: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== GDPR Schemas =====

class GDPRDataExportRequest(BaseModel):
    include_data_sources: bool = True
    include_queries: bool = True
    include_dashboards: bool = True
    include_activity_logs: bool = True


class GDPRDataExportResponse(BaseModel):
    export_id: str
    download_url: str
    expires_at: datetime


class GDPRDeleteRequest(BaseModel):
    confirmation: str = Field(..., description="Must be 'DELETE MY DATA'")
    
    @validator('confirmation')
    def validate_confirmation(cls, v):
        if v != "DELETE MY DATA":
            raise ValueError("Confirmation must be exactly 'DELETE MY DATA'")
        return v


# ===== Compliance Report Schemas =====

class ComplianceReportRequest(BaseModel):
    report_type: str  # soc2, gdpr, hipaa
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None


class ComplianceReportResponse(BaseModel):
    report_type: str
    generated_at: datetime
    summary: Dict[str, Any]
    details: Dict[str, Any]


# ===== Session Schemas =====

class SessionLogResponse(BaseModel):
    id: str
    user_id: str
    ip_address: str
    user_agent: str
    started_at: datetime
    last_activity_at: datetime
    ended_at: Optional[datetime] = None
    is_active: bool
    logout_reason: Optional[str] = None

    class Config:
        from_attributes = True


# ===== Policy Testing Schemas =====

class PolicyTestRequest(BaseModel):
    policy_id: str
    test_user_id: str
    test_resource_id: Optional[str] = None
    test_data: Optional[Dict[str, Any]] = None


class PolicyTestResponse(BaseModel):
    policy_applied: bool
    filtered_data: Optional[Dict[str, Any]] = None
    explanation: str
