import json
import time
import tempfile
import subprocess
import os
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from ..models.plugin import Plugin, PluginInstance
from ..schemas.plugin import (
    PluginCreate, PluginUpdate, PluginInstanceCreate, PluginInstanceUpdate,
    PluginStatsResponse, PluginExecutionResponse
)
from fastapi import HTTPException, status

class PluginService:
    """Service for managing plugins"""
    
    @staticmethod
    def create_plugin(
        db: Session,
        user_id: str,
        tenant_id: Optional[str],
        plugin_data: PluginCreate
    ) -> Plugin:
        """Install a new plugin"""
        manifest = plugin_data.manifest
        
        # Check if plugin with same name already exists
        existing = db.query(Plugin).filter(Plugin.name == manifest.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Plugin '{manifest.name}' already exists"
            )
        
        plugin = Plugin(
            name=manifest.name,
            display_name=manifest.display_name,
            description=manifest.description,
            version=manifest.version,
            author=manifest.author,
            plugin_type=manifest.plugin_type,
            entry_point=manifest.entry_point,
            files=plugin_data.files,
            manifest=manifest.dict(),
            dependencies=manifest.dependencies,
            required_scopes=manifest.required_scopes,
            config_schema=manifest.config_schema,
            default_config=manifest.default_config,
            installed_by=user_id,
            tenant_id=tenant_id,
            is_enabled=False,  # Disabled by default for security
            is_verified=False
        )
        
        db.add(plugin)
        db.commit()
        db.refresh(plugin)
        
        return plugin
    
    @staticmethod
    def get_plugins(
        db: Session,
        tenant_id: Optional[str],
        plugin_type: Optional[str] = None,
        enabled_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[Plugin]:
        """Get all plugins"""
        query = db.query(Plugin)
        
        # Show global plugins + tenant-specific plugins
        if tenant_id:
            query = query.filter(
                (Plugin.tenant_id == tenant_id) | (Plugin.tenant_id.is_(None))
            )
        else:
            query = query.filter(Plugin.tenant_id.is_(None))
        
        if plugin_type:
            query = query.filter(Plugin.plugin_type == plugin_type)
        
        if enabled_only:
            query = query.filter(Plugin.is_enabled == True)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_plugin_by_id(
        db: Session,
        plugin_id: str
    ) -> Optional[Plugin]:
        """Get a specific plugin by ID"""
        return db.query(Plugin).filter(Plugin.id == plugin_id).first()
    
    @staticmethod
    def update_plugin(
        db: Session,
        plugin_id: str,
        update_data: PluginUpdate
    ) -> Plugin:
        """Update a plugin"""
        plugin = PluginService.get_plugin_by_id(db, plugin_id)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(plugin, field, value)
        
        db.commit()
        db.refresh(plugin)
        return plugin
    
    @staticmethod
    def delete_plugin(
        db: Session,
        plugin_id: str
    ) -> bool:
        """Uninstall a plugin"""
        plugin = PluginService.get_plugin_by_id(db, plugin_id)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        # Delete all instances first
        db.query(PluginInstance).filter(PluginInstance.plugin_id == plugin_id).delete()
        
        # Delete plugin
        db.delete(plugin)
        db.commit()
        return True
    
    # Plugin Instance Management
    
    @staticmethod
    def create_instance(
        db: Session,
        tenant_id: str,
        instance_data: PluginInstanceCreate
    ) -> PluginInstance:
        """Create a plugin instance"""
        # Verify plugin exists and is enabled
        plugin = PluginService.get_plugin_by_id(db, instance_data.plugin_id)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        if not plugin.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plugin is not enabled"
            )
        
        # Validate config against schema if provided
        if plugin.config_schema and instance_data.config:
            # TODO: Implement JSON Schema validation
            pass
        
        instance = PluginInstance(
            plugin_id=instance_data.plugin_id,
            tenant_id=tenant_id,
            name=instance_data.name,
            config=instance_data.config or plugin.default_config or {},
            is_enabled=True
        )
        
        db.add(instance)
        db.commit()
        db.refresh(instance)
        
        return instance
    
    @staticmethod
    def get_instances(
        db: Session,
        tenant_id: str,
        plugin_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[PluginInstance]:
        """Get plugin instances for a tenant"""
        query = db.query(PluginInstance).filter(PluginInstance.tenant_id == tenant_id)
        
        if plugin_id:
            query = query.filter(PluginInstance.plugin_id == plugin_id)
        
        return query.offset(skip).limit(limit).all()
    
    @staticmethod
    def get_instance_by_id(
        db: Session,
        instance_id: str,
        tenant_id: str
    ) -> Optional[PluginInstance]:
        """Get a specific plugin instance"""
        return db.query(PluginInstance).filter(
            PluginInstance.id == instance_id,
            PluginInstance.tenant_id == tenant_id
        ).first()
    
    @staticmethod
    def update_instance(
        db: Session,
        instance_id: str,
        tenant_id: str,
        update_data: PluginInstanceUpdate
    ) -> PluginInstance:
        """Update a plugin instance"""
        instance = PluginService.get_instance_by_id(db, instance_id, tenant_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin instance not found"
            )
        
        # Update fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(instance, field, value)
        
        db.commit()
        db.refresh(instance)
        return instance
    
    @staticmethod
    def delete_instance(
        db: Session,
        instance_id: str,
        tenant_id: str
    ) -> bool:
        """Delete a plugin instance"""
        instance = PluginService.get_instance_by_id(db, instance_id, tenant_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin instance not found"
            )
        
        db.delete(instance)
        db.commit()
        return True
    
    # Plugin Execution
    
    @staticmethod
    def execute_plugin(
        db: Session,
        instance_id: str,
        tenant_id: str,
        input_data: Dict[str, Any],
        params: Dict[str, Any]
    ) -> PluginExecutionResponse:
        """
        Execute a plugin in a sandboxed environment
        
        This is a simplified implementation. In production, you would:
        1. Use Docker containers for isolation
        2. Implement resource limits (CPU, memory, time)
        3. Add more security checks
        4. Implement proper logging and monitoring
        """
        # Get instance and plugin
        instance = PluginService.get_instance_by_id(db, instance_id, tenant_id)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin instance not found"
            )
        
        if not instance.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plugin instance is disabled"
            )
        
        plugin = PluginService.get_plugin_by_id(db, instance.plugin_id)
        if not plugin or not plugin.is_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Plugin is not available"
            )
        
        start_time = time.time()
        
        try:
            # Create temporary directory for plugin execution
            with tempfile.TemporaryDirectory() as tmpdir:
                # Write plugin files to temp directory
                for filename, content in plugin.files.items():
                    filepath = os.path.join(tmpdir, filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, 'w') as f:
                        f.write(content)
                
                # Prepare execution context
                execution_context = {
                    "input": input_data,
                    "params": params,
                    "config": instance.config
                }
                
                context_file = os.path.join(tmpdir, "_context.json")
                with open(context_file, 'w') as f:
                    json.dump(execution_context, f)
                
                # Execute plugin (timeout: 30 seconds)
                entry_point = os.path.join(tmpdir, plugin.entry_point)
                result = subprocess.run(
                    ["python", entry_point, context_file],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=tmpdir
                )
                
                execution_time_ms = int((time.time() - start_time) * 1000)
                
                # Update instance statistics
                instance.execution_count += 1
                instance.last_executed_at = datetime.utcnow()
                instance.total_execution_time_ms += execution_time_ms
                
                # Update plugin statistics
                plugin.usage_count += 1
                plugin.last_used_at = datetime.utcnow()
                
                if result.returncode == 0:
                    # Success
                    try:
                        output = json.loads(result.stdout)
                    except json.JSONDecodeError:
                        output = {"result": result.stdout}
                    
                    db.commit()
                    
                    return PluginExecutionResponse(
                        success=True,
                        output=output,
                        error=None,
                        execution_time_ms=execution_time_ms
                    )
                else:
                    # Execution error
                    instance.error_count += 1
                    instance.last_error = result.stderr[:1000]
                    instance.last_error_at = datetime.utcnow()
                    
                    db.commit()
                    
                    return PluginExecutionResponse(
                        success=False,
                        output=None,
                        error=result.stderr,
                        execution_time_ms=execution_time_ms
                    )
                    
        except subprocess.TimeoutExpired:
            execution_time_ms = int((time.time() - start_time) * 1000)
            instance.error_count += 1
            instance.last_error = "Plugin execution timed out (30s limit)"
            instance.last_error_at = datetime.utcnow()
            
            db.commit()
            
            return PluginExecutionResponse(
                success=False,
                output=None,
                error="Plugin execution timed out (30 second limit)",
                execution_time_ms=execution_time_ms
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            instance.error_count += 1
            instance.last_error = str(e)[:1000]
            instance.last_error_at = datetime.utcnow()
            
            db.commit()
            
            return PluginExecutionResponse(
                success=False,
                output=None,
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    @staticmethod
    def get_plugin_stats(
        db: Session,
        plugin_id: str
    ) -> PluginStatsResponse:
        """Get statistics for a plugin"""
        plugin = PluginService.get_plugin_by_id(db, plugin_id)
        if not plugin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plugin not found"
            )
        
        # Get all instances
        instances = db.query(PluginInstance).filter(
            PluginInstance.plugin_id == plugin_id
        ).all()
        
        total_instances = len(instances)
        total_executions = sum(i.execution_count for i in instances)
        total_errors = sum(i.error_count for i in instances)
        total_time_ms = sum(i.total_execution_time_ms for i in instances)
        
        # Calculate average execution time
        avg_execution_time_ms = None
        if total_executions > 0:
            avg_execution_time_ms = total_time_ms / total_executions
        
        # Success rate
        success_rate = 0.0
        if total_executions > 0:
            success_rate = ((total_executions - total_errors) / total_executions) * 100
        
        # Last 30 days executions
        now = datetime.utcnow()
        executions_30d = sum(
            i.execution_count for i in instances
            if i.last_executed_at and i.last_executed_at >= now - timedelta(days=30)
        )
        
        return PluginStatsResponse(
            plugin_id=plugin.id,
            plugin_name=plugin.display_name,
            total_instances=total_instances,
            total_executions=total_executions,
            total_errors=total_errors,
            avg_execution_time_ms=avg_execution_time_ms,
            success_rate=round(success_rate, 2),
            last_30d_executions=executions_30d
        )
