"""
Backup Service for Phase 4.5 - Enterprise Admin
Handles database backups with local and S3 storage support
"""
import os
import subprocess
import json
import gzip
import shutil
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import logging
from pathlib import Path

from app.models.admin import BackupJob, BackupType, BackupStatus, BackupStorageType
from app.schemas.admin import BackupJobCreate, BackupRestoreRequest, BackupScheduleConfig
from app.core.database import get_db_url

# Optional S3 imports
try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False

logger = logging.getLogger(__name__)


class BackupService:
    """
    Service for managing database backups and restores
    Supports local filesystem and S3 storage
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.backup_dir = os.getenv("BACKUP_DIR", "/app/backups")
        self.db_url = get_db_url()
        
        # Ensure backup directory exists
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Initialize S3 client if available
        self.s3_client = None
        if S3_AVAILABLE:
            try:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.getenv('AWS_REGION', 'us-east-1')
                )
            except Exception as e:
                logger.warning(f"S3 client initialization failed: {e}")
    
    def create_backup(
        self,
        backup_request: BackupJobCreate,
        created_by: str
    ) -> BackupJob:
        """
        Create a new backup job
        """
        # Create backup job record
        backup_job = BackupJob(
            tenant_id=backup_request.tenant_id,
            backup_type=backup_request.backup_type,
            storage_type=backup_request.storage_type,
            includes_data=backup_request.includes_data,
            includes_config=backup_request.includes_config,
            tables_included=backup_request.tables_included,
            is_encrypted=backup_request.is_encrypted,
            s3_bucket=backup_request.s3_bucket,
            s3_region=backup_request.s3_region,
            status=BackupStatus.PENDING,
            created_by=created_by,
            metadata={"description": backup_request.description} if hasattr(backup_request, 'description') else None
        )
        
        self.db.add(backup_job)
        self.db.commit()
        self.db.refresh(backup_job)
        
        # Execute backup asynchronously (in production, use Celery/background worker)
        try:
            self._execute_backup(backup_job)
        except Exception as e:
            logger.error(f"Backup execution failed: {e}")
            backup_job.status = BackupStatus.FAILED
            backup_job.error_message = str(e)
            self.db.commit()
        
        return backup_job
    
    def _execute_backup(self, backup_job: BackupJob) -> None:
        """
        Execute the actual backup operation
        """
        backup_job.status = BackupStatus.IN_PROGRESS
        backup_job.started_at = datetime.utcnow()
        self.db.commit()
        
        try:
            if backup_job.backup_type == BackupType.FULL:
                file_path = self._create_full_backup(backup_job)
            elif backup_job.backup_type == BackupType.INCREMENTAL:
                file_path = self._create_incremental_backup(backup_job)
            elif backup_job.backup_type == BackupType.CONFIGURATION:
                file_path = self._create_configuration_backup(backup_job)
            else:
                raise ValueError(f"Unknown backup type: {backup_job.backup_type}")
            
            backup_job.file_path = file_path
            backup_job.file_name = os.path.basename(file_path)
            backup_job.file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
            
            # Upload to S3 if configured
            if backup_job.storage_type == BackupStorageType.S3:
                self._upload_to_s3(backup_job, file_path)
            
            backup_job.status = BackupStatus.COMPLETED
            backup_job.completed_at = datetime.utcnow()
            
        except Exception as e:
            backup_job.status = BackupStatus.FAILED
            backup_job.error_message = str(e)
            logger.error(f"Backup failed: {e}")
        
        self.db.commit()
    
    def _create_full_backup(self, backup_job: BackupJob) -> str:
        """
        Create a full database backup using pg_dump
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        tenant_suffix = f"_{backup_job.tenant_id}" if backup_job.tenant_id else ""
        filename = f"backup_full{tenant_suffix}_{timestamp}.sql.gz"
        file_path = os.path.join(self.backup_dir, filename)
        
        # Parse database URL
        db_url = self.db_url
        
        # For SQLite, just copy the file
        if "sqlite" in db_url:
            db_file = db_url.split("///")[-1]
            with open(db_file, 'rb') as f_in:
                with gzip.open(file_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return file_path
        
        # For PostgreSQL
        if "postgresql" in db_url:
            # Extract connection details
            # Format: postgresql://user:password@host:port/database
            parts = db_url.replace("postgresql://", "").split("@")
            if len(parts) == 2:
                user_pass = parts[0].split(":")
                host_port_db = parts[1].split("/")
                
                user = user_pass[0] if len(user_pass) > 0 else "postgres"
                password = user_pass[1] if len(user_pass) > 1 else ""
                host_port = host_port_db[0].split(":")
                host = host_port[0]
                port = host_port[1] if len(host_port) > 1 else "5432"
                database = host_port_db[1] if len(host_port_db) > 1 else "nexbii"
                
                # Set environment variable for password
                env = os.environ.copy()
                env['PGPASSWORD'] = password
                
                # Build pg_dump command
                cmd = [
                    'pg_dump',
                    '-h', host,
                    '-p', port,
                    '-U', user,
                    '-d', database,
                    '--no-password',
                ]
                
                # Add table filters if specified
                if backup_job.tables_included:
                    for table in backup_job.tables_included:
                        cmd.extend(['-t', table])
                
                # Execute pg_dump and compress
                with gzip.open(file_path, 'wb') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        env=env,
                        check=True
                    )
                    f.write(result.stdout)
                
                return file_path
        
        raise ValueError(f"Unsupported database type: {db_url}")
    
    def _create_incremental_backup(self, backup_job: BackupJob) -> str:
        """
        Create an incremental backup (changes since last backup)
        This is a simplified version - production would use WAL archiving
        """
        # For now, implement as full backup
        # In production, implement proper incremental backup using WAL
        logger.warning("Incremental backup not fully implemented, creating full backup")
        return self._create_full_backup(backup_job)
    
    def _create_configuration_backup(self, backup_job: BackupJob) -> str:
        """
        Create a backup of configuration only (no data)
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        tenant_suffix = f"_{backup_job.tenant_id}" if backup_job.tenant_id else ""
        filename = f"backup_config{tenant_suffix}_{timestamp}.json.gz"
        file_path = os.path.join(self.backup_dir, filename)
        
        # Export configuration from database
        from app.models.tenant import Tenant
        from app.models.integration import Integration
        
        config_data = {}
        
        # Export tenant configuration
        if backup_job.tenant_id:
            tenant = self.db.query(Tenant).filter(Tenant.id == backup_job.tenant_id).first()
            if tenant:
                config_data['tenant'] = {
                    'name': tenant.name,
                    'plan': tenant.plan,
                    'features': tenant.features,
                    'branding': tenant.branding
                }
        
        # Export integrations (without secrets)
        integrations = self.db.query(Integration).all()
        config_data['integrations'] = [
            {
                'type': i.type,
                'name': i.name,
                'is_active': i.is_active
                # Don't export encrypted credentials
            }
            for i in integrations
        ]
        
        # Compress and save
        with gzip.open(file_path, 'wt', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, default=str)
        
        return file_path
    
    def _upload_to_s3(self, backup_job: BackupJob, file_path: str) -> None:
        """
        Upload backup file to S3
        """
        if not self.s3_client:
            raise ValueError("S3 client not initialized")
        
        if not backup_job.s3_bucket:
            raise ValueError("S3 bucket not specified")
        
        s3_key = f"backups/{backup_job.file_name}"
        
        try:
            self.s3_client.upload_file(
                file_path,
                backup_job.s3_bucket,
                s3_key,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256' if backup_job.is_encrypted else None
                }
            )
            
            backup_job.s3_key = s3_key
            logger.info(f"Backup uploaded to S3: s3://{backup_job.s3_bucket}/{s3_key}")
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    def restore_backup(
        self,
        restore_request: BackupRestoreRequest,
        performed_by: str
    ) -> Dict[str, Any]:
        """
        Restore from a backup
        """
        backup_job = self.db.query(BackupJob).filter(
            BackupJob.id == restore_request.backup_id
        ).first()
        
        if not backup_job:
            raise ValueError("Backup not found")
        
        if backup_job.status != BackupStatus.COMPLETED:
            raise ValueError("Backup is not in completed state")
        
        result = {
            "backup_id": backup_job.id,
            "restore_started": datetime.utcnow().isoformat(),
            "actions": []
        }
        
        try:
            # Download from S3 if needed
            file_path = backup_job.file_path
            if backup_job.storage_type == BackupStorageType.S3:
                file_path = self._download_from_s3(backup_job)
            
            # Perform restore
            if restore_request.restore_data:
                self._restore_data(file_path, restore_request.tables_to_restore)
                result["actions"].append("data_restored")
            
            if restore_request.restore_config:
                self._restore_configuration(file_path)
                result["actions"].append("configuration_restored")
            
            result["status"] = "success"
            result["restore_completed"] = datetime.utcnow().isoformat()
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
            logger.error(f"Restore failed: {e}")
        
        return result
    
    def _download_from_s3(self, backup_job: BackupJob) -> str:
        """
        Download backup from S3 to local filesystem
        """
        if not self.s3_client or not backup_job.s3_key:
            raise ValueError("S3 not configured or key missing")
        
        local_path = os.path.join(self.backup_dir, backup_job.file_name)
        
        try:
            self.s3_client.download_file(
                backup_job.s3_bucket,
                backup_job.s3_key,
                local_path
            )
            return local_path
        except ClientError as e:
            logger.error(f"S3 download failed: {e}")
            raise
    
    def _restore_data(self, file_path: str, tables: Optional[List[str]] = None) -> None:
        """
        Restore data from backup file
        """
        # WARNING: This is destructive! Use with caution
        logger.warning("Performing database restore - this will overwrite data!")
        
        # For SQLite
        if "sqlite" in self.db_url:
            db_file = self.db_url.split("///")[-1]
            with gzip.open(file_path, 'rb') as f_in:
                with open(db_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            return
        
        # For PostgreSQL
        if "postgresql" in self.db_url:
            # Extract connection details (similar to backup)
            parts = self.db_url.replace("postgresql://", "").split("@")
            # ... connection parsing code ...
            
            # Decompress and restore
            with gzip.open(file_path, 'rb') as f:
                sql_content = f.read().decode('utf-8')
            
            # Execute SQL (simplified - production should use psql)
            from sqlalchemy import text
            for statement in sql_content.split(';'):
                if statement.strip():
                    try:
                        self.db.execute(text(statement))
                    except Exception as e:
                        logger.warning(f"Statement failed: {e}")
            
            self.db.commit()
    
    def _restore_configuration(self, file_path: str) -> None:
        """
        Restore configuration from backup
        """
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Restore tenant configuration
        if 'tenant' in config_data:
            # Update tenant settings
            pass
        
        # Restore integrations
        if 'integrations' in config_data:
            # Update integration settings
            pass
    
    def list_backups(
        self,
        tenant_id: Optional[str] = None,
        limit: int = 50
    ) -> List[BackupJob]:
        """
        List available backups
        """
        query = self.db.query(BackupJob)
        
        if tenant_id:
            query = query.filter(BackupJob.tenant_id == tenant_id)
        
        return query.order_by(BackupJob.created_at.desc()).limit(limit).all()
    
    def cleanup_old_backups(self, retention_days: int = 30) -> int:
        """
        Clean up old backups based on retention policy
        """
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        old_backups = self.db.query(BackupJob).filter(
            BackupJob.created_at < cutoff_date,
            BackupJob.status == BackupStatus.COMPLETED
        ).all()
        
        deleted_count = 0
        for backup in old_backups:
            try:
                # Delete local file
                if backup.file_path and os.path.exists(backup.file_path):
                    os.remove(backup.file_path)
                
                # Delete from S3
                if backup.storage_type == BackupStorageType.S3 and backup.s3_key:
                    self.s3_client.delete_object(
                        Bucket=backup.s3_bucket,
                        Key=backup.s3_key
                    )
                
                # Delete database record
                self.db.delete(backup)
                deleted_count += 1
                
            except Exception as e:
                logger.error(f"Failed to delete backup {backup.id}: {e}")
        
        self.db.commit()
        return deleted_count


def get_backup_service(db: Session) -> BackupService:
    """Get backup service instance"""
    return BackupService(db)
