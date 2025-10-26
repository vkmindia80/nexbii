from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Plugin types
PLUGIN_TYPES = [
    "visualization",  # Custom chart types
    "datasource",     # Custom database connectors
    "transformation", # Data transformation functions
    "export"         # Custom export formats
]

class PluginManifest(BaseModel):
    """Plugin manifest schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Unique plugin identifier")
    display_name: str = Field(..., min_length=1, max_length=200, description="Human-readable name")
    description: str = Field(..., max_length=1000)
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$", description="Semantic version (e.g., 1.0.0)")
    author: Optional[str] = Field(None, max_length=200)
    plugin_type: str = Field(..., description="Type of plugin")
    entry_point: str = Field(..., description="Main file to execute (e.g., main.py)")
    dependencies: List[str] = Field(default_factory=list, description="Python package dependencies")
    required_scopes: List[str] = Field(default_factory=list, description="Required API scopes")
    config_schema: Optional[Dict[str, Any]] = Field(None, description="JSON Schema for configuration")
    default_config: Optional[Dict[str, Any]] = Field(None, description="Default configuration values")
    
    @validator('plugin_type')
    def validate_plugin_type(cls, v):
        if v not in PLUGIN_TYPES:
            raise ValueError(f"Plugin type must be one of: {', '.join(PLUGIN_TYPES)}")
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Plugin name must be alphanumeric with hyphens/underscores"""
        import re
        if not re.match(r'^[a-z0-9-_]+$', v):
            raise ValueError("Plugin name must contain only lowercase letters, numbers, hyphens, and underscores")
        return v


class PluginCreate(BaseModel):
    """Schema for uploading a new plugin"""
    manifest: PluginManifest
    files: Dict[str, str] = Field(..., description="Plugin files {filename: content}")
    
    @validator('files')
    def validate_files(cls, v, values):
        """Validate that entry point exists in files"""
        if 'manifest' in values:
            entry_point = values['manifest'].entry_point
            if entry_point not in v:
                raise ValueError(f"Entry point file '{entry_point}' not found in uploaded files")
        return v


class PluginUpdate(BaseModel):
    """Schema for updating a plugin"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    is_enabled: Optional[bool] = None
    config_schema: Optional[Dict[str, Any]] = None
    default_config: Optional[Dict[str, Any]] = None


class PluginResponse(BaseModel):
    """Schema for plugin response"""
    id: str
    name: str
    display_name: str
    description: Optional[str]
    version: str
    author: Optional[str]
    plugin_type: str
    is_enabled: bool
    is_verified: bool
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PluginDetailResponse(PluginResponse):
    """Detailed plugin response with manifest"""
    entry_point: str
    dependencies: List[str]
    required_scopes: List[str]
    config_schema: Optional[Dict[str, Any]]
    default_config: Optional[Dict[str, Any]]
    installed_by: str
    tenant_id: Optional[str]


class PluginInstanceCreate(BaseModel):
    """Schema for creating a plugin instance"""
    plugin_id: str
    name: str = Field(..., min_length=1, max_length=200)
    config: Dict[str, Any] = Field(default_factory=dict)


class PluginInstanceUpdate(BaseModel):
    """Schema for updating a plugin instance"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    config: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None


class PluginInstanceResponse(BaseModel):
    """Schema for plugin instance response"""
    id: str
    plugin_id: str
    name: str
    config: Dict[str, Any]
    is_enabled: bool
    execution_count: int
    last_executed_at: Optional[datetime]
    error_count: int
    last_error: Optional[str]
    last_error_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class PluginExecutionRequest(BaseModel):
    """Schema for executing a plugin"""
    instance_id: str
    input_data: Dict[str, Any] = Field(default_factory=dict)
    params: Dict[str, Any] = Field(default_factory=dict)


class PluginExecutionResponse(BaseModel):
    """Response from plugin execution"""
    success: bool
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    execution_time_ms: int


class PluginTypeInfo(BaseModel):
    """Information about plugin types"""
    type: str
    description: str
    example_use_cases: List[str]


class PluginTypesResponse(BaseModel):
    """Response with all available plugin types"""
    types: List[PluginTypeInfo]


class PluginStatsResponse(BaseModel):
    """Plugin usage statistics"""
    plugin_id: str
    plugin_name: str
    total_instances: int
    total_executions: int
    total_errors: int
    avg_execution_time_ms: Optional[float]
    success_rate: float
    last_30d_executions: int
