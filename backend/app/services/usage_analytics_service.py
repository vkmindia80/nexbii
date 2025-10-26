"""
Usage Analytics Service for Phase 4.5 - Enterprise Admin
Tracks and analyzes tenant usage for billing and analytics
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging

from app.models.admin import TenantUsageMetrics, UserActivity
from app.models.user import User
from app.models.query import Query
from app.models.dashboard import Dashboard
from app.models.datasource import DataSource
from app.schemas.admin import (
    TenantUsageMetricsCreate, TenantUsageQuery, UsageAnalyticsSummary
)

logger = logging.getLogger(__name__)


class UsageAnalyticsService:
    """
    Service for tracking and analyzing tenant usage
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def aggregate_daily_usage(self, tenant_id: str, date: datetime) -> TenantUsageMetricsCreate:
        """
        Aggregate usage metrics for a tenant for a specific date
        """
        # Start and end of the day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # User metrics
        total_users = self.db.query(func.count(User.id)).filter(
            User.tenant_id == tenant_id
        ).scalar() or 0
        
        active_users = self.db.query(func.count(func.distinct(UserActivity.user_id))).filter(
            UserActivity.tenant_id == tenant_id,
            UserActivity.timestamp >= start_of_day,
            UserActivity.timestamp < end_of_day
        ).scalar() or 0
        
        new_users = self.db.query(func.count(User.id)).filter(
            User.tenant_id == tenant_id,
            User.created_at >= start_of_day,
            User.created_at < end_of_day
        ).scalar() or 0
        
        # Usage metrics
        query_count = self.db.query(func.count(UserActivity.id)).filter(
            UserActivity.tenant_id == tenant_id,
            UserActivity.action == 'query_executed',
            UserActivity.timestamp >= start_of_day,
            UserActivity.timestamp < end_of_day
        ).scalar() or 0
        
        dashboard_count = self.db.query(func.count(Dashboard.id)).filter(
            Dashboard.tenant_id == tenant_id
        ).scalar() or 0
        
        datasource_count = self.db.query(func.count(DataSource.id)).filter(
            DataSource.tenant_id == tenant_id
        ).scalar() or 0
        
        api_calls = self.db.query(func.count(UserActivity.id)).filter(
            UserActivity.tenant_id == tenant_id,
            UserActivity.timestamp >= start_of_day,
            UserActivity.timestamp < end_of_day
        ).scalar() or 0
        
        # Performance metrics
        avg_query_time = self.db.query(func.avg(UserActivity.duration)).filter(
            UserActivity.tenant_id == tenant_id,
            UserActivity.action == 'query_executed',
            UserActivity.duration.isnot(None),
            UserActivity.timestamp >= start_of_day,
            UserActivity.timestamp < end_of_day
        ).scalar()
        
        # Cache hit rate (would need to be calculated from cache service)
        cache_hit_rate = self._calculate_cache_hit_rate(tenant_id, start_of_day, end_of_day)
        
        # Storage used (approximate based on data sources)
        storage_used = self._calculate_storage_used(tenant_id)
        
        # Billing calculation (simple example - customize based on pricing model)
        billable_amount = self._calculate_billable_amount(
            active_users=active_users,
            query_count=query_count,
            api_calls=api_calls,
            storage_used=storage_used
        )
        
        return TenantUsageMetricsCreate(
            tenant_id=tenant_id,
            date=date,
            active_users=active_users,
            total_users=total_users,
            new_users=new_users,
            query_count=query_count,
            dashboard_count=dashboard_count,
            datasource_count=datasource_count,
            api_calls=api_calls,
            storage_used=storage_used,
            avg_query_time=float(avg_query_time) if avg_query_time else None,
            cache_hit_rate=cache_hit_rate,
            billable_amount=billable_amount,
            metadata={
                "aggregated_at": datetime.utcnow().isoformat(),
                "period": "daily"
            }
        )
    
    def store_usage_metrics(self, metrics: TenantUsageMetricsCreate) -> TenantUsageMetrics:
        """
        Store aggregated usage metrics
        """
        # Check if metrics already exist for this date
        existing = self.db.query(TenantUsageMetrics).filter(
            TenantUsageMetrics.tenant_id == metrics.tenant_id,
            TenantUsageMetrics.date == metrics.date
        ).first()
        
        if existing:
            # Update existing metrics
            for key, value in metrics.model_dump().items():
                if key not in ['tenant_id', 'date']:
                    setattr(existing, key, value)
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            # Create new metrics record
            usage_metrics = TenantUsageMetrics(**metrics.model_dump())
            self.db.add(usage_metrics)
            self.db.commit()
            self.db.refresh(usage_metrics)
            return usage_metrics
    
    def get_usage_metrics(
        self,
        query: TenantUsageQuery
    ) -> List[TenantUsageMetrics]:
        """
        Retrieve usage metrics with filters
        """
        db_query = self.db.query(TenantUsageMetrics)
        
        if query.tenant_id:
            db_query = db_query.filter(TenantUsageMetrics.tenant_id == query.tenant_id)
        
        if query.start_date:
            db_query = db_query.filter(TenantUsageMetrics.date >= query.start_date)
        
        if query.end_date:
            db_query = db_query.filter(TenantUsageMetrics.date <= query.end_date)
        
        db_query = db_query.order_by(desc(TenantUsageMetrics.date))
        db_query = db_query.limit(query.limit)
        
        return db_query.all()
    
    def get_usage_summary(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> UsageAnalyticsSummary:
        """
        Get usage analytics summary for a tenant over a period
        """
        # Get all metrics for the period
        metrics = self.get_usage_metrics(
            TenantUsageQuery(
                tenant_id=tenant_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
        )
        
        if not metrics:
            # No data available, return empty summary
            return UsageAnalyticsSummary(
                tenant_id=tenant_id,
                period_start=start_date,
                period_end=end_date,
                total_users=0,
                active_users=0,
                total_queries=0,
                total_dashboards=0,
                total_api_calls=0,
                storage_used_mb=0.0,
                estimated_cost=0.0,
                usage_trend=[]
            )
        
        # Calculate aggregates
        total_queries = sum(m.query_count for m in metrics)
        total_api_calls = sum(m.api_calls for m in metrics)
        avg_active_users = int(sum(m.active_users for m in metrics) / len(metrics))
        max_users = max(m.total_users for m in metrics)
        current_storage = metrics[0].storage_used if metrics else 0.0
        total_cost = sum(m.billable_amount for m in metrics)
        latest_dashboards = metrics[0].dashboard_count if metrics else 0
        
        # Build usage trend (daily breakdown)
        usage_trend = []
        for metric in reversed(metrics):  # Chronological order
            usage_trend.append({
                "date": metric.date.isoformat(),
                "active_users": metric.active_users,
                "queries": metric.query_count,
                "api_calls": metric.api_calls,
                "cost": metric.billable_amount
            })
        
        return UsageAnalyticsSummary(
            tenant_id=tenant_id,
            period_start=start_date,
            period_end=end_date,
            total_users=max_users,
            active_users=avg_active_users,
            total_queries=total_queries,
            total_dashboards=latest_dashboards,
            total_api_calls=total_api_calls,
            storage_used_mb=current_storage,
            estimated_cost=total_cost,
            usage_trend=usage_trend
        )
    
    def _calculate_cache_hit_rate(
        self,
        tenant_id: str,
        start_time: datetime,
        end_time: datetime
    ) -> Optional[float]:
        """
        Calculate cache hit rate for a tenant in a time period
        """
        try:
            # Query cache hits and misses from activity logs
            cache_hits = self.db.query(func.count(UserActivity.id)).filter(
                UserActivity.tenant_id == tenant_id,
                UserActivity.action == 'cache_hit',
                UserActivity.timestamp >= start_time,
                UserActivity.timestamp < end_time
            ).scalar() or 0
            
            cache_misses = self.db.query(func.count(UserActivity.id)).filter(
                UserActivity.tenant_id == tenant_id,
                UserActivity.action == 'cache_miss',
                UserActivity.timestamp >= start_time,
                UserActivity.timestamp < end_time
            ).scalar() or 0
            
            total = cache_hits + cache_misses
            if total > 0:
                return (cache_hits / total) * 100
            
        except Exception as e:
            logger.warning(f"Error calculating cache hit rate: {e}")
        
        return None
    
    def _calculate_storage_used(self, tenant_id: str) -> float:
        """
        Calculate storage used by a tenant (in MB)
        This is an approximation - you might want to implement more accurate tracking
        """
        # Count various objects and estimate storage
        queries = self.db.query(func.count(Query.id)).filter(
            Query.tenant_id == tenant_id
        ).scalar() or 0
        
        dashboards = self.db.query(func.count(Dashboard.id)).filter(
            Dashboard.tenant_id == tenant_id
        ).scalar() or 0
        
        datasources = self.db.query(func.count(DataSource.id)).filter(
            DataSource.tenant_id == tenant_id
        ).scalar() or 0
        
        # Rough estimate: 1KB per query, 5KB per dashboard, 2KB per datasource
        estimated_mb = (queries * 1 + dashboards * 5 + datasources * 2) / 1024
        
        return round(estimated_mb, 2)
    
    def _calculate_billable_amount(
        self,
        active_users: int,
        query_count: int,
        api_calls: int,
        storage_used: float
    ) -> float:
        """
        Calculate billable amount based on usage
        Customize this based on your pricing model
        """
        # Example pricing model:
        # $5 per active user per month (prorated daily)
        # $0.01 per 100 queries
        # $0.005 per 1000 API calls
        # $0.10 per GB storage per month (prorated daily)
        
        user_cost = active_users * (5.0 / 30)  # Daily proration
        query_cost = (query_count / 100) * 0.01
        api_cost = (api_calls / 1000) * 0.005
        storage_cost = (storage_used / 1024) * (0.10 / 30)  # GB daily proration
        
        total = user_cost + query_cost + api_cost + storage_cost
        
        return round(total, 2)
    
    def aggregate_all_tenants_usage(self, date: datetime) -> List[TenantUsageMetrics]:
        """
        Aggregate usage for all tenants for a specific date
        Useful for batch processing
        """
        from app.models.tenant import Tenant
        
        tenants = self.db.query(Tenant).filter(Tenant.is_active == True).all()
        
        results = []
        for tenant in tenants:
            try:
                metrics = self.aggregate_daily_usage(tenant.id, date)
                stored_metrics = self.store_usage_metrics(metrics)
                results.append(stored_metrics)
            except Exception as e:
                logger.error(f"Error aggregating usage for tenant {tenant.id}: {e}")
        
        return results
    
    def get_billing_report(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        Generate a billing report for a tenant
        """
        metrics = self.get_usage_metrics(
            TenantUsageQuery(
                tenant_id=tenant_id,
                start_date=start_date,
                end_date=end_date,
                limit=1000
            )
        )
        
        # Calculate totals
        total_cost = sum(m.billable_amount for m in metrics)
        total_days = len(metrics)
        
        # Breakdown by category
        user_costs = sum(m.active_users * (5.0 / 30) for m in metrics)
        query_costs = sum((m.query_count / 100) * 0.01 for m in metrics)
        api_costs = sum((m.api_calls / 1000) * 0.005 for m in metrics)
        storage_costs = sum((m.storage_used / 1024) * (0.10 / 30) for m in metrics)
        
        return {
            "tenant_id": tenant_id,
            "billing_period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": total_days
            },
            "total_amount": round(total_cost, 2),
            "breakdown": {
                "users": round(user_costs, 2),
                "queries": round(query_costs, 2),
                "api_calls": round(api_costs, 2),
                "storage": round(storage_costs, 2)
            },
            "usage_summary": {
                "avg_active_users": round(sum(m.active_users for m in metrics) / total_days if total_days > 0 else 0, 1),
                "total_queries": sum(m.query_count for m in metrics),
                "total_api_calls": sum(m.api_calls for m in metrics),
                "avg_storage_mb": round(sum(m.storage_used for m in metrics) / total_days if total_days > 0 else 0, 2)
            },
            "generated_at": datetime.utcnow().isoformat()
        }


def get_usage_analytics_service(db: Session) -> UsageAnalyticsService:
    """Get usage analytics service instance"""
    return UsageAnalyticsService(db)
