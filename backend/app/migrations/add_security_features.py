"""
Database migration for Phase 4.3 - Security & Compliance
Adds tables for RLS, CLS, SSO, MFA, Audit Logs, and Compliance
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.database import Base
from app.core.config import settings
from app.models.security import (
    SecurityPolicy,
    DataMaskingRule,
    DataClassification,
    OAuthProvider,
    SAMLConfig,
    LDAPConfig,
    MFAConfig,
    AuditLog,
    ConsentRecord,
    SessionLog
)
from app.models.tenant import Tenant
from app.models.user import User

def run_migration():
    """Create security-related tables"""
    print("🔐 Starting Phase 4.3 Security Features Migration...")
    
    # Use the same engine logic as the app (PostgreSQL with SQLite fallback)
    from app.core.database import engine as app_engine
    engine = app_engine
    
    print(f"Using database: {engine.url}")
    
    try:
        # Create all security tables
        print("Creating security tables...")
        Base.metadata.create_all(bind=engine, tables=[
            SecurityPolicy.__table__,
            DataMaskingRule.__table__,
            DataClassification.__table__,
            OAuthProvider.__table__,
            SAMLConfig.__table__,
            LDAPConfig.__table__,
            MFAConfig.__table__,
            AuditLog.__table__,
            ConsentRecord.__table__,
            SessionLog.__table__,
        ])
        
        print("✅ Security tables created successfully!")
        
        # Verify tables
        print("\n📋 Created tables:")
        print("  - security_policies (RLS & CLS)")
        print("  - data_masking_rules (PII masking)")
        print("  - data_classifications (Data tagging)")
        print("  - oauth_providers (OAuth 2.0 SSO)")
        print("  - saml_configs (SAML 2.0 SSO)")
        print("  - ldap_configs (LDAP/AD SSO)")
        print("  - mfa_configs (Multi-Factor Auth)")
        print("  - audit_logs (Comprehensive logging)")
        print("  - consent_records (GDPR compliance)")
        print("  - session_logs (Session tracking)")
        
        print("\n✅ Phase 4.3 Security Migration Complete!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        engine.dispose()

if __name__ == "__main__":
    run_migration()
