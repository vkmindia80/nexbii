"""
LDAP/Active Directory Service
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.security import LDAPConfig
from app.models.user import User, UserRole
import uuid

# Note: For production, use ldap3 library
# This is a mock implementation for demo purposes

class LDAPService:
    """Service for LDAP/Active Directory authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_config(self, config_id: str) -> Optional[LDAPConfig]:
        """Get LDAP config by ID"""
        return self.db.query(LDAPConfig).filter(
            LDAPConfig.id == config_id,
            LDAPConfig.is_enabled == True
        ).first()
    
    def get_config_by_tenant(self, tenant_id: str) -> Optional[LDAPConfig]:
        """Get LDAP config for tenant"""
        return self.db.query(LDAPConfig).filter(
            LDAPConfig.tenant_id == tenant_id,
            LDAPConfig.is_enabled == True
        ).first()
    
    def create_config(self, tenant_id: str, config_data: Dict[str, Any]) -> LDAPConfig:
        """Create LDAP configuration"""
        config = LDAPConfig(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            **config_data
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def test_connection(self, config: LDAPConfig) -> Dict[str, Any]:
        """Test LDAP connection"""
        # This would actually connect to LDAP server
        # For demo purposes, returning mock success
        try:
            # In production:
            # from ldap3 import Server, Connection
            # server = Server(config.server_url, use_ssl=config.use_ssl)
            # conn = Connection(server, config.bind_dn, config.bind_password)
            # conn.bind()
            
            return {
                "success": True,
                "message": "LDAP connection successful (mock)"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"LDAP connection failed: {str(e)}"
            }
    
    def authenticate_user(
        self, config: LDAPConfig, username: str, password: str
    ) -> Optional[Dict[str, Any]]:
        """Authenticate user against LDAP"""
        # This would perform LDAP authentication
        # For demo purposes, returning mock user data
        try:
            # In production:
            # from ldap3 import Server, Connection
            # server = Server(config.server_url, use_ssl=config.use_ssl)
            # user_dn = config.user_search_filter.replace("{username}", username)
            # conn = Connection(server, user_dn, password)
            # if conn.bind():
            #     return self._get_user_attributes(conn, user_dn, config)
            
            # Mock successful authentication
            return {
                "uid": username,
                "mail": f"{username}@company.com",
                "givenName": "Demo",
                "sn": "User",
                "cn": "Demo User"
            }
        except Exception:
            return None
    
    def sync_users(self, config: LDAPConfig) -> Dict[str, Any]:
        """Sync users from LDAP to local database"""
        # This would fetch all users from LDAP and sync
        # For demo purposes, returning mock results
        try:
            # In production:
            # from ldap3 import Server, Connection
            # Perform LDAP search and sync users
            
            return {
                "success": True,
                "synced_users": 0,
                "created_users": 0,
                "updated_users": 0,
                "message": "User sync completed (mock)"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"User sync failed: {str(e)}"
            }
    
    def map_user_data(
        self, config: LDAPConfig, ldap_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map LDAP attributes to our user model"""
        mapping = config.attribute_mapping or {}
        
        email = ldap_attributes.get(mapping.get("email", "mail"))
        first_name = ldap_attributes.get(mapping.get("first_name", "givenName"), "")
        last_name = ldap_attributes.get(mapping.get("last_name", "sn"), "")
        
        return {
            "email": email,
            "full_name": f"{first_name} {last_name}".strip()
        }
    
    def get_user_role(
        self, config: LDAPConfig, ldap_attributes: Dict[str, Any]
    ) -> str:
        """Determine user role based on LDAP groups"""
        # Map LDAP groups to roles
        group_mapping = config.group_mapping or {}
        
        # In production, get user's groups from LDAP
        # user_groups = ldap_attributes.get("memberOf", [])
        
        # For demo, return default role
        return UserRole.VIEWER
    
    def find_or_create_user(
        self, config: LDAPConfig, ldap_attributes: Dict[str, Any]
    ) -> Optional[User]:
        """Find existing user or create new one from LDAP data"""
        user_data = self.map_user_data(config, ldap_attributes)
        email = user_data.get("email")
        
        if not email:
            return None
        
        # Find existing user
        user = self.db.query(User).filter(
            User.email == email,
            User.tenant_id == config.tenant_id
        ).first()
        
        if user:
            return user
        
        # Create new user if allowed
        if not config.allow_sign_up:
            return None
        
        from app.core.security import get_password_hash
        import secrets
        
        role = self.get_user_role(config, ldap_attributes)
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=user_data.get("full_name", email),
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=role,
            is_active=True,
            tenant_id=config.tenant_id
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
