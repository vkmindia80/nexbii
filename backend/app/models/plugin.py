from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, Text, Index
from sqlalchemy.sql import func
import uuid
from ..core.database import Base

class Plugin(Base):
    """Plugin model for custom extensions"""
    __tablename__ = "plugins"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Plugin metadata
    name = Column(String, nullable=False, unique=True, index=True)
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(String, nullable=False)
    author = Column(String, nullable=True)
    
    # Plugin type and configuration
    plugin_type = Column(String, nullable=False, index=True)
    # Types: visualization, datasource, transformation, export
    
    # Plugin files and code
    entry_point = Column(String, nullable=False)  # Main file/module to execute
    files = Column(JSON, nullable=False, default=dict)  # {filename: content}
    manifest = Column(JSON, nullable=False)  # Full plugin manifest
    
    # Dependencies and requirements
    dependencies = Column(JSON, nullable=False, default=list)  # Python packages
    required_scopes = Column(JSON, nullable=False, default=list)  # Required permissions
    
    # Configuration schema (JSON Schema format)
    config_schema = Column(JSON, nullable=True)
    default_config = Column(JSON, nullable=True)
    
    # Installation details
    installed_by = Column(String, nullable=False)  # User ID
    tenant_id = Column(String, index=True, nullable=True)  # Null = global plugin
    
    # Status
    is_enabled = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)  # Verified by platform admin
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_plugin_tenant_type', 'tenant_id', 'plugin_type'),
        Index('idx_plugin_enabled', 'is_enabled', 'plugin_type'),
    )


class PluginInstance(Base):
    """Plugin instance with tenant-specific configuration"""
    __tablename__ = "plugin_instances"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    plugin_id = Column(String, index=True, nullable=False)
    tenant_id = Column(String, index=True, nullable=False)
    
    # Instance configuration
    name = Column(String, nullable=False)  # User-friendly name for this instance
    config = Column(JSON, nullable=False, default=dict)  # Instance-specific config
    
    # Status
    is_enabled = Column(Boolean, default=True)
    
    # Usage tracking
    execution_count = Column(Integer, default=0)
    last_executed_at = Column(DateTime(timezone=True), nullable=True)
    total_execution_time_ms = Column(Integer, default=0)
    
    # Error tracking
    error_count = Column(Integer, default=0)
    last_error = Column(Text, nullable=True)
    last_error_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_plugin_instance_tenant_plugin', 'tenant_id', 'plugin_id'),
    )
