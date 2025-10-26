"""
Security Models for Phase 4.3
Includes RLS, CLS, Data Masking, SSO, MFA, Audit Logs, and Compliance
"""

from sqlalchemy import Column, String, Boolean, Integer, JSON, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
import enum


class PolicyType(str, enum.Enum):
    """Types of security policies"""
    ROW_LEVEL = "row_level"
    COLUMN_LEVEL = "column_level"


class DataClassificationType(str, enum.Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    PII = "pii"  # Personally Identifiable Information
    PHI = "phi"  # Protected Health Information
    PCI = "pci"  # Payment Card Industry


class AuditEventCategory(str, enum.Enum):
    """Categories for audit events"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SECURITY_CHANGE = "security_change"
    USER_MANAGEMENT = "user_management"
    SYSTEM = "system"
    COMPLIANCE = "compliance"


class SecurityPolicy(Base):
    """
    Security policies for Row-Level and Column-Level Security
    """
    __tablename__ = "security_policies"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    policy_type = Column(Enum(PolicyType), nullable=False)
    
    # Policy rules as JSON
    # For RLS: {"conditions": [{"field": "user_id", "operator": "equals", "value": "{{current_user.id}}"}]}
    # For CLS: {"columns": ["email", "ssn"], "action": "mask", "except_roles": ["admin"]}
    rules = Column(JSON, nullable=False)
    
    # Applies to specific resource types (datasource, query, dashboard, etc.)
    resource_type = Column(String)
    resource_id = Column(String, nullable=True)  # Null means applies to all
    
    # Applies to users/roles
    applies_to_users = Column(JSON, default=[])  # List of user IDs
    applies_to_roles = Column(JSON, default=[])  # List of roles
    
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority evaluated first
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    created_by = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="security_policies")
    creator = relationship("User", foreign_keys=[created_by])


class DataMaskingRule(Base):
    """
    Rules for masking sensitive data (PII, PHI, etc.)
    """
    __tablename__ = "data_masking_rules"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    # What type of data to mask
    data_type = Column(String, nullable=False)  # email, phone, ssn, credit_card, etc.
    
    # Masking pattern
    # Examples: "***@***.com", "(***) ***-1234", "***-**-1234"
    masking_pattern = Column(String, nullable=False)
    
    # Regex pattern to detect this data type
    detection_regex = Column(String)
    
    is_active = Column(Boolean, default=True)
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="data_masking_rules")


class DataClassification(Base):
    """
    Classification of data columns for compliance
    """
    __tablename__ = "data_classifications"

    id = Column(String, primary_key=True)
    datasource_id = Column(String, ForeignKey("datasources.id", ondelete="CASCADE"))
    table_name = Column(String, nullable=False)
    column_name = Column(String, nullable=False)
    
    classification = Column(Enum(DataClassificationType), nullable=False)
    
    # Associated masking rule
    masking_rule_id = Column(String, ForeignKey("data_masking_rules.id"), nullable=True)
    
    # Additional metadata
    description = Column(Text)
    detected_by = Column(String)  # "auto" or "manual"
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    classified_by = Column(String, ForeignKey("users.id"))
    classified_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant")
    datasource = relationship("DataSource")
    masking_rule = relationship("DataMaskingRule")
    classifier = relationship("User", foreign_keys=[classified_by])


class OAuthProvider(Base):
    """
    OAuth 2.0 provider configuration for SSO
    """
    __tablename__ = "oauth_providers"

    id = Column(String, primary_key=True)
    provider_name = Column(String, nullable=False)  # google, microsoft, github, etc.
    display_name = Column(String, nullable=False)
    
    # OAuth configuration
    client_id = Column(String, nullable=False)
    client_secret = Column(String, nullable=False)  # Encrypted
    
    authorize_url = Column(String, nullable=False)
    token_url = Column(String, nullable=False)
    user_info_url = Column(String, nullable=False)
    
    scopes = Column(JSON, default=["openid", "email", "profile"])
    
    # User mapping
    # Maps OAuth user fields to our user fields
    # Example: {"email": "email", "name": "name", "picture": "avatar_url"}
    user_field_mapping = Column(JSON, default={})
    
    is_enabled = Column(Boolean, default=True)
    allow_sign_up = Column(Boolean, default=True)  # Auto-create users on first login
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="oauth_providers")


class SAMLConfig(Base):
    """
    SAML 2.0 IdP configuration for enterprise SSO
    """
    __tablename__ = "saml_configs"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    
    # Identity Provider configuration
    idp_entity_id = Column(String, nullable=False)
    sso_url = Column(String, nullable=False)  # IdP Single Sign-On URL
    slo_url = Column(String, nullable=True)  # Single Logout URL (optional)
    x509_cert = Column(Text, nullable=False)  # IdP public certificate
    
    # Service Provider (us) configuration
    sp_entity_id = Column(String, nullable=False)
    sp_acs_url = Column(String, nullable=False)  # Assertion Consumer Service URL
    sp_slo_url = Column(String, nullable=True)
    
    # SAML settings
    name_id_format = Column(String, default="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress")
    
    # Attribute mapping
    # Maps SAML attributes to user fields
    attribute_mapping = Column(JSON, default={
        "email": "email",
        "firstName": "first_name",
        "lastName": "last_name"
    })
    
    is_enabled = Column(Boolean, default=True)
    allow_sign_up = Column(Boolean, default=True)
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="saml_configs")


class LDAPConfig(Base):
    """
    LDAP/Active Directory configuration
    """
    __tablename__ = "ldap_configs"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    
    # Connection settings
    server_url = Column(String, nullable=False)  # ldap://domain.com:389 or ldaps://domain.com:636
    bind_dn = Column(String, nullable=False)  # CN=admin,DC=domain,DC=com
    bind_password = Column(String, nullable=False)  # Encrypted
    
    # Search settings
    search_base = Column(String, nullable=False)  # DC=domain,DC=com
    user_filter = Column(String, default="(objectClass=person)")
    user_search_filter = Column(String, default="(uid={username})")  # Or (sAMAccountName={username})
    
    # Attribute mapping
    attribute_mapping = Column(JSON, default={
        "username": "uid",
        "email": "mail",
        "first_name": "givenName",
        "last_name": "sn",
        "full_name": "cn"
    })
    
    # Group mapping to roles
    group_mapping = Column(JSON, default={})  # {"CN=Admins,DC=domain,DC=com": "admin"}
    
    # SSL/TLS settings
    use_ssl = Column(Boolean, default=False)
    verify_certificate = Column(Boolean, default=True)
    
    is_enabled = Column(Boolean, default=True)
    allow_sign_up = Column(Boolean, default=True)
    
    # Sync settings
    auto_sync_users = Column(Boolean, default=False)
    sync_interval_hours = Column(Integer, default=24)
    last_sync_at = Column(DateTime, nullable=True)
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="ldap_configs")


class MFAConfig(Base):
    """
    Multi-Factor Authentication configuration per user
    """
    __tablename__ = "mfa_configs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # TOTP settings
    secret_key = Column(String, nullable=False)  # Encrypted
    
    # Backup codes (one-time use)
    backup_codes = Column(JSON, default=[])  # List of encrypted backup codes
    
    is_enabled = Column(Boolean, default=False)
    enrollment_completed = Column(Boolean, default=False)
    
    # Tracking
    enrolled_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    failed_attempts = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="mfa_config")


class AuditLog(Base):
    """
    Comprehensive audit logging for compliance and security
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    
    # Event information
    event_type = Column(String, nullable=False)  # login, logout, query_executed, dashboard_viewed, etc.
    event_category = Column(Enum(AuditEventCategory), nullable=False)
    
    # User context
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    username = Column(String)  # Denormalized for faster queries
    user_role = Column(String)
    
    # Request context
    ip_address = Column(String)
    user_agent = Column(String)
    request_method = Column(String)
    request_path = Column(String)
    
    # Resource information
    resource_type = Column(String, nullable=True)  # datasource, query, dashboard, user, etc.
    resource_id = Column(String, nullable=True)
    resource_name = Column(String, nullable=True)
    
    # Action details
    action = Column(String, nullable=False)  # create, read, update, delete, execute, export, etc.
    status = Column(String, nullable=False)  # success, failure, denied
    
    # Additional details
    details = Column(JSON, default={})  # Any additional context
    error_message = Column(Text, nullable=True)
    
    # Performance
    duration_ms = Column(Integer, nullable=True)
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")


class ConsentRecord(Base):
    """
    GDPR consent management
    """
    __tablename__ = "consent_records"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Consent type
    consent_type = Column(String, nullable=False)  # terms_of_service, privacy_policy, marketing, etc.
    version = Column(String, nullable=False)  # Policy version
    
    # Consent status
    is_granted = Column(Boolean, default=False)
    granted_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    
    # Tracking
    ip_address = Column(String)
    user_agent = Column(String)
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User", back_populates="consent_records")


class SessionLog(Base):
    """
    Session tracking for security and compliance
    """
    __tablename__ = "session_logs"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Session information
    session_token = Column(String, unique=True, index=True)
    ip_address = Column(String)
    user_agent = Column(String)
    
    # Session lifecycle
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    logout_reason = Column(String, nullable=True)  # manual, timeout, forced, etc.
    
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"))
    
    # Relationships
    tenant = relationship("Tenant")
    user = relationship("User")


# Update relationships in existing models
# This will be added to the respective model files

def update_tenant_relationships():
    """
    Add these relationships to app/models/tenant.py Tenant class:
    """
    """
    security_policies = relationship("SecurityPolicy", back_populates="tenant", cascade="all, delete-orphan")
    data_masking_rules = relationship("DataMaskingRule", back_populates="tenant", cascade="all, delete-orphan")
    oauth_providers = relationship("OAuthProvider", back_populates="tenant", cascade="all, delete-orphan")
    saml_configs = relationship("SAMLConfig", back_populates="tenant", cascade="all, delete-orphan")
    ldap_configs = relationship("LDAPConfig", back_populates="tenant", cascade="all, delete-orphan")
    """
    pass


def update_user_relationships():
    """
    Add these relationships to app/models/user.py User class:
    """
    """
    mfa_config = relationship("MFAConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    consent_records = relationship("ConsentRecord", back_populates="user", cascade="all, delete-orphan")
    """
    pass
