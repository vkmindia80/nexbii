"""
Configuration Management Service for Phase 4.5 - Enterprise Admin
Handles configuration versioning, export/import, and rollback
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from app.models.admin import ConfigurationVersion
from app.models.tenant import Tenant
from app.models.integration import Integration
from app.schemas.admin import (
    ConfigurationVersionCreate,
    ConfigurationExportRequest,
    ConfigurationImportRequest
)

logger = logging.getLogger(__name__)


class ConfigurationService:
    """
    Service for managing configuration versions and rollback
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def export_configuration(
        self,
        request: ConfigurationExportRequest
    ) -> Dict[str, Any]:
        """
        Export tenant configuration
        """
        config = {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "sections": {}
        }
        
        tenant_id = request.tenant_id
        sections = request.sections or ["all"]
        
        # Export tenant information
        if "all" in sections or "tenant" in sections:
            config["sections"]["tenant"] = self._export_tenant_config(tenant_id)
        
        # Export branding
        if "all" in sections or "branding" in sections:
            config["sections"]["branding"] = self._export_branding_config(tenant_id)
        
        # Export integrations
        if "all" in sections or "integrations" in sections:
            config["sections"]["integrations"] = self._export_integrations_config(
                tenant_id, 
                request.include_secrets
            )
        
        # Export security settings
        if "all" in sections or "security" in sections:
            config["sections"]["security"] = self._export_security_config(tenant_id)
        
        # Export features
        if "all" in sections or "features" in sections:
            config["sections"]["features"] = self._export_features_config(tenant_id)
        
        return config
    
    def _export_tenant_config(self, tenant_id: Optional[str]) -> Dict[str, Any]:
        """Export basic tenant configuration"""
        if not tenant_id:
            return {}
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return {}
        
        return {
            "name": tenant.name,
            "slug": tenant.slug,
            "plan": tenant.plan,
            "is_active": tenant.is_active,
            "settings": tenant.settings or {}
        }
    
    def _export_branding_config(self, tenant_id: Optional[str]) -> Dict[str, Any]:
        """Export branding configuration"""
        if not tenant_id:
            return {}
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant or not tenant.branding:
            return {}
        
        return tenant.branding
    
    def _export_integrations_config(
        self, 
        tenant_id: Optional[str],
        include_secrets: bool = False
    ) -> List[Dict[str, Any]]:
        """Export integrations configuration"""
        query = self.db.query(Integration)
        
        if tenant_id:
            query = query.filter(Integration.tenant_id == tenant_id)
        
        integrations = query.all()
        
        result = []
        for integration in integrations:
            config = {
                "type": integration.type,
                "name": integration.name,
                "is_active": integration.is_active,
                "settings": integration.settings or {}
            }
            
            # Only include credentials if explicitly requested
            if include_secrets and integration.encrypted_credentials:
                config["credentials"] = integration.encrypted_credentials
            
            result.append(config)
        
        return result
    
    def _export_security_config(self, tenant_id: Optional[str]) -> Dict[str, Any]:
        """Export security settings"""
        # Export security policies, SSO settings, etc.
        from app.models.security import SecurityPolicy, SSOConfig, MFAConfig
        
        config = {
            "policies": [],
            "sso": [],
            "mfa": {}
        }
        
        # Export security policies
        query = self.db.query(SecurityPolicy)
        if tenant_id:
            query = query.filter(SecurityPolicy.tenant_id == tenant_id)
        
        policies = query.all()
        config["policies"] = [
            {
                "name": p.policy_name,
                "type": p.policy_type,
                "rule": p.rule,
                "is_active": p.is_active
            }
            for p in policies
        ]
        
        # Export SSO configuration
        sso_query = self.db.query(SSOConfig)
        if tenant_id:
            sso_query = sso_query.filter(SSOConfig.tenant_id == tenant_id)
        
        sso_configs = sso_query.all()
        config["sso"] = [
            {
                "provider": s.provider,
                "is_enabled": s.is_enabled,
                "settings": s.settings or {}
                # Don't export secrets
            }
            for s in sso_configs
        ]
        
        return config
    
    def _export_features_config(self, tenant_id: Optional[str]) -> Dict[str, Any]:
        """Export feature flags and settings"""
        if not tenant_id:
            return {}
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return {}
        
        return tenant.features or {}
    
    def import_configuration(
        self,
        request: ConfigurationImportRequest,
        imported_by: str
    ) -> Dict[str, Any]:
        """
        Import configuration from exported data
        """
        result = {
            "imported_at": datetime.utcnow().isoformat(),
            "sections_imported": [],
            "errors": []
        }
        
        tenant_id = request.tenant_id
        config = request.configuration
        
        try:
            # Import each section
            if "tenant" in config.get("sections", {}):
                self._import_tenant_config(tenant_id, config["sections"]["tenant"], request.merge)
                result["sections_imported"].append("tenant")
            
            if "branding" in config.get("sections", {}):
                self._import_branding_config(tenant_id, config["sections"]["branding"])
                result["sections_imported"].append("branding")
            
            if "integrations" in config.get("sections", {}):
                self._import_integrations_config(
                    tenant_id, 
                    config["sections"]["integrations"],
                    request.merge
                )
                result["sections_imported"].append("integrations")
            
            if "security" in config.get("sections", {}):
                self._import_security_config(tenant_id, config["sections"]["security"])
                result["sections_imported"].append("security")
            
            if "features" in config.get("sections", {}):
                self._import_features_config(tenant_id, config["sections"]["features"])
                result["sections_imported"].append("features")
            
            # Create configuration version if requested
            if request.create_version:
                version = self.create_version(
                    tenant_id=tenant_id,
                    configuration=config,
                    description="Imported configuration",
                    changed_by=imported_by
                )
                result["version_id"] = version.id
            
            self.db.commit()
            result["status"] = "success"
            
        except Exception as e:
            self.db.rollback()
            result["status"] = "failed"
            result["errors"].append(str(e))
            logger.error(f"Configuration import failed: {e}")
        
        return result
    
    def _import_tenant_config(
        self, 
        tenant_id: Optional[str], 
        config: Dict[str, Any],
        merge: bool = False
    ) -> None:
        """Import tenant configuration"""
        if not tenant_id:
            return
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return
        
        # Update tenant settings
        if "name" in config:
            tenant.name = config["name"]
        if "plan" in config:
            tenant.plan = config["plan"]
        if "settings" in config:
            if merge and tenant.settings:
                tenant.settings.update(config["settings"])
            else:
                tenant.settings = config["settings"]
    
    def _import_branding_config(
        self, 
        tenant_id: Optional[str], 
        config: Dict[str, Any]
    ) -> None:
        """Import branding configuration"""
        if not tenant_id:
            return
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return
        
        tenant.branding = config
    
    def _import_integrations_config(
        self,
        tenant_id: Optional[str],
        integrations: List[Dict[str, Any]],
        merge: bool = False
    ) -> None:
        """Import integrations configuration"""
        for int_config in integrations:
            # Find existing integration
            existing = self.db.query(Integration).filter(
                Integration.tenant_id == tenant_id,
                Integration.type == int_config["type"]
            ).first()
            
            if existing:
                if merge:
                    # Update existing
                    existing.name = int_config.get("name", existing.name)
                    existing.is_active = int_config.get("is_active", existing.is_active)
                    if "settings" in int_config:
                        existing.settings = int_config["settings"]
            else:
                # Create new integration
                new_integration = Integration(
                    tenant_id=tenant_id,
                    type=int_config["type"],
                    name=int_config["name"],
                    is_active=int_config.get("is_active", True),
                    settings=int_config.get("settings", {})
                )
                self.db.add(new_integration)
    
    def _import_security_config(
        self,
        tenant_id: Optional[str],
        config: Dict[str, Any]
    ) -> None:
        """Import security configuration"""
        # Import security policies
        # This would involve creating SecurityPolicy records
        pass
    
    def _import_features_config(
        self,
        tenant_id: Optional[str],
        features: Dict[str, Any]
    ) -> None:
        """Import feature flags"""
        if not tenant_id:
            return
        
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not tenant:
            return
        
        tenant.features = features
    
    def create_version(
        self,
        tenant_id: str,
        configuration: Dict[str, Any],
        description: Optional[str] = None,
        changed_by: Optional[str] = None
    ) -> ConfigurationVersion:
        """
        Create a new configuration version
        """
        # Get current version number
        latest_version = self.db.query(ConfigurationVersion).filter(
            ConfigurationVersion.tenant_id == tenant_id
        ).order_by(desc(ConfigurationVersion.version)).first()
        
        new_version_number = (latest_version.version + 1) if latest_version else 1
        
        # Calculate changes from previous version
        changes = None
        if latest_version:
            changes = self._calculate_changes(
                latest_version.configuration,
                configuration
            )
        
        # Deactivate previous active version
        if latest_version and latest_version.is_active:
            latest_version.is_active = False
        
        # Create new version
        version = ConfigurationVersion(
            tenant_id=tenant_id,
            version=new_version_number,
            description=description,
            configuration=configuration,
            changes=changes,
            changed_by=changed_by,
            is_active=True
        )
        
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        return version
    
    def get_versions(
        self,
        tenant_id: str,
        limit: int = 20
    ) -> List[ConfigurationVersion]:
        """
        Get configuration version history
        """
        return self.db.query(ConfigurationVersion).filter(
            ConfigurationVersion.tenant_id == tenant_id
        ).order_by(desc(ConfigurationVersion.version)).limit(limit).all()
    
    def get_version(
        self,
        version_id: str
    ) -> Optional[ConfigurationVersion]:
        """
        Get a specific configuration version
        """
        return self.db.query(ConfigurationVersion).filter(
            ConfigurationVersion.id == version_id
        ).first()
    
    def rollback_to_version(
        self,
        tenant_id: str,
        version_id: str,
        performed_by: str
    ) -> ConfigurationVersion:
        """
        Rollback configuration to a previous version
        """
        target_version = self.get_version(version_id)
        
        if not target_version:
            raise ValueError("Version not found")
        
        if target_version.tenant_id != tenant_id:
            raise ValueError("Version does not belong to tenant")
        
        # Import the configuration from that version
        import_request = ConfigurationImportRequest(
            tenant_id=tenant_id,
            configuration=target_version.configuration,
            merge=False,
            create_version=True
        )
        
        result = self.import_configuration(import_request, performed_by)
        
        if result["status"] != "success":
            raise Exception(f"Rollback failed: {result.get('errors')}")
        
        # Get the newly created version
        new_version = self.db.query(ConfigurationVersion).filter(
            ConfigurationVersion.id == result.get("version_id")
        ).first()
        
        if new_version:
            new_version.description = f"Rolled back to version {target_version.version}"
            self.db.commit()
        
        return new_version
    
    def _calculate_changes(
        self,
        old_config: Dict[str, Any],
        new_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate differences between two configurations
        """
        changes = {
            "added": [],
            "removed": [],
            "modified": []
        }
        
        # Flatten configurations for comparison
        old_flat = self._flatten_dict(old_config)
        new_flat = self._flatten_dict(new_config)
        
        # Find added keys
        for key in new_flat:
            if key not in old_flat:
                changes["added"].append(key)
        
        # Find removed keys
        for key in old_flat:
            if key not in new_flat:
                changes["removed"].append(key)
        
        # Find modified keys
        for key in old_flat:
            if key in new_flat and old_flat[key] != new_flat[key]:
                changes["modified"].append({
                    "key": key,
                    "old_value": old_flat[key],
                    "new_value": new_flat[key]
                })
        
        return changes
    
    def _flatten_dict(
        self, 
        d: Dict[str, Any], 
        parent_key: str = '', 
        sep: str = '.'
    ) -> Dict[str, Any]:
        """
        Flatten nested dictionary
        """
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)


def get_configuration_service(db: Session) -> ConfigurationService:
    """Get configuration service instance"""
    return ConfigurationService(db)
