"""
Data Governance Service
Phase 4.4: Data Governance
"""
import re
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta
import uuid

from app.models.governance import (
    DataCatalogEntry, DataLineage, DataClassificationRule,
    AccessRequest, DataImpactAnalysis, ClassificationLevel, PIIType, ApprovalStatus
)
from app.models.datasource import DataSource
from app.models.query import Query
from app.models.dashboard import Dashboard
from app.schemas.governance import (
    DataCatalogEntryCreate, DataCatalogEntryUpdate,
    DataLineageCreate, DataClassificationRuleCreate,
    AccessRequestCreate, ScanRequest, ScanResult,
    LineageGraph, ImpactAnalysisRequest
)


class GovernanceService:
    """Service for data governance operations"""
    
    # PII Detection Patterns
    PII_PATTERNS = {
        PIIType.SSN: r'\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b',
        PIIType.EMAIL: r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        PIIType.PHONE: r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
        PIIType.CREDIT_CARD: r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        PIIType.PASSPORT: r'\b[A-Z]{1,2}\d{6,9}\b',
        PIIType.DRIVER_LICENSE: r'\b[A-Z]{1,2}\d{5,8}\b',
    }
    
    COLUMN_NAME_PATTERNS = {
        PIIType.SSN: r'(ssn|social|security)',
        PIIType.EMAIL: r'(email|e_mail|mail)',
        PIIType.PHONE: r'(phone|tel|mobile|cell)',
        PIIType.CREDIT_CARD: r'(card|cc|credit)',
        PIIType.ADDRESS: r'(address|addr|street|city|zip|postal)',
        PIIType.DATE_OF_BIRTH: r'(dob|birth|birthday)',
    }
    
    # ==================== Data Catalog ====================
    
    @staticmethod
    def create_catalog_entry(
        db: Session,
        entry_data: DataCatalogEntryCreate,
        tenant_id: str,
        user_id: str
    ) -> DataCatalogEntry:
        """Create a new catalog entry"""
        entry = DataCatalogEntry(
            **entry_data.model_dump(),
            tenant_id=tenant_id,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def get_catalog_entries(
        db: Session,
        tenant_id: str,
        datasource_id: Optional[str] = None,
        table_name: Optional[str] = None,
        classification_level: Optional[ClassificationLevel] = None,
        is_pii: Optional[bool] = None,
        search_query: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[DataCatalogEntry], int]:
        """Get catalog entries with filters"""
        query = db.query(DataCatalogEntry).filter(
            DataCatalogEntry.tenant_id == tenant_id
        )
        
        if datasource_id:
            query = query.filter(DataCatalogEntry.datasource_id == datasource_id)
        
        if table_name:
            query = query.filter(DataCatalogEntry.table_name == table_name)
        
        if classification_level:
            query = query.filter(DataCatalogEntry.classification_level == classification_level)
        
        if is_pii is not None:
            query = query.filter(DataCatalogEntry.is_pii == is_pii)
        
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.filter(
                or_(
                    DataCatalogEntry.table_name.ilike(search_pattern),
                    DataCatalogEntry.column_name.ilike(search_pattern),
                    DataCatalogEntry.description.ilike(search_pattern),
                    DataCatalogEntry.display_name.ilike(search_pattern)
                )
            )
        
        total = query.count()
        entries = query.order_by(DataCatalogEntry.created_at.desc())\
                      .limit(limit).offset(offset).all()
        
        return entries, total
    
    @staticmethod
    def update_catalog_entry(
        db: Session,
        entry_id: str,
        entry_data: DataCatalogEntryUpdate,
        user_id: str
    ) -> Optional[DataCatalogEntry]:
        """Update a catalog entry"""
        entry = db.query(DataCatalogEntry).filter(DataCatalogEntry.id == entry_id).first()
        if not entry:
            return None
        
        update_data = entry_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entry, key, value)
        
        entry.updated_by = user_id
        entry.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(entry)
        return entry
    
    @staticmethod
    def delete_catalog_entry(db: Session, entry_id: str) -> bool:
        """Delete a catalog entry"""
        entry = db.query(DataCatalogEntry).filter(DataCatalogEntry.id == entry_id).first()
        if not entry:
            return False
        
        db.delete(entry)
        db.commit()
        return True
    
    @staticmethod
    def get_catalog_statistics(db: Session, tenant_id: str) -> dict:
        """Get catalog statistics"""
        total_entries = db.query(DataCatalogEntry).filter(
            DataCatalogEntry.tenant_id == tenant_id
        ).count()
        
        total_tables = db.query(DataCatalogEntry.table_name).filter(
            and_(
                DataCatalogEntry.tenant_id == tenant_id,
                DataCatalogEntry.column_name.is_(None)
            )
        ).distinct().count()
        
        total_columns = db.query(DataCatalogEntry).filter(
            and_(
                DataCatalogEntry.tenant_id == tenant_id,
                DataCatalogEntry.column_name.isnot(None)
            )
        ).count()
        
        # Count by classification level
        by_classification = {}
        for level in ClassificationLevel:
            count = db.query(DataCatalogEntry).filter(
                and_(
                    DataCatalogEntry.tenant_id == tenant_id,
                    DataCatalogEntry.classification_level == level
                )
            ).count()
            by_classification[level.value] = count
        
        pii_count = db.query(DataCatalogEntry).filter(
            and_(
                DataCatalogEntry.tenant_id == tenant_id,
                DataCatalogEntry.is_pii == True
            )
        ).count()
        
        datasources_cataloged = db.query(DataCatalogEntry.datasource_id).filter(
            DataCatalogEntry.tenant_id == tenant_id
        ).distinct().count()
        
        return {
            "total_entries": total_entries,
            "total_tables": total_tables,
            "total_columns": total_columns,
            "by_classification": by_classification,
            "pii_count": pii_count,
            "datasources_cataloged": datasources_cataloged
        }
    
    # ==================== Data Lineage ====================
    
    @staticmethod
    def create_lineage(
        db: Session,
        lineage_data: DataLineageCreate,
        tenant_id: str
    ) -> DataLineage:
        """Create a lineage entry"""
        lineage = DataLineage(
            **lineage_data.model_dump(),
            tenant_id=tenant_id
        )
        db.add(lineage)
        db.commit()
        db.refresh(lineage)
        return lineage
    
    @staticmethod
    def get_lineage_graph(
        db: Session,
        tenant_id: str,
        resource_type: str,
        resource_id: str
    ) -> LineageGraph:
        """Build lineage graph for a resource"""
        # Get all lineage entries for this resource (as source or target)
        lineages = db.query(DataLineage).filter(
            and_(
                DataLineage.tenant_id == tenant_id,
                DataLineage.is_active == True,
                or_(
                    and_(
                        DataLineage.source_type == resource_type,
                        DataLineage.source_id == resource_id
                    ),
                    and_(
                        DataLineage.target_type == resource_type,
                        DataLineage.target_id == resource_id
                    )
                )
            )
        ).all()
        
        nodes = {}
        edges = []
        
        for lineage in lineages:
            # Add source node
            source_key = f"{lineage.source_type}:{lineage.source_id}"
            if source_key not in nodes:
                nodes[source_key] = {
                    "id": source_key,
                    "type": lineage.source_type,
                    "resource_id": lineage.source_id,
                    "table": lineage.source_table,
                    "column": lineage.source_column
                }
            
            # Add target node
            target_key = f"{lineage.target_type}:{lineage.target_id}"
            if target_key not in nodes:
                nodes[target_key] = {
                    "id": target_key,
                    "type": lineage.target_type,
                    "resource_id": lineage.target_id,
                    "table": lineage.target_table,
                    "column": lineage.target_column
                }
            
            # Add edge
            edges.append({
                "source": source_key,
                "target": target_key,
                "transformation": lineage.transformation_type,
                "confidence": lineage.confidence_score
            })
        
        return LineageGraph(
            nodes=list(nodes.values()),
            edges=edges
        )
    
    @staticmethod
    def analyze_impact(
        db: Session,
        request: ImpactAnalysisRequest,
        tenant_id: str,
        user_id: str
    ) -> DataImpactAnalysis:
        """Analyze impact of changes to a resource"""
        # Find all downstream dependencies
        affected_queries = []
        affected_dashboards = []
        affected_users = set()
        
        # Get lineage where this resource is the source
        lineages = db.query(DataLineage).filter(
            and_(
                DataLineage.tenant_id == tenant_id,
                DataLineage.source_type == request.affected_resource_type,
                DataLineage.source_id == request.affected_resource_id,
                DataLineage.is_active == True
            )
        ).all()
        
        # Trace downstream impacts
        for lineage in lineages:
            if lineage.target_type == "query":
                query = db.query(Query).filter(Query.id == lineage.target_id).first()
                if query:
                    affected_queries.append(query.id)
                    if query.created_by:
                        affected_users.add(query.created_by)
            
            elif lineage.target_type == "dashboard":
                dashboard = db.query(Dashboard).filter(Dashboard.id == lineage.target_id).first()
                if dashboard:
                    affected_dashboards.append(dashboard.id)
                    if dashboard.created_by:
                        affected_users.add(dashboard.created_by)
        
        # Determine impact level
        total_affected = len(affected_queries) + len(affected_dashboards)
        if total_affected == 0:
            impact_level = "low"
        elif total_affected <= 5:
            impact_level = "medium"
        elif total_affected <= 20:
            impact_level = "high"
        else:
            impact_level = "critical"
        
        # Generate summary
        impact_summary = f"Change will affect {len(affected_queries)} queries, {len(affected_dashboards)} dashboards, and {len(affected_users)} users."
        
        # Generate recommendations
        recommendations = [
            "Review and test all affected queries before deploying changes",
            "Notify affected users about the upcoming changes",
            "Create backups of current configurations"
        ]
        
        if impact_level in ["high", "critical"]:
            recommendations.extend([
                "Schedule maintenance window for changes",
                "Prepare rollback plan",
                "Consider phased rollout"
            ])
        
        mitigation_steps = [
            "Update query logic to accommodate changes",
            "Refresh dashboard data after changes",
            "Verify data integrity post-change"
        ]
        
        # Save analysis
        analysis = DataImpactAnalysis(
            id=str(uuid.uuid4()),
            tenant_id=tenant_id,
            change_type=request.change_type,
            affected_resource_type=request.affected_resource_type,
            affected_resource_id=request.affected_resource_id,
            affected_resource_name=request.affected_resource_name,
            impact_level=impact_level,
            impact_summary=impact_summary,
            affected_queries=affected_queries,
            affected_dashboards=affected_dashboards,
            affected_users=list(affected_users),
            recommendations=recommendations,
            mitigation_steps=mitigation_steps,
            analyzed_by=user_id
        )
        
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return analysis
    
    # ==================== Classification & PII ====================
    
    @staticmethod
    def create_classification_rule(
        db: Session,
        rule_data: DataClassificationRuleCreate,
        tenant_id: str,
        user_id: str
    ) -> DataClassificationRule:
        """Create a classification rule"""
        rule = DataClassificationRule(
            **rule_data.model_dump(),
            tenant_id=tenant_id,
            created_by=user_id,
            updated_by=user_id
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    
    @staticmethod
    def get_classification_rules(
        db: Session,
        tenant_id: str,
        is_enabled: Optional[bool] = None
    ) -> List[DataClassificationRule]:
        """Get classification rules"""
        query = db.query(DataClassificationRule).filter(
            DataClassificationRule.tenant_id == tenant_id
        )
        
        if is_enabled is not None:
            query = query.filter(DataClassificationRule.is_enabled == is_enabled)
        
        return query.order_by(DataClassificationRule.priority.desc()).all()
    
    @staticmethod
    def scan_for_pii(
        db: Session,
        scan_request: ScanRequest,
        tenant_id: str
    ) -> List[ScanResult]:
        """Scan datasource for PII"""
        results = []
        
        # Get datasource
        datasource = db.query(DataSource).filter(
            and_(
                DataSource.id == scan_request.datasource_id,
                DataSource.tenant_id == tenant_id
            )
        ).first()
        
        if not datasource:
            return results
        
        # Get classification rules
        rules = GovernanceService.get_classification_rules(db, tenant_id, is_enabled=True)
        
        # Get schema from datasource (this would need actual DB connection)
        # For now, we'll return mock results or search in catalog
        catalog_entries = db.query(DataCatalogEntry).filter(
            and_(
                DataCatalogEntry.tenant_id == tenant_id,
                DataCatalogEntry.datasource_id == scan_request.datasource_id
            )
        ).all()
        
        for entry in catalog_entries:
            if entry.column_name:
                # Check column name against patterns
                for rule in rules:
                    if rule.column_name_pattern:
                        pattern = re.compile(rule.column_name_pattern, re.IGNORECASE)
                        if pattern.search(entry.column_name or ""):
                            results.append(ScanResult(
                                datasource_id=entry.datasource_id,
                                table_name=entry.table_name,
                                column_name=entry.column_name,
                                pii_type=rule.pii_type,
                                matches_found=1,
                                confidence_score=80,
                                sample_values=[]
                            ))
        
        return results
    
    # ==================== Access Requests ====================
    
    @staticmethod
    def create_access_request(
        db: Session,
        request_data: AccessRequestCreate,
        tenant_id: str,
        requester_id: str
    ) -> AccessRequest:
        """Create an access request"""
        # Check if resource is classified
        catalog_entry = db.query(DataCatalogEntry).filter(
            and_(
                DataCatalogEntry.tenant_id == tenant_id,
                DataCatalogEntry.datasource_id == request_data.resource_id
            )
        ).first()
        
        requires_compliance = False
        classification_level = None
        
        if catalog_entry:
            classification_level = catalog_entry.classification_level
            # Restricted data requires compliance approval
            if catalog_entry.classification_level == ClassificationLevel.RESTRICTED:
                requires_compliance = True
        
        request = AccessRequest(
            **request_data.model_dump(),
            tenant_id=tenant_id,
            requester_id=requester_id,
            classification_level=classification_level,
            requires_compliance_approval=requires_compliance
        )
        
        db.add(request)
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def get_access_requests(
        db: Session,
        tenant_id: str,
        status: Optional[ApprovalStatus] = None,
        requester_id: Optional[str] = None,
        approver_id: Optional[str] = None
    ) -> List[AccessRequest]:
        """Get access requests"""
        query = db.query(AccessRequest).filter(
            AccessRequest.tenant_id == tenant_id
        )
        
        if status:
            query = query.filter(AccessRequest.status == status)
        
        if requester_id:
            query = query.filter(AccessRequest.requester_id == requester_id)
        
        if approver_id:
            query = query.filter(
                or_(
                    AccessRequest.approver_id == approver_id,
                    AccessRequest.compliance_approver_id == approver_id
                )
            )
        
        return query.order_by(AccessRequest.created_at.desc()).all()
    
    @staticmethod
    def approve_access_request(
        db: Session,
        request_id: str,
        approver_id: str,
        approval_notes: Optional[str] = None,
        is_compliance_approval: bool = False
    ) -> Optional[AccessRequest]:
        """Approve an access request"""
        request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
        if not request:
            return None
        
        if is_compliance_approval:
            request.compliance_approver_id = approver_id
            request.compliance_approved_at = datetime.utcnow()
            request.compliance_notes = approval_notes
            
            # Check if also needs regular approval
            if request.approver_id:
                request.status = ApprovalStatus.APPROVED
        else:
            request.approver_id = approver_id
            request.approved_at = datetime.utcnow()
            request.approval_notes = approval_notes
            
            # Check if also needs compliance approval
            if not request.requires_compliance_approval:
                request.status = ApprovalStatus.APPROVED
        
        # Set expiration date if approved
        if request.status == ApprovalStatus.APPROVED and request.duration_days:
            request.expires_at = datetime.utcnow() + timedelta(days=request.duration_days)
        
        db.commit()
        db.refresh(request)
        return request
    
    @staticmethod
    def reject_access_request(
        db: Session,
        request_id: str,
        approver_id: str,
        rejection_notes: str
    ) -> Optional[AccessRequest]:
        """Reject an access request"""
        request = db.query(AccessRequest).filter(AccessRequest.id == request_id).first()
        if not request:
            return None
        
        request.status = ApprovalStatus.REJECTED
        request.approver_id = approver_id
        request.approval_notes = rejection_notes
        request.approved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(request)
        return request
