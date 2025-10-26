"""
Compliance API Endpoints
Handles GDPR and HIPAA compliance features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.security import (
    ConsentRecordCreate,
    ConsentRecordResponse,
    GDPRDataExportResponse,
    GDPRDeleteRequest,
    DataClassificationCreate,
    DataClassificationResponse
)
from app.services.gdpr_service import GDPRService
from app.services.hipaa_service import HIPAAService
from app.services.audit_service import AuditService
import uuid
from datetime import datetime, timedelta

router = APIRouter()


# ===== GDPR Endpoints =====

@router.get("/gdpr/export", response_model=GDPRDataExportResponse)
def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data (GDPR)"""
    gdpr_service = GDPRService(db)
    
    # Export data
    data = gdpr_service.export_user_data(current_user)
    
    # Log the export
    audit_service = AuditService(db)
    audit_service.log_gdpr_export(current_user)
    
    # In production, create a downloadable file and return URL
    export_id = str(uuid.uuid4())
    
    return GDPRDataExportResponse(
        export_id=export_id,
        download_url=f"/api/compliance/gdpr/download/{export_id}",
        expires_at=datetime.utcnow() + timedelta(days=7)
    )


@router.post("/gdpr/delete")
def delete_user_data(
    request: GDPRDeleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete all user data (Right to be Forgotten)"""
    gdpr_service = GDPRService(db)
    
    # Log the deletion before deleting
    audit_service = AuditService(db)
    audit_service.log_gdpr_deletion(current_user)
    
    # Delete all user data
    summary = gdpr_service.delete_user_data(current_user)
    
    return summary


@router.get("/consents", response_model=List[ConsentRecordResponse])
def list_consents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all consent records"""
    gdpr_service = GDPRService(db)
    consents = gdpr_service.get_consents(current_user)
    
    return consents


@router.post("/consents", response_model=ConsentRecordResponse, status_code=status.HTTP_201_CREATED)
def record_consent(
    consent_data: ConsentRecordCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Record user consent"""
    gdpr_service = GDPRService(db)
    
    # Get IP and user agent from request
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    consent = gdpr_service.record_consent(
        user=current_user,
        consent_type=consent_data.consent_type,
        version=consent_data.version,
        is_granted=consent_data.is_granted,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return consent


@router.put("/consents/{consent_type}")
def revoke_consent(
    consent_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific consent"""
    gdpr_service = GDPRService(db)
    
    consent = gdpr_service.revoke_consent(current_user, consent_type)
    
    if not consent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found or already revoked"
        )
    
    return {"message": f"Consent for {consent_type} revoked"}


# ===== HIPAA Endpoints =====

@router.get("/hipaa/classifications", response_model=List[DataClassificationResponse])
def list_phi_classifications(
    datasource_id: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List PHI classifications"""
    hipaa_service = HIPAAService(db)
    
    if datasource_id:
        classifications = hipaa_service.get_phi_columns(datasource_id, current_user.tenant_id)
    else:
        from app.models.security import DataClassification, DataClassificationType
        classifications = db.query(DataClassification).filter(
            DataClassification.tenant_id == current_user.tenant_id,
            DataClassification.classification == DataClassificationType.PHI
        ).all()
    
    return classifications


@router.post("/hipaa/classify", response_model=DataClassificationResponse, status_code=status.HTTP_201_CREATED)
def classify_as_phi(
    classification_data: DataClassificationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Classify a column as PHI"""
    hipaa_service = HIPAAService(db)
    
    classification = hipaa_service.classify_column_as_phi(
        datasource_id=classification_data.datasource_id,
        table_name=classification_data.table_name,
        column_name=classification_data.column_name,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        description=classification_data.description,
        masking_rule_id=classification_data.masking_rule_id
    )
    
    return classification


@router.post("/hipaa/auto-detect")
def auto_detect_phi(
    datasource_id: str,
    schema: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Auto-detect PHI columns in a datasource"""
    hipaa_service = HIPAAService(db)
    
    classifications = hipaa_service.auto_detect_phi(
        datasource_id=datasource_id,
        schema=schema,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id
    )
    
    return {
        "detected": len(classifications),
        "classifications": classifications
    }


# ===== Compliance Reports =====

@router.get("/reports/soc2")
def generate_soc2_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate SOC 2 compliance report"""
    # Mock SOC 2 report
    return {
        "report_type": "soc2",
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "security_policies": 5,
            "audit_logs_enabled": True,
            "mfa_enabled": True,
            "encryption_enabled": True
        }
    }


@router.get("/reports/gdpr")
def generate_gdpr_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate GDPR compliance report"""
    gdpr_service = GDPRService(db)
    
    consents = gdpr_service.get_consents(current_user)
    
    return {
        "report_type": "gdpr",
        "generated_at": datetime.utcnow().isoformat(),
        "summary": {
            "data_export_available": True,
            "right_to_be_forgotten": True,
            "consent_records": len(consents)
        }
    }


@router.get("/reports/hipaa")
def generate_hipaa_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate HIPAA compliance report"""
    hipaa_service = HIPAAService(db)
    
    report = hipaa_service.generate_hipaa_compliance_report(current_user.tenant_id)
    
    return report
