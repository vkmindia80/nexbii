#!/usr/bin/env python3
"""
Database initialization script
Creates default demo user if it doesn't exist
"""

from app.core.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.core.security import get_password_hash
import uuid

def init_database():
    """Initialize database with tables and default data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if demo user exists
        demo_user = db.query(User).filter(User.email == 'admin@nexbii.demo').first()
        
        if not demo_user:
            # Create demo admin user
            demo_user = User(
                id=str(uuid.uuid4()),
                email='admin@nexbii.demo',
                hashed_password=get_password_hash('demo123'),
                full_name='Demo Admin',
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            print('✅ Demo user created successfully!')
            print('   Email: admin@nexbii.demo')
            print('   Password: demo123')
        else:
            print('✅ Demo user already exists')
        
        # Count total users
        user_count = db.query(User).count()
        print(f'📊 Total users in database: {user_count}')
        
    except Exception as e:
        print(f'❌ Error initializing database: {e}')
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    init_database()
