from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from ...core.database import get_db
from ...core.security import get_current_user
from ...models.user import User, UserRole
from ...schemas.plugin import (
    PluginCreate,
    PluginUpdate,
    PluginResponse,
    PluginDetailResponse,
    PluginInstanceCreate,
    PluginInstanceUpdate,
    PluginInstanceResponse,
    PluginExecutionRequest,
    PluginExecutionResponse,
    PluginTypesResponse,
    PluginTypeInfo,
    PluginStatsResponse,
    PLUGIN_TYPES
)
from ...services.plugin_service import PluginService

router = APIRouter()

# Plugin type descriptions
PLUGIN_TYPE_DESCRIPTIONS = {
    "visualization": {
        "description": "Custom chart and visualization components",
        "examples": ["3D scatter plots", "Custom gauges", "Geographic maps", "Network diagrams"]
    },
    "datasource": {
        "description": "Custom database and API connectors",
        "examples": ["Proprietary databases", "REST APIs", "GraphQL endpoints", "Streaming data sources"]
    },
    "transformation": {
        "description": "Data transformation and processing functions",
        "examples": ["Custom aggregations", "Data cleaning", "Format conversions", "Enrichment pipelines"]
    },
    "export": {
        "description": "Custom export formats and destinations",
        "examples": ["Custom PDF templates", "Cloud storage uploads", "Email delivery", "Webhook notifications"]
    }
}


@router.get("/types", response_model=PluginTypesResponse)
async def get_plugin_types():
    """
    Get list of all available plugin types
    """
    types = [
        PluginTypeInfo(
            type=plugin_type,
            description=PLUGIN_TYPE_DESCRIPTIONS[plugin_type]["description"],
            example_use_cases=PLUGIN_TYPE_DESCRIPTIONS[plugin_type]["examples"]
        )
        for plugin_type in PLUGIN_TYPES
    ]
    
    return PluginTypesResponse(types=types)


@router.post("/", response_model=PluginDetailResponse, status_code=status.HTTP_201_CREATED)
async def install_plugin(
    plugin_data: PluginCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Install a new plugin
    
    Uploads and installs a custom plugin. The plugin will be disabled by default
    and must be enabled before use.
    
    **Required fields:**
    - manifest: Plugin metadata and configuration
    - files: Dictionary of plugin files {filename: content}
    
    **Security Note:** Plugins are executed in a sandboxed environment but should
    still be reviewed before enabling.
    """
    # Only admins can install plugins
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can install plugins"
        )
    
    plugin = PluginService.create_plugin(
        db=db,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        plugin_data=plugin_data
    )
    
    return plugin


@router.get("/", response_model=List[PluginResponse])
async def list_plugins(
    plugin_type: Optional[str] = None,
    enabled_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all available plugins
    
    Returns plugins available to the current tenant, including global plugins.
    """
    plugins = PluginService.get_plugins(
        db=db,
        tenant_id=current_user.tenant_id,
        plugin_type=plugin_type,
        enabled_only=enabled_only,
        skip=skip,
        limit=limit
    )
    
    return plugins


@router.get("/{plugin_id}", response_model=PluginDetailResponse)
async def get_plugin(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific plugin
    """
    plugin = PluginService.get_plugin_by_id(db, plugin_id)
    
    if not plugin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin not found"
        )
    
    return plugin


@router.put("/{plugin_id}", response_model=PluginResponse)
async def update_plugin(
    plugin_id: str,
    update_data: PluginUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a plugin
    
    Can update display name, description, and enabled status.
    Only administrators can modify plugins.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update plugins"
        )
    
    plugin = PluginService.update_plugin(
        db=db,
        plugin_id=plugin_id,
        update_data=update_data
    )
    
    return plugin


@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def uninstall_plugin(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Uninstall a plugin
    
    This will permanently delete the plugin and all its instances.
    Only administrators can uninstall plugins.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can uninstall plugins"
        )
    
    PluginService.delete_plugin(db=db, plugin_id=plugin_id)
    
    return None


@router.get("/{plugin_id}/stats", response_model=PluginStatsResponse)
async def get_plugin_stats(
    plugin_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get usage statistics for a plugin
    
    Returns execution counts, error rates, and performance metrics.
    """
    stats = PluginService.get_plugin_stats(db=db, plugin_id=plugin_id)
    
    return stats


# Plugin Instance Endpoints

@router.post("/instances", response_model=PluginInstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_plugin_instance(
    instance_data: PluginInstanceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new plugin instance
    
    Creates a configured instance of a plugin that can be used in your workflows.
    """
    instance = PluginService.create_instance(
        db=db,
        tenant_id=current_user.tenant_id,
        instance_data=instance_data
    )
    
    return instance


@router.get("/instances", response_model=List[PluginInstanceResponse])
async def list_plugin_instances(
    plugin_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all plugin instances for the current tenant
    """
    instances = PluginService.get_instances(
        db=db,
        tenant_id=current_user.tenant_id,
        plugin_id=plugin_id,
        skip=skip,
        limit=limit
    )
    
    return instances


@router.get("/instances/{instance_id}", response_model=PluginInstanceResponse)
async def get_plugin_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific plugin instance
    """
    instance = PluginService.get_instance_by_id(
        db=db,
        instance_id=instance_id,
        tenant_id=current_user.tenant_id
    )
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plugin instance not found"
        )
    
    return instance


@router.put("/instances/{instance_id}", response_model=PluginInstanceResponse)
async def update_plugin_instance(
    instance_id: str,
    update_data: PluginInstanceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a plugin instance
    
    Can update name, configuration, and enabled status.
    """
    instance = PluginService.update_instance(
        db=db,
        instance_id=instance_id,
        tenant_id=current_user.tenant_id,
        update_data=update_data
    )
    
    return instance


@router.delete("/instances/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plugin_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a plugin instance
    """
    PluginService.delete_instance(
        db=db,
        instance_id=instance_id,
        tenant_id=current_user.tenant_id
    )
    
    return None


@router.post("/execute", response_model=PluginExecutionResponse)
async def execute_plugin(
    execution_request: PluginExecutionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute a plugin instance
    
    Runs the plugin with the provided input data and parameters.
    Execution is sandboxed and has a 30-second timeout.
    """
    result = PluginService.execute_plugin(
        db=db,
        instance_id=execution_request.instance_id,
        tenant_id=current_user.tenant_id,
        input_data=execution_request.input_data,
        params=execution_request.params
    )
    
    return result
