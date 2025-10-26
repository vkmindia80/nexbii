"""
MFA API Endpoints
Handles Multi-Factor Authentication enrollment and verification
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user, verify_password
from app.models.user import User
from app.schemas.security import (
    MFAEnrollmentResponse,
    MFAVerifyEnrollmentRequest,
    MFAVerifyRequest,
    MFADisableRequest,
    MFAStatusResponse
)
from app.services.mfa_service import MFAService
from app.services.audit_service import AuditService

router = APIRouter()


@router.post("/enroll", response_model=MFAEnrollmentResponse)
def enroll_mfa(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start MFA enrollment"""
    mfa_service = MFAService(db)
    
    enrollment_data = mfa_service.enroll_user(current_user)
    
    return MFAEnrollmentResponse(**enrollment_data)


@router.post("/verify-enrollment")
def verify_mfa_enrollment(
    request: MFAVerifyEnrollmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete MFA enrollment by verifying TOTP code"""
    mfa_service = MFAService(db)
    
    success = mfa_service.verify_enrollment(current_user, request.code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Log enrollment
    audit_service = AuditService(db)
    audit_service.log_mfa_enrollment(
        user=current_user,
        success=True
    )
    
    return {"message": "MFA enrollment completed successfully"}


@router.post("/verify")
def verify_mfa_code(
    request: MFAVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify MFA code during login"""
    mfa_service = MFAService(db)
    
    success = mfa_service.verify_code(current_user, request.code)
    
    # Log verification attempt
    audit_service = AuditService(db)
    audit_service.log_mfa_verification(
        user=current_user,
        success=success
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code"
        )
    
    return {"message": "MFA verification successful"}


@router.get("/backup-codes")
def get_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get MFA backup codes"""
    mfa_service = MFAService(db)
    status_data = mfa_service.get_status(current_user)
    
    if not status_data["is_enabled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    # In production, don't return backup codes directly
    # User should re-authenticate first
    return {"message": "Backup codes are securely stored"}


@router.post("/backup-codes/regenerate")
def regenerate_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate MFA backup codes"""
    mfa_service = MFAService(db)
    
    backup_codes = mfa_service.regenerate_backup_codes(current_user)
    
    if not backup_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    return {
        "backup_codes": backup_codes,
        "message": "Backup codes regenerated. Save them securely."
    }


@router.post("/disable")
def disable_mfa(
    request: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable MFA (requires password confirmation)"""
    # Verify password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    mfa_service = MFAService(db)
    success = mfa_service.disable_mfa(current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled"
        )
    
    return {"message": "MFA disabled successfully"}


@router.get("/status", response_model=MFAStatusResponse)
def get_mfa_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get MFA status for current user"""
    mfa_service = MFAService(db)
    status_data = mfa_service.get_status(current_user)
    
    return MFAStatusResponse(**status_data)
