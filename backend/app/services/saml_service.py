"""
SAML 2.0 Service for Enterprise SSO
"""

from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.security import SAMLConfig
from app.models.user import User, UserRole
import uuid

# Note: For production, use python3-saml library
# This is a mock implementation for demo purposes

class SAMLService:
    """Service for SAML 2.0 authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_config(self, config_id: str) -> Optional[SAMLConfig]:
        """Get SAML config by ID"""
        return self.db.query(SAMLConfig).filter(
            SAMLConfig.id == config_id,
            SAMLConfig.is_enabled == True
        ).first()
    
    def get_config_by_tenant(self, tenant_id: str) -> Optional[SAMLConfig]:
        """Get SAML config for tenant"""
        return self.db.query(SAMLConfig).filter(
            SAMLConfig.tenant_id == tenant_id,
            SAMLConfig.is_enabled == True
        ).first()
    
    def create_config(self, tenant_id: str, config_data: Dict[str, Any]) -> SAMLConfig:
        """Create SAML configuration"""
        config = SAMLConfig(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            **config_data
        )
        
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        
        return config
    
    def get_sp_metadata(self, config: SAMLConfig) -> str:
        """Generate Service Provider metadata XML"""
        # This would generate SAML SP metadata XML
        # For demo purposes, returning a simplified version
        metadata = f"""
        <?xml version="1.0"?>
        <md:EntityDescriptor xmlns:md="urn:oasis:names:tc:SAML:2.0:metadata"
                             entityID="{config.sp_entity_id}">
            <md:SPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
                <md:AssertionConsumerService
                    Binding="urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
                    Location="{config.sp_acs_url}"
                    index="0" />
            </md:SPSSODescriptor>
        </md:EntityDescriptor>
        """
        return metadata
    
    def generate_authn_request(self, config: SAMLConfig) -> str:
        """Generate SAML authentication request"""
        # This would generate a proper SAML AuthnRequest
        # For demo purposes, returning mock
        return "MOCK_SAML_AUTHN_REQUEST"
    
    def parse_saml_response(self, saml_response: str, config: SAMLConfig) -> Dict[str, Any]:
        """Parse and validate SAML response"""
        # This would parse and validate the SAML assertion
        # For demo purposes, returning mock data
        return {
            "email": "demo.user@company.com",
            "firstName": "Demo",
            "lastName": "User",
            "attributes": {}
        }
    
    def map_user_data(
        self, config: SAMLConfig, saml_attributes: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map SAML attributes to our user model"""
        mapping = config.attribute_mapping or {}
        
        return {
            "email": saml_attributes.get(mapping.get("email", "email")),
            "full_name": f"{saml_attributes.get(mapping.get('firstName', 'firstName'), '')} {saml_attributes.get(mapping.get('lastName', 'lastName'), '')}".strip()
        }
    
    def find_or_create_user(
        self, config: SAMLConfig, user_data: Dict[str, Any]
    ) -> Optional[User]:
        """Find existing user or create new one from SAML data"""
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
        
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            full_name=user_data.get("full_name", email),
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
            role=UserRole.VIEWER,
            is_active=True,
            tenant_id=config.tenant_id
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
