"""
Data Governance API Endpoints
Phase 4.4: Data Governance

Routes:
- Data Catalog: /api/governance/catalog
- Data Lineage: /api/governance/lineage
- Data Classification: /api/governance/classification
- Access Requests: /api/governance/access-requests
"""
from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.schemas.governance import (
    DataCatalogEntry, DataCatalogEntryCreate, DataCatalogEntryUpdate,
    DataLineage, DataLineageCreate, LineageGraph,
    DataClassificationRule, DataClassificationRuleCreate, DataClassificationRuleUpdate,
    AccessRequest, AccessRequestCreate, AccessRequestUpdate,
    ScanRequest, ScanResult, ImpactAnalysisRequest, ImpactAnalysisResult,
    CatalogStatistics, ClassificationLevel, ApprovalStatus
)
from app.services.governance_service import GovernanceService

router = APIRouter()


# ==================== Data Catalog Endpoints ====================

@router.post("/catalog", response_model=DataCatalogEntry, tags=["Data Catalog"])
def create_catalog_entry(
    entry: DataCatalogEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new data catalog entry
    
    **Requires:** Editor or Admin role
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        return GovernanceService.create_catalog_entry(
            db=db,
            entry_data=entry,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create catalog entry: {str(e)}")


@router.get("/catalog", response_model=dict, tags=["Data Catalog"])
def get_catalog_entries(
    datasource_id: Optional[str] = None,
    table_name: Optional[str] = None,
    classification_level: Optional[ClassificationLevel] = None,
    is_pii: Optional[bool] = None,
    search: Optional[str] = None,
    limit: int = QueryParam(50, ge=1, le=100),
    offset: int = QueryParam(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get data catalog entries with optional filters
    
    **Query Parameters:**
    - datasource_id: Filter by datasource
    - table_name: Filter by table name
    - classification_level: Filter by classification level
    - is_pii: Filter by PII status
    - search: Search in table/column names and descriptions
    - limit: Number of results (1-100, default: 50)
    - offset: Pagination offset
    """
    try:
        entries, total = GovernanceService.get_catalog_entries(
            db=db,
            tenant_id=current_user.tenant_id,
            datasource_id=datasource_id,
            table_name=table_name,
            classification_level=classification_level,
            is_pii=is_pii,
            search_query=search,
            limit=limit,
            offset=offset
        )
        
        return {
            "entries": entries,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get catalog entries: {str(e)}")


@router.get("/catalog/statistics", response_model=CatalogStatistics, tags=["Data Catalog"])
def get_catalog_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for the data catalog"""
    try:
        stats = GovernanceService.get_catalog_statistics(db, current_user.tenant_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/catalog/{entry_id}", response_model=DataCatalogEntry, tags=["Data Catalog"])
def get_catalog_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific catalog entry by ID"""
    from app.models.governance import DataCatalogEntry as DataCatalogEntryModel
    
    entry = db.query(DataCatalogEntryModel).filter(
        DataCatalogEntryModel.id == entry_id,
        DataCatalogEntryModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Catalog entry not found")
    
    return entry


@router.put("/catalog/{entry_id}", response_model=DataCatalogEntry, tags=["Data Catalog"])
def update_catalog_entry(
    entry_id: str,
    entry_update: DataCatalogEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a catalog entry
    
    **Requires:** Editor or Admin role
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    # Verify entry belongs to tenant
    from app.models.governance import DataCatalogEntry as DataCatalogEntryModel
    entry = db.query(DataCatalogEntryModel).filter(
        DataCatalogEntryModel.id == entry_id,
        DataCatalogEntryModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Catalog entry not found")
    
    try:
        updated = GovernanceService.update_catalog_entry(
            db=db,
            entry_id=entry_id,
            entry_data=entry_update,
            user_id=current_user.id
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Failed to update entry")
        
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update catalog entry: {str(e)}")


@router.delete("/catalog/{entry_id}", tags=["Data Catalog"])
def delete_catalog_entry(
    entry_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a catalog entry
    
    **Requires:** Admin role
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify entry belongs to tenant
    from app.models.governance import DataCatalogEntry as DataCatalogEntryModel
    entry = db.query(DataCatalogEntryModel).filter(
        DataCatalogEntryModel.id == entry_id,
        DataCatalogEntryModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Catalog entry not found")
    
    try:
        success = GovernanceService.delete_catalog_entry(db, entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Failed to delete entry")
        
        return {"message": "Catalog entry deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete catalog entry: {str(e)}")


@router.get("/catalog/statistics", response_model=CatalogStatistics, tags=["Data Catalog"])
def get_catalog_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for the data catalog"""
    try:
        stats = GovernanceService.get_catalog_statistics(db, current_user.tenant_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


# ==================== Data Lineage Endpoints ====================

@router.post("/lineage", response_model=DataLineage, tags=["Data Lineage"])
def create_lineage(
    lineage: DataLineageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a lineage entry
    
    **Requires:** Editor or Admin role
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        return GovernanceService.create_lineage(
            db=db,
            lineage_data=lineage,
            tenant_id=current_user.tenant_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create lineage: {str(e)}")


@router.get("/lineage/graph/{resource_type}/{resource_id}", response_model=LineageGraph, tags=["Data Lineage"])
def get_lineage_graph(
    resource_type: str,
    resource_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get lineage graph for a resource
    
    **Resource Types:**
    - datasource
    - query
    - dashboard
    """
    try:
        return GovernanceService.get_lineage_graph(
            db=db,
            tenant_id=current_user.tenant_id,
            resource_type=resource_type,
            resource_id=resource_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get lineage graph: {str(e)}")


@router.post("/lineage/impact-analysis", response_model=ImpactAnalysisResult, tags=["Data Lineage"])
def analyze_impact(
    request: ImpactAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Analyze impact of changes to a resource
    
    **Change Types:**
    - schema_change
    - data_deletion
    - source_removal
    - transformation_change
    """
    try:
        return GovernanceService.analyze_impact(
            db=db,
            request=request,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze impact: {str(e)}")


# ==================== Data Classification Endpoints ====================

@router.post("/classification/rules", response_model=DataClassificationRule, tags=["Data Classification"])
def create_classification_rule(
    rule: DataClassificationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a data classification rule
    
    **Requires:** Admin role
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return GovernanceService.create_classification_rule(
            db=db,
            rule_data=rule,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")


@router.get("/classification/rules", response_model=List[DataClassificationRule], tags=["Data Classification"])
def get_classification_rules(
    is_enabled: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all classification rules"""
    try:
        return GovernanceService.get_classification_rules(
            db=db,
            tenant_id=current_user.tenant_id,
            is_enabled=is_enabled
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get rules: {str(e)}")


@router.post("/classification/scan", response_model=List[ScanResult], tags=["Data Classification"])
def scan_for_pii(
    scan_request: ScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Scan datasource for PII (Personally Identifiable Information)
    
    **Requires:** Editor or Admin role
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        return GovernanceService.scan_for_pii(
            db=db,
            scan_request=scan_request,
            tenant_id=current_user.tenant_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to scan for PII: {str(e)}")


# ==================== Access Request Endpoints ====================

@router.post("/access-requests", response_model=AccessRequest, tags=["Access Requests"])
def create_access_request(
    request: AccessRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create an access request for data or resources
    
    **Access Levels:**
    - read: Read-only access
    - write: Read and modify access
    - admin: Full control
    """
    try:
        return GovernanceService.create_access_request(
            db=db,
            request_data=request,
            tenant_id=current_user.tenant_id,
            requester_id=current_user.id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create access request: {str(e)}")


@router.get("/access-requests", response_model=List[AccessRequest], tags=["Access Requests"])
def get_access_requests(
    status: Optional[ApprovalStatus] = None,
    requester_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get access requests
    
    **Filters:**
    - status: Filter by approval status (pending, approved, rejected, cancelled)
    - requester_id: Filter by requester (leave empty to see all)
    
    **Note:** Regular users see only their own requests. Admins see all requests.
    """
    # Non-admin users can only see their own requests
    if current_user.role != UserRole.ADMIN:
        requester_id = current_user.id
    
    try:
        return GovernanceService.get_access_requests(
            db=db,
            tenant_id=current_user.tenant_id,
            status=status,
            requester_id=requester_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get access requests: {str(e)}")


@router.get("/access-requests/pending", response_model=List[AccessRequest], tags=["Access Requests"])
def get_pending_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get pending access requests for approval
    
    **Requires:** Admin role
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        return GovernanceService.get_access_requests(
            db=db,
            tenant_id=current_user.tenant_id,
            status=ApprovalStatus.PENDING
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get pending requests: {str(e)}")


@router.post("/access-requests/{request_id}/approve", response_model=AccessRequest, tags=["Access Requests"])
def approve_access_request(
    request_id: str,
    approval_notes: Optional[str] = None,
    is_compliance_approval: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve an access request
    
    **Requires:** Admin role
    
    **Parameters:**
    - approval_notes: Optional notes for the approval
    - is_compliance_approval: Set to true for compliance officer approval
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify request belongs to tenant
    from app.models.governance import AccessRequest as AccessRequestModel
    request = db.query(AccessRequestModel).filter(
        AccessRequestModel.id == request_id,
        AccessRequestModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Access request not found")
    
    try:
        updated = GovernanceService.approve_access_request(
            db=db,
            request_id=request_id,
            approver_id=current_user.id,
            approval_notes=approval_notes,
            is_compliance_approval=is_compliance_approval
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Failed to approve request")
        
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to approve request: {str(e)}")


@router.post("/access-requests/{request_id}/reject", response_model=AccessRequest, tags=["Access Requests"])
def reject_access_request(
    request_id: str,
    rejection_notes: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject an access request
    
    **Requires:** Admin role
    
    **Parameters:**
    - rejection_notes: Required notes explaining the rejection
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Verify request belongs to tenant
    from app.models.governance import AccessRequest as AccessRequestModel
    request = db.query(AccessRequestModel).filter(
        AccessRequestModel.id == request_id,
        AccessRequestModel.tenant_id == current_user.tenant_id
    ).first()
    
    if not request:
        raise HTTPException(status_code=404, detail="Access request not found")
    
    try:
        updated = GovernanceService.reject_access_request(
            db=db,
            request_id=request_id,
            approver_id=current_user.id,
            rejection_notes=rejection_notes
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Failed to reject request")
        
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject request: {str(e)}")


@router.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint for governance service"""
    return {
        "status": "healthy",
        "service": "data-governance",
        "features": [
            "data-catalog",
            "data-lineage",
            "data-classification",
            "access-requests",
            "impact-analysis"
        ]
    }
