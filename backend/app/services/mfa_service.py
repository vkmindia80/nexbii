"""
Multi-Factor Authentication (MFA) Service
Implements TOTP-based MFA with QR codes and backup codes
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from app.models.security import MFAConfig
from app.models.user import User
import pyotp
import qrcode
import io
import base64
import secrets
import uuid
from datetime import datetime


class MFAService:
    """Service for Multi-Factor Authentication"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def enroll_user(self, user: User) -> Dict[str, Any]:
        """
        Start MFA enrollment for user
        
        Returns:
            {
                "secret_key": str,
                "qr_code_url": str,  # Data URL for QR code image
                "backup_codes": List[str]
            }
        """
        # Check if user already has MFA
        existing_mfa = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id
        ).first()
        
        if existing_mfa:
            # Delete old config to re-enroll
            self.db.delete(existing_mfa)
            self.db.commit()
        
        # Generate secret key
        secret_key = pyotp.random_base32()
        
        # Generate backup codes
        backup_codes = [self._generate_backup_code() for _ in range(10)]
        
        # Create MFA config (not enabled yet)
        mfa_config = MFAConfig(
            id=str(uuid.uuid4()),
            user_id=user.id,
            secret_key=secret_key,  # In production, encrypt this
            backup_codes=backup_codes,  # In production, hash these
            is_enabled=False,
            enrollment_completed=False
        )
        
        self.db.add(mfa_config)
        self.db.commit()
        self.db.refresh(mfa_config)
        
        # Generate QR code
        qr_code_url = self._generate_qr_code(user, secret_key)
        
        return {
            "secret_key": secret_key,
            "qr_code_url": qr_code_url,
            "backup_codes": backup_codes
        }
    
    def verify_enrollment(self, user: User, code: str) -> bool:
        """
        Verify MFA enrollment with a TOTP code
        
        This completes the enrollment process
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id
        ).first()
        
        if not mfa_config:
            return False
        
        # Verify code
        totp = pyotp.TOTP(mfa_config.secret_key)
        
        if totp.verify(code, valid_window=1):
            # Enable MFA
            mfa_config.is_enabled = True
            mfa_config.enrollment_completed = True
            mfa_config.enrolled_at = datetime.utcnow()
            self.db.commit()
            return True
        
        return False
    
    def verify_code(self, user: User, code: str) -> bool:
        """
        Verify MFA code during login
        
        Args:
            user: User attempting to login
            code: TOTP code or backup code
            
        Returns:
            True if code is valid
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id,
            MFAConfig.is_enabled == True
        ).first()
        
        if not mfa_config:
            return False
        
        # Try TOTP code first
        totp = pyotp.TOTP(mfa_config.secret_key)
        if totp.verify(code, valid_window=1):
            mfa_config.last_used_at = datetime.utcnow()
            mfa_config.failed_attempts = 0
            self.db.commit()
            return True
        
        # Try backup codes
        if code in mfa_config.backup_codes:
            # Remove used backup code
            mfa_config.backup_codes.remove(code)
            mfa_config.last_used_at = datetime.utcnow()
            mfa_config.failed_attempts = 0
            self.db.commit()
            return True
        
        # Increment failed attempts
        mfa_config.failed_attempts += 1
        self.db.commit()
        
        # Lock after 5 failed attempts
        if mfa_config.failed_attempts >= 5:
            mfa_config.is_enabled = False
            self.db.commit()
        
        return False
    
    def disable_mfa(self, user: User) -> bool:
        """
        Disable MFA for user
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id
        ).first()
        
        if mfa_config:
            self.db.delete(mfa_config)
            self.db.commit()
            return True
        
        return False
    
    def get_status(self, user: User) -> Dict[str, Any]:
        """
        Get MFA status for user
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id
        ).first()
        
        if not mfa_config:
            return {
                "is_enabled": False,
                "enrollment_completed": False,
                "enrolled_at": None,
                "last_used_at": None
            }
        
        return {
            "is_enabled": mfa_config.is_enabled,
            "enrollment_completed": mfa_config.enrollment_completed,
            "enrolled_at": mfa_config.enrolled_at,
            "last_used_at": mfa_config.last_used_at
        }
    
    def regenerate_backup_codes(self, user: User) -> List[str]:
        """
        Regenerate backup codes for user
        """
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id,
            MFAConfig.is_enabled == True
        ).first()
        
        if not mfa_config:
            return []
        
        # Generate new backup codes
        backup_codes = [self._generate_backup_code() for _ in range(10)]
        mfa_config.backup_codes = backup_codes
        self.db.commit()
        
        return backup_codes
    
    def _generate_backup_code(self) -> str:
        """Generate a random backup code"""
        return secrets.token_hex(8).upper()
    
    def _generate_qr_code(self, user: User, secret_key: str) -> str:
        """
        Generate QR code data URL for authenticator apps
        
        Returns:
            Data URL string (data:image/png;base64,...)
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret_key)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name="NexBII"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to data URL
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    def is_mfa_required(self, user: User) -> bool:
        """
        Check if MFA is required for user
        
        This can be based on role, tenant policy, etc.
        """
        # For now, just check if user has MFA enabled
        mfa_config = self.db.query(MFAConfig).filter(
            MFAConfig.user_id == user.id,
            MFAConfig.is_enabled == True
        ).first()
        
        return mfa_config is not None
