"""
Pydantic Schemas for Data Governance
Phase 4.4: Data Governance
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ClassificationLevel(str, Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PIIType(str, Enum):
    """Types of PII"""
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    CUSTOM = "custom"


class ApprovalStatus(str, Enum):
    """Status of access requests"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


# Data Catalog Schemas
class DataCatalogEntryBase(BaseModel):
    datasource_id: str
    table_name: str
    column_name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    classification_level: ClassificationLevel = ClassificationLevel.INTERNAL
    is_pii: bool = False
    pii_types: List[PIIType] = Field(default_factory=list)
    data_type: Optional[str] = None
    is_nullable: Optional[bool] = None
    default_value: Optional[str] = None
    usage_notes: Optional[str] = None
    related_dashboards: List[str] = Field(default_factory=list)
    related_queries: List[str] = Field(default_factory=list)


class DataCatalogEntryCreate(DataCatalogEntryBase):
    pass


class DataCatalogEntryUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    business_owner: Optional[str] = None
    technical_owner: Optional[str] = None
    tags: Optional[List[str]] = None
    classification_level: Optional[ClassificationLevel] = None
    is_pii: Optional[bool] = None
    pii_types: Optional[List[PIIType]] = None
    usage_notes: Optional[str] = None
    related_dashboards: Optional[List[str]] = None
    related_queries: Optional[List[str]] = None


class DataCatalogEntry(DataCatalogEntryBase):
    id: str
    tenant_id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


# Data Lineage Schemas
class DataLineageBase(BaseModel):
    source_type: str  # datasource, query, dashboard
    source_id: str
    source_table: Optional[str] = None
    source_column: Optional[str] = None
    target_type: str
    target_id: str
    target_table: Optional[str] = None
    target_column: Optional[str] = None
    transformation_type: Optional[str] = None
    transformation_logic: Optional[str] = None
    confidence_score: int = 100
    is_active: bool = True


class DataLineageCreate(DataLineageBase):
    pass


class DataLineage(DataLineageBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LineageGraph(BaseModel):
    """Graph representation of data lineage"""
    nodes: List[dict]
    edges: List[dict]


# Data Classification Schemas
class DataClassificationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    pii_type: PIIType
    pattern: Optional[str] = None
    column_name_pattern: Optional[str] = None
    classification_level: ClassificationLevel
    is_enabled: bool = True
    priority: int = 0


class DataClassificationRuleCreate(DataClassificationRuleBase):
    pass


class DataClassificationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    pattern: Optional[str] = None
    column_name_pattern: Optional[str] = None
    classification_level: Optional[ClassificationLevel] = None
    is_enabled: Optional[bool] = None
    priority: Optional[int] = None


class DataClassificationRule(DataClassificationRuleBase):
    id: str
    tenant_id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: datetime

    class Config:
        from_attributes = True


class ScanRequest(BaseModel):
    """Request to scan datasource for PII"""
    datasource_id: str
    table_name: Optional[str] = None  # Scan specific table or all


class ScanResult(BaseModel):
    """Result of PII scanning"""
    datasource_id: str
    table_name: str
    column_name: str
    pii_type: PIIType
    matches_found: int
    confidence_score: int
    sample_values: List[str] = Field(default_factory=list)


# Access Request Schemas
class AccessRequestBase(BaseModel):
    requester_justification: str
    resource_type: str  # datasource, table, dashboard
    resource_id: str
    resource_name: Optional[str] = None
    access_level: str = "read"
    duration_days: Optional[int] = None


class AccessRequestCreate(AccessRequestBase):
    pass


class AccessRequestUpdate(BaseModel):
    status: Optional[ApprovalStatus] = None
    approval_notes: Optional[str] = None
    compliance_notes: Optional[str] = None


class AccessRequest(AccessRequestBase):
    id: str
    tenant_id: str
    requester_id: str
    status: ApprovalStatus
    approver_id: Optional[str] = None
    approval_notes: Optional[str] = None
    approved_at: Optional[datetime] = None
    classification_level: Optional[ClassificationLevel] = None
    requires_compliance_approval: bool = False
    compliance_approver_id: Optional[str] = None
    compliance_approved_at: Optional[datetime] = None
    compliance_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Impact Analysis Schemas
class ImpactAnalysisRequest(BaseModel):
    """Request for impact analysis"""
    change_type: str
    affected_resource_type: str
    affected_resource_id: str
    affected_resource_name: Optional[str] = None


class ImpactAnalysisResult(BaseModel):
    """Result of impact analysis"""
    id: str
    tenant_id: str
    change_type: str
    affected_resource_type: str
    affected_resource_id: str
    affected_resource_name: Optional[str] = None
    impact_level: str
    impact_summary: str
    affected_queries: List[str]
    affected_dashboards: List[str]
    affected_users: List[str]
    recommendations: List[str]
    mitigation_steps: List[str]
    analysis_date: datetime
    analyzed_by: Optional[str] = None

    class Config:
        from_attributes = True


# Search and Filter Schemas
class CatalogSearchParams(BaseModel):
    """Parameters for searching data catalog"""
    query: Optional[str] = None
    datasource_id: Optional[str] = None
    classification_level: Optional[ClassificationLevel] = None
    is_pii: Optional[bool] = None
    tags: Optional[List[str]] = None
    limit: int = 50
    offset: int = 0


class CatalogStatistics(BaseModel):
    """Statistics for data catalog"""
    total_entries: int
    total_tables: int
    total_columns: int
    by_classification: dict
    pii_count: int
    datasources_cataloged: int
