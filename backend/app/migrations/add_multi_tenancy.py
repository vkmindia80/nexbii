"""
Database Migration: Add Multi-Tenancy Support
Adds tenant_id column to all existing models for tenant isolation.
"""

from sqlalchemy import Column, String, ForeignKey, Index
from app.core.database import Base, engine, SessionLocal
from app.models.user import User
from app.models.datasource import DataSource
from app.models.query import Query
from app.models.dashboard import Dashboard
from app.models.alert import Alert
from app.models.comment import Comment
from app.models.activity import Activity
from app.models.share import SharedDashboard
from app.models.subscription import EmailSubscription
from app.models.analytics import SavedAnalysis
from app.models.tenant import Tenant, TenantDomain, TenantInvitation, TenantUsage
import uuid


def add_tenant_id_column(table_name: str):
    """Add tenant_id column to existing table"""
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        # Check if column already exists
        result = db.execute(text(f"PRAGMA table_info({table_name})"))
        columns = [row[1] for row in result]
        
        if 'tenant_id' not in columns:
            print(f"Adding tenant_id to {table_name}...")
            db.execute(text(f"""
                ALTER TABLE {table_name}
                ADD COLUMN tenant_id VARCHAR
            """))
            
            # Create index for performance
            db.execute(text(f"""
                CREATE INDEX IF NOT EXISTS idx_{table_name}_tenant_id
                ON {table_name}(tenant_id)
            """))
            
            db.commit()
            print(f"✅ Added tenant_id to {table_name}")
        else:
            print(f"⏭️  tenant_id already exists in {table_name}")
    
    except Exception as e:
        print(f"⚠️  Error adding tenant_id to {table_name}: {e}")
        db.rollback()
    finally:
        db.close()


def create_default_tenant():
    """Create a default tenant for existing data"""
    db = SessionLocal()
    try:
        # Check if default tenant exists
        default_tenant = db.query(Tenant).filter(Tenant.slug == "default").first()
        
        if not default_tenant:
            print("Creating default tenant...")
            default_tenant = Tenant(
                id=str(uuid.uuid4()),
                name="Default Organization",
                slug="default",
                contact_email="admin@example.com",
                contact_name="System Admin",
                plan="enterprise",  # Give full access to existing data
                is_active=True,
                max_users=1000,
                max_datasources=100,
                max_dashboards=500,
                max_queries=10000,
                storage_limit_mb=100000,
                features={
                    "ai_enabled": True,
                    "advanced_analytics": True,
                    "white_labeling": True,
                    "api_access": True
                }
            )
            db.add(default_tenant)
            db.commit()
            db.refresh(default_tenant)
            print(f"✅ Created default tenant: {default_tenant.id}")
            return default_tenant.id
        else:
            print(f"⏭️  Default tenant already exists: {default_tenant.id}")
            return default_tenant.id
    
    except Exception as e:
        print(f"⚠️  Error creating default tenant: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def migrate_existing_data(default_tenant_id: str):
    """Assign existing data to default tenant"""
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        tables_to_migrate = [
            'users',
            'datasources',
            'queries',
            'dashboards',
            'alerts',
            'comments',
            'activities',
            'shared_dashboards',
            'email_subscriptions',
            'saved_analyses'
        ]
        
        for table in tables_to_migrate:
            print(f"Migrating {table} to default tenant...")
            result = db.execute(text(f"""
                UPDATE {table}
                SET tenant_id = :tenant_id
                WHERE tenant_id IS NULL
            """), {"tenant_id": default_tenant_id})
            
            count = result.rowcount
            db.commit()
            print(f"✅ Migrated {count} rows in {table}")
    
    except Exception as e:
        print(f"⚠️  Error migrating data: {e}")
        db.rollback()
    finally:
        db.close()


def run_migration():
    """Run the complete migration"""
    print("=" * 60)
    print("🚀 Starting Multi-Tenancy Migration")
    print("=" * 60)
    
    # Step 1: Create tenant tables
    print("\n1️⃣  Creating tenant tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tenant tables created")
    
    # Step 2: Create default tenant
    print("\n2️⃣  Creating default tenant...")
    default_tenant_id = create_default_tenant()
    
    if not default_tenant_id:
        print("❌ Migration failed: Could not create default tenant")
        return
    
    # Step 3: Add tenant_id columns to existing tables
    print("\n3️⃣  Adding tenant_id columns...")
    tables_to_update = [
        'users',
        'datasources',
        'queries',
        'dashboards',
        'alerts',
        'comments',
        'activities',
        'shared_dashboards',
        'email_subscriptions',
        'saved_analyses'
    ]
    
    for table in tables_to_update:
        add_tenant_id_column(table)
    
    # Step 4: Migrate existing data
    print("\n4️⃣  Migrating existing data to default tenant...")
    migrate_existing_data(default_tenant_id)
    
    print("\n" + "=" * 60)
    print("🎉 Migration Complete!")
    print("=" * 60)
    print(f"\nDefault Tenant ID: {default_tenant_id}")
    print("All existing data has been migrated to the default tenant.")
    print("\nNext steps:")
    print("1. Update User model to include tenant_id")
    print("2. Update all other models to include tenant_id")
    print("3. Add tenant context middleware to server.py")
    print("4. Test multi-tenant isolation")


if __name__ == "__main__":
    run_migration()
