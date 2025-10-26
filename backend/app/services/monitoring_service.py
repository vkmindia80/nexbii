"""
Monitoring Service for Phase 4.5 - Enterprise Admin
Collects and stores system metrics using configurable backends
"""
import psutil
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import json
import logging

from app.models.admin import SystemMetrics, SystemHealthCheck
from app.schemas.admin import (
    SystemMetricsCreate, SystemMetricsQuery, MetricTypeEnum,
    HealthCheckRequest
)

# Optional imports for different metric storage backends
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from influxdb_client import InfluxDBClient, Point
    from influxdb_client.client.write_api import SYNCHRONOUS
    INFLUXDB_AVAILABLE = True
except ImportError:
    INFLUXDB_AVAILABLE = False

logger = logging.getLogger(__name__)


class MonitoringService:
    """
    Service for collecting and storing system metrics
    Supports multiple backends: Database, Redis, InfluxDB
    """
    
    def __init__(self, db: Session, metric_storage: str = "database"):
        self.db = db
        self.metric_storage = metric_storage
        
        # Initialize Redis if available and configured
        self.redis_client = None
        if REDIS_AVAILABLE and metric_storage == "redis":
            try:
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
            except Exception as e:
                logger.warning(f"Redis not available: {e}")
        
        # Initialize InfluxDB if available and configured
        self.influx_client = None
        if INFLUXDB_AVAILABLE and metric_storage == "influxdb":
            try:
                influx_url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
                influx_token = os.getenv("INFLUXDB_TOKEN")
                influx_org = os.getenv("INFLUXDB_ORG", "nexbii")
                if influx_token:
                    self.influx_client = InfluxDBClient(
                        url=influx_url, token=influx_token, org=influx_org
                    )
            except Exception as e:
                logger.warning(f"InfluxDB not available: {e}")
    
    def collect_system_metrics(self) -> SystemMetricsCreate:
        """
        Collect current system metrics from the OS
        """
        try:
            # CPU and memory metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get active users count from database
            from app.models.user import User
            from app.models.admin import UserSession
            active_users = self.db.query(func.count(func.distinct(UserSession.user_id))).filter(
                UserSession.is_active == True,
                UserSession.last_activity >= datetime.utcnow() - timedelta(minutes=30)
            ).scalar() or 0
            
            # Get query and API metrics from recent activity
            from app.models.activity import Activity
            now = datetime.utcnow()
            last_minute = now - timedelta(minutes=1)
            
            api_requests = self.db.query(func.count(Activity.id)).filter(
                Activity.created_at >= last_minute
            ).scalar() or 0
            
            query_count = self.db.query(func.count(Activity.id)).filter(
                Activity.action == 'query_executed',
                Activity.created_at >= last_minute
            ).scalar() or 0
            
            # Get cache hit rate from cache service
            cache_hit_rate = self._get_cache_hit_rate()
            
            # Get average query time
            avg_query_time = self._get_avg_query_time()
            
            # Get error count
            error_count = self.db.query(func.count(Activity.id)).filter(
                Activity.action.like('%error%'),
                Activity.created_at >= last_minute
            ).scalar() or 0
            
            metrics = SystemMetricsCreate(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                active_users=active_users,
                api_requests=api_requests,
                query_count=query_count,
                cache_hit_rate=cache_hit_rate,
                avg_query_time=avg_query_time,
                error_count=error_count,
                additional_data={
                    "hostname": os.uname().nodename,
                    "python_version": os.sys.version,
                }
            )
            
            return metrics
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            # Return default metrics on error
            return SystemMetricsCreate(
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                error_count=1,
                metadata={"error": str(e)}
            )
    
    def store_metrics(self, metrics: SystemMetricsCreate) -> None:
        """
        Store metrics in configured backend
        """
        try:
            if self.metric_storage == "redis" and self.redis_client:
                self._store_metrics_redis(metrics)
            elif self.metric_storage == "influxdb" and self.influx_client:
                self._store_metrics_influxdb(metrics)
            else:
                self._store_metrics_database(metrics)
        except Exception as e:
            logger.error(f"Error storing metrics: {e}")
            # Fallback to database if other storage fails
            if self.metric_storage != "database":
                try:
                    self._store_metrics_database(metrics)
                except Exception as db_error:
                    logger.error(f"Fallback database storage also failed: {db_error}")
    
    def _store_metrics_database(self, metrics: SystemMetricsCreate) -> None:
        """Store metrics in PostgreSQL database"""
        metric_record = SystemMetrics(**metrics.model_dump())
        self.db.add(metric_record)
        self.db.commit()
    
    def _store_metrics_redis(self, metrics: SystemMetricsCreate) -> None:
        """Store metrics in Redis with TTL"""
        if not self.redis_client:
            return
        
        timestamp = datetime.utcnow().isoformat()
        key = f"metrics:{timestamp}"
        
        # Store as JSON with 7 days TTL
        self.redis_client.setex(
            key,
            7 * 24 * 60 * 60,  # 7 days
            json.dumps(metrics.model_dump())
        )
        
        # Also maintain a sorted set for time-based queries
        self.redis_client.zadd(
            "metrics:timeline",
            {key: datetime.utcnow().timestamp()}
        )
    
    def _store_metrics_influxdb(self, metrics: SystemMetricsCreate) -> None:
        """Store metrics in InfluxDB"""
        if not self.influx_client:
            return
        
        bucket = os.getenv("INFLUXDB_BUCKET", "nexbii_metrics")
        write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        
        point = Point("system_metrics") \
            .field("cpu_usage", metrics.cpu_usage) \
            .field("memory_usage", metrics.memory_usage) \
            .field("disk_usage", metrics.disk_usage) \
            .field("active_users", metrics.active_users) \
            .field("api_requests", metrics.api_requests) \
            .field("query_count", metrics.query_count) \
            .field("cache_hit_rate", metrics.cache_hit_rate) \
            .field("error_count", metrics.error_count)
        
        if metrics.avg_query_time:
            point = point.field("avg_query_time", metrics.avg_query_time)
        
        write_api.write(bucket=bucket, record=point)
    
    def get_metrics(
        self, 
        query: SystemMetricsQuery
    ) -> List[SystemMetrics]:
        """
        Retrieve metrics from configured backend
        """
        if query.metric_type.value == "redis" and self.redis_client:
            return self._get_metrics_redis(query)
        elif query.metric_type.value == "influxdb" and self.influx_client:
            return self._get_metrics_influxdb(query)
        else:
            return self._get_metrics_database(query)
    
    def _get_metrics_database(self, query: SystemMetricsQuery) -> List[SystemMetrics]:
        """Retrieve metrics from database"""
        db_query = self.db.query(SystemMetrics)
        
        if query.start_time:
            db_query = db_query.filter(SystemMetrics.timestamp >= query.start_time)
        if query.end_time:
            db_query = db_query.filter(SystemMetrics.timestamp <= query.end_time)
        
        db_query = db_query.order_by(desc(SystemMetrics.timestamp))
        db_query = db_query.limit(query.limit)
        
        return db_query.all()
    
    def _get_metrics_redis(self, query: SystemMetricsQuery) -> List[Dict[str, Any]]:
        """Retrieve metrics from Redis"""
        if not self.redis_client:
            return []
        
        # Get keys from timeline sorted set
        start_score = query.start_time.timestamp() if query.start_time else 0
        end_score = query.end_time.timestamp() if query.end_time else datetime.utcnow().timestamp()
        
        keys = self.redis_client.zrangebyscore(
            "metrics:timeline",
            start_score,
            end_score,
            start=0,
            num=query.limit
        )
        
        metrics = []
        for key in keys:
            data = self.redis_client.get(key)
            if data:
                metrics.append(json.loads(data))
        
        return metrics
    
    def _get_metrics_influxdb(self, query: SystemMetricsQuery) -> List[Dict[str, Any]]:
        """Retrieve metrics from InfluxDB"""
        if not self.influx_client:
            return []
        
        bucket = os.getenv("INFLUXDB_BUCKET", "nexbii_metrics")
        query_api = self.influx_client.query_api()
        
        # Build Flux query
        start_time = query.start_time.isoformat() if query.start_time else "-30d"
        end_time = query.end_time.isoformat() if query.end_time else "now()"
        
        flux_query = f'''
        from(bucket: "{bucket}")
            |> range(start: {start_time}, stop: {end_time})
            |> filter(fn: (r) => r._measurement == "system_metrics")
            |> limit(n: {query.limit})
        '''
        
        tables = query_api.query(flux_query)
        
        # Convert to list of dicts
        metrics = []
        for table in tables:
            for record in table.records:
                metrics.append({
                    "timestamp": record.get_time(),
                    "field": record.get_field(),
                    "value": record.get_value()
                })
        
        return metrics
    
    def _get_cache_hit_rate(self) -> float:
        """Get current cache hit rate from cache service"""
        try:
            from app.services.cache_service import cache_service
            stats = cache_service.get_stats()
            total = stats.get('total_queries', 0)
            hits = stats.get('cache_hits', 0)
            if total > 0:
                return (hits / total) * 100
        except Exception:
            pass
        return 0.0
    
    def _get_avg_query_time(self) -> Optional[float]:
        """Get average query execution time from recent queries"""
        try:
            from app.models.activity import Activity
            
            result = self.db.query(
                func.avg(Activity.duration)
            ).filter(
                Activity.action == 'query_executed',
                Activity.created_at >= datetime.utcnow() - timedelta(minutes=5),
                Activity.duration.isnot(None)
            ).scalar()
            
            return float(result) if result else None
        except Exception:
            return None
    
    def perform_health_check(self, request: HealthCheckRequest) -> SystemHealthCheck:
        """
        Perform comprehensive system health check
        """
        alerts = []
        
        # Check database
        database_status = "healthy"
        database_response_time = None
        if request.check_database:
            db_start = datetime.utcnow()
            try:
                self.db.execute("SELECT 1")
                database_response_time = (datetime.utcnow() - db_start).total_seconds() * 1000
                if database_response_time > 100:
                    database_status = "degraded"
                    alerts.append({"type": "database", "message": "Database response time is high"})
            except Exception as e:
                database_status = "down"
                alerts.append({"type": "database", "message": f"Database error: {str(e)}"})
        
        # Check Redis
        redis_status = "healthy"
        redis_response_time = None
        if request.check_redis:
            redis_start = datetime.utcnow()
            try:
                if self.redis_client:
                    self.redis_client.ping()
                    redis_response_time = (datetime.utcnow() - redis_start).total_seconds() * 1000
                    if redis_response_time > 50:
                        redis_status = "degraded"
                else:
                    redis_status = "not_configured"
            except Exception as e:
                redis_status = "down"
                alerts.append({"type": "redis", "message": f"Redis error: {str(e)}"})
        
        # API status (always healthy if we're running)
        api_status = "healthy"
        api_response_time = 10.0
        
        # Check external integrations if requested
        email_service_status = None
        slack_service_status = None
        
        if request.check_integrations:
            # Check email service
            try:
                from app.services.email_service import email_service
                if email_service.mock_mode:
                    email_service_status = "mock"
                else:
                    email_service_status = "healthy"
            except Exception:
                email_service_status = "not_configured"
            
            # Check Slack service
            try:
                from app.services.slack_service import slack_service
                if slack_service.mock_mode:
                    slack_service_status = "mock"
                else:
                    slack_service_status = "healthy"
            except Exception:
                slack_service_status = "not_configured"
        
        # Determine overall status
        if any(s == "down" for s in [database_status, redis_status, api_status]):
            overall_status = "critical"
        elif any(s == "degraded" for s in [database_status, redis_status, api_status]):
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        # Create health check record
        health_check = SystemHealthCheck(
            database_status=database_status,
            redis_status=redis_status,
            api_status=api_status,
            email_service_status=email_service_status,
            slack_service_status=slack_service_status,
            database_response_time=database_response_time,
            redis_response_time=redis_response_time,
            api_response_time=api_response_time,
            overall_status=overall_status,
            alerts_triggered=alerts if alerts else None
        )
        
        self.db.add(health_check)
        self.db.commit()
        self.db.refresh(health_check)
        
        return health_check
    
    def cleanup_old_metrics(self, days: int = 90) -> int:
        """
        Clean up old metrics from database
        Returns number of records deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted = self.db.query(SystemMetrics).filter(
            SystemMetrics.created_at < cutoff_date
        ).delete()
        
        self.db.commit()
        
        logger.info(f"Cleaned up {deleted} old metric records")
        return deleted
