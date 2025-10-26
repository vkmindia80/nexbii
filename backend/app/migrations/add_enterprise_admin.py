"""
Migration script for Phase 4.5 - Enterprise Admin
Adds admin models: SystemMetrics, UserActivity, UserSession, TenantUsageMetrics,
BackupJob, ConfigurationVersion, SystemHealthCheck
"""
import sys
import os

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.core.database import engine, Base
from app.models.admin import (
    SystemMetrics, UserActivity, UserSession, TenantUsageMetrics,
    BackupJob, ConfigurationVersion, SystemHealthCheck
)

def run_migration():
    """
    Create admin tables in the database
    """
    print("🚀 Starting Phase 4.5 Enterprise Admin migration...")
    
    try:
        # Create all admin tables
        Base.metadata.create_all(bind=engine, tables=[
            SystemMetrics.__table__,
            UserActivity.__table__,
            UserSession.__table__,
            TenantUsageMetrics.__table__,
            BackupJob.__table__,
            ConfigurationVersion.__table__,
            SystemHealthCheck.__table__,
        ])
        
        print("✅ Admin tables created successfully:")
        print("   - system_metrics")
        print("   - user_activities")
        print("   - user_sessions")
        print("   - tenant_usage_metrics")
        print("   - backup_jobs")
        print("   - configuration_versions")
        print("   - system_health_checks")
        print("\n🎉 Phase 4.5 migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == "__main__":
    run_migration()
