"""
Data Governance Models for NexBII Platform
Phase 4.4: Data Governance
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from app.core.database import Base


class ClassificationLevel(str, enum.Enum):
    """Data classification levels"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class PIIType(str, enum.Enum):
    """Types of Personally Identifiable Information"""
    SSN = "ssn"
    EMAIL = "email"
    PHONE = "phone"
    CREDIT_CARD = "credit_card"
    PASSPORT = "passport"
    DRIVER_LICENSE = "driver_license"
    ADDRESS = "address"
    DATE_OF_BIRTH = "date_of_birth"
    CUSTOM = "custom"


class ApprovalStatus(str, enum.Enum):
    """Status of access requests"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class DataCatalogEntry(Base):
    """
    Data Catalog Entry Model
    Stores metadata for tables and columns
    """
    __tablename__ = "data_catalog_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Resource identification
    datasource_id = Column(String(36), ForeignKey("datasources.id"), nullable=False)
    table_name = Column(String(255), nullable=False)
    column_name = Column(String(255), nullable=True)  # NULL for table-level metadata
    
    # Metadata
    display_name = Column(String(255))
    description = Column(Text)
    business_owner = Column(String(255))
    technical_owner = Column(String(255))
    tags = Column(JSON, default=list)  # List of tags
    
    # Classification
    classification_level = Column(SQLEnum(ClassificationLevel), default=ClassificationLevel.INTERNAL)
    is_pii = Column(Boolean, default=False)
    pii_types = Column(JSON, default=list)  # List of PII types if is_pii=True
    
    # Data quality metadata
    data_type = Column(String(100))
    is_nullable = Column(Boolean)
    default_value = Column(String(255))
    
    # Additional metadata
    usage_notes = Column(Text)
    related_dashboards = Column(JSON, default=list)  # List of dashboard IDs
    related_queries = Column(JSON, default=list)  # List of query IDs
    
    # Audit fields
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(36), ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="catalog_entries")
    datasource = relationship("DataSource")


class DataLineage(Base):
    """
    Data Lineage Model
    Tracks data flow and transformations
    """
    __tablename__ = "data_lineage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Source information
    source_type = Column(String(50), nullable=False)  # datasource, query, dashboard
    source_id = Column(String(36), nullable=False)
    source_table = Column(String(255))
    source_column = Column(String(255))
    
    # Target information
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(36), nullable=False)
    target_table = Column(String(255))
    target_column = Column(String(255))
    
    # Transformation details
    transformation_type = Column(String(100))  # select, join, aggregate, filter, etc.
    transformation_logic = Column(Text)  # SQL or description
    
    # Metadata
    confidence_score = Column(Integer, default=100)  # 0-100, how confident we are
    is_active = Column(Boolean, default=True)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="lineage_entries")


class DataClassificationRule(Base):
    """
    Data Classification Rule Model
    Rules for automated PII detection and classification
    """
    __tablename__ = "data_classification_rules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Rule identification
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Rule logic
    pii_type = Column(SQLEnum(PIIType), nullable=False)
    pattern = Column(String(500))  # Regex pattern for detection
    column_name_pattern = Column(String(255))  # Pattern to match column names
    
    # Classification
    classification_level = Column(SQLEnum(ClassificationLevel), nullable=False)
    
    # Rule settings
    is_enabled = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher priority rules run first
    
    # Audit fields
    created_by = Column(String(36), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(String(36), ForeignKey("users.id"))
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="classification_rules")


class AccessRequest(Base):
    """
    Access Request Model
    Approval workflow for data access
    """
    __tablename__ = "access_requests"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Requester information
    requester_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    requester_justification = Column(Text, nullable=False)
    
    # Resource information
    resource_type = Column(String(50), nullable=False)  # datasource, table, dashboard
    resource_id = Column(String(36), nullable=False)
    resource_name = Column(String(255))
    
    # Access details
    access_level = Column(String(50))  # read, write, admin
    duration_days = Column(Integer)  # NULL for permanent access
    
    # Approval workflow
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    approver_id = Column(String(36), ForeignKey("users.id"))
    approval_notes = Column(Text)
    approved_at = Column(DateTime)
    
    # Metadata
    classification_level = Column(SQLEnum(ClassificationLevel))
    requires_compliance_approval = Column(Boolean, default=False)
    compliance_approver_id = Column(String(36), ForeignKey("users.id"))
    compliance_approved_at = Column(DateTime)
    compliance_notes = Column(Text)
    
    # Audit fields
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)  # When the approved access expires
    
    # Relationships
    tenant = relationship("Tenant", back_populates="access_requests")
    requester = relationship("User", foreign_keys=[requester_id])
    approver = relationship("User", foreign_keys=[approver_id])
    compliance_approver = relationship("User", foreign_keys=[compliance_approver_id])


class DataImpactAnalysis(Base):
    """
    Data Impact Analysis Model
    Stores impact analysis results for changes
    """
    __tablename__ = "data_impact_analysis"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id"), nullable=False, index=True)
    
    # Change information
    change_type = Column(String(50), nullable=False)  # schema_change, data_deletion, etc.
    affected_resource_type = Column(String(50), nullable=False)
    affected_resource_id = Column(String(36), nullable=False)
    affected_resource_name = Column(String(255))
    
    # Impact details
    impact_level = Column(String(20))  # low, medium, high, critical
    impact_summary = Column(Text)
    affected_queries = Column(JSON, default=list)
    affected_dashboards = Column(JSON, default=list)
    affected_users = Column(JSON, default=list)
    
    # Recommendations
    recommendations = Column(JSON, default=list)
    mitigation_steps = Column(JSON, default=list)
    
    # Analysis metadata
    analysis_date = Column(DateTime, default=datetime.utcnow)
    analyzed_by = Column(String(36), ForeignKey("users.id"))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="impact_analyses")
