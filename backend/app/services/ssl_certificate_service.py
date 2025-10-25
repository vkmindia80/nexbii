"""
SSL/TLS Certificate Management Service
Supports both Let's Encrypt automatic certificates and manual certificate upload.
"""

import os
import logging
import subprocess
import tempfile
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import OpenSSL

logger = logging.getLogger(__name__)


class SSLCertificateService:
    """Service for SSL/TLS certificate management"""
    
    CERT_DIR = "/app/backend/ssl_certificates"
    
    def __init__(self):
        # Create certificate directory if it doesn't exist
        os.makedirs(self.CERT_DIR, exist_ok=True)
    
    # ========== Manual Certificate Upload ==========
    
    @staticmethod
    def validate_certificate(cert_pem: str, private_key_pem: str, domain: str) -> Dict[str, any]:
        """
        Validate SSL certificate and private key.
        
        Args:
            cert_pem: PEM-formatted certificate
            private_key_pem: PEM-formatted private key
            domain: Domain name to verify
        
        Returns:
            dict: Validation result with certificate info
        """
        try:
            # Load certificate
            cert = x509.load_pem_x509_certificate(cert_pem.encode(), default_backend())
            
            # Load private key
            try:
                private_key = serialization.load_pem_private_key(
                    private_key_pem.encode(),
                    password=None,
                    backend=default_backend()
                )
            except Exception as e:
                return {
                    "valid": False,
                    "error": f"Invalid private key: {str(e)}"
                }
            
            # Extract certificate info
            subject = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            issuer = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            
            # Check if certificate matches domain
            if subject != domain and not SSLCertificateService._check_san(cert, domain):
                return {
                    "valid": False,
                    "error": f"Certificate subject '{subject}' does not match domain '{domain}'"
                }
            
            # Check if certificate is expired
            now = datetime.utcnow()
            if now < not_before:
                return {
                    "valid": False,
                    "error": f"Certificate is not yet valid (valid from {not_before})"
                }
            
            if now > not_after:
                return {
                    "valid": False,
                    "error": f"Certificate has expired (expired on {not_after})"
                }
            
            # Verify private key matches certificate
            if not SSLCertificateService._verify_key_pair(cert_pem, private_key_pem):
                return {
                    "valid": False,
                    "error": "Private key does not match certificate"
                }
            
            return {
                "valid": True,
                "subject": subject,
                "issuer": issuer,
                "not_before": not_before.isoformat(),
                "not_after": not_after.isoformat(),
                "days_until_expiry": (not_after - now).days,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Certificate validation error: {str(e)}")
            return {
                "valid": False,
                "error": f"Certificate validation failed: {str(e)}"
            }
    
    @staticmethod
    def _check_san(cert: x509.Certificate, domain: str) -> bool:
        """Check if domain is in Subject Alternative Names"""
        try:
            san_extension = cert.extensions.get_extension_for_oid(
                x509.oid.ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            )
            san_names = san_extension.value.get_values_for_type(x509.DNSName)
            return domain in san_names
        except x509.ExtensionNotFound:
            return False
    
    @staticmethod
    def _verify_key_pair(cert_pem: str, private_key_pem: str) -> bool:
        """Verify that private key matches certificate"""
        try:
            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert_pem)
            key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, private_key_pem)
            
            context = OpenSSL.SSL.Context(OpenSSL.SSL.TLSv1_2_METHOD)
            context.use_privatekey(key)
            context.use_certificate(cert)
            context.check_privatekey()
            
            return True
        except Exception as e:
            logger.error(f"Key pair verification failed: {str(e)}")
            return False
    
    def store_certificate(
        self, 
        tenant_id: str, 
        domain: str, 
        cert_pem: str, 
        private_key_pem: str,
        chain_pem: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Store SSL certificate files for a domain.
        
        Args:
            tenant_id: Tenant ID
            domain: Domain name
            cert_pem: Certificate in PEM format
            private_key_pem: Private key in PEM format
            chain_pem: Certificate chain (optional)
        
        Returns:
            dict: File paths
        """
        try:
            domain_dir = os.path.join(self.CERT_DIR, tenant_id, domain)
            os.makedirs(domain_dir, exist_ok=True)
            
            cert_path = os.path.join(domain_dir, "certificate.pem")
            key_path = os.path.join(domain_dir, "private_key.pem")
            chain_path = os.path.join(domain_dir, "chain.pem") if chain_pem else None
            
            # Write certificate
            with open(cert_path, 'w') as f:
                f.write(cert_pem)
            
            # Write private key (with restricted permissions)
            with open(key_path, 'w') as f:
                f.write(private_key_pem)
            os.chmod(key_path, 0o600)
            
            # Write chain if provided
            if chain_pem:
                with open(chain_path, 'w') as f:
                    f.write(chain_pem)
            
            logger.info(f"✅ Stored SSL certificate for {domain}")
            
            return {
                "certificate_path": cert_path,
                "private_key_path": key_path,
                "chain_path": chain_path
            }
            
        except Exception as e:
            logger.error(f"Failed to store certificate: {str(e)}")
            raise
    
    # ========== Let's Encrypt Integration ==========
    
    @staticmethod
    def request_letsencrypt_certificate(
        domain: str, 
        email: str,
        staging: bool = False
    ) -> Dict[str, any]:
        """
        Request SSL certificate from Let's Encrypt using certbot.
        
        Note: This requires certbot to be installed and the domain to be 
        accessible from the internet on port 80 (HTTP-01 challenge).
        
        Args:
            domain: Domain to get certificate for
            email: Contact email for Let's Encrypt
            staging: Use Let's Encrypt staging server (for testing)
        
        Returns:
            dict: Certificate paths and status
        """
        try:
            # Check if certbot is installed
            certbot_check = subprocess.run(
                ["which", "certbot"],
                capture_output=True,
                text=True
            )
            
            if certbot_check.returncode != 0:
                return {
                    "success": False,
                    "error": "certbot is not installed. Please install certbot first.",
                    "install_command": "sudo apt-get install -y certbot"
                }
            
            # Build certbot command
            cmd = [
                "certbot", "certonly",
                "--standalone",
                "--non-interactive",
                "--agree-tos",
                "--email", email,
                "-d", domain
            ]
            
            if staging:
                cmd.append("--staging")
            
            # Run certbot
            logger.info(f"Running certbot for {domain}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Certificate paths (Let's Encrypt standard locations)
                cert_path = f"/etc/letsencrypt/live/{domain}/fullchain.pem"
                key_path = f"/etc/letsencrypt/live/{domain}/privkey.pem"
                
                return {
                    "success": True,
                    "certificate_path": cert_path,
                    "private_key_path": key_path,
                    "message": f"SSL certificate obtained successfully for {domain}",
                    "error": None
                }
            else:
                logger.error(f"certbot failed: {result.stderr}")
                return {
                    "success": False,
                    "error": f"certbot failed: {result.stderr}",
                    "message": None
                }
            
        except Exception as e:
            logger.error(f"Let's Encrypt certificate request failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": None
            }
    
    @staticmethod
    def renew_letsencrypt_certificate(domain: str) -> Dict[str, any]:
        """
        Renew Let's Encrypt certificate.
        
        Args:
            domain: Domain to renew certificate for
        
        Returns:
            dict: Renewal status
        """
        try:
            cmd = ["certbot", "renew", "--cert-name", domain]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "message": f"Certificate renewed successfully for {domain}",
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": f"Renewal failed: {result.stderr}"
                }
        
        except Exception as e:
            logger.error(f"Certificate renewal failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    def get_certificate_info(cert_path: str) -> Optional[Dict[str, any]]:
        """
        Get information about an existing certificate.
        
        Args:
            cert_path: Path to certificate file
        
        Returns:
            dict: Certificate information or None if error
        """
        try:
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            cert = x509.load_pem_x509_certificate(cert_data, default_backend())
            
            subject = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            issuer = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            not_before = cert.not_valid_before
            not_after = cert.not_valid_after
            
            now = datetime.utcnow()
            days_until_expiry = (not_after - now).days
            
            return {
                "subject": subject,
                "issuer": issuer,
                "not_before": not_before.isoformat(),
                "not_after": not_after.isoformat(),
                "days_until_expiry": days_until_expiry,
                "is_expired": now > not_after,
                "needs_renewal": days_until_expiry < 30
            }
        
        except Exception as e:
            logger.error(f"Failed to read certificate info: {str(e)}")
            return None
    
    # ========== Self-Signed Certificate (for testing) ==========
    
    @staticmethod
    def generate_self_signed_certificate(domain: str, days_valid: int = 365) -> Tuple[str, str]:
        """
        Generate self-signed certificate for testing.
        
        Args:
            domain: Domain name
            days_valid: Number of days certificate is valid
        
        Returns:
            tuple: (certificate_pem, private_key_pem)
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"NexBII"),
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=days_valid)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(domain)]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Convert to PEM format
        cert_pem = cert.public_bytes(serialization.Encoding.PEM).decode()
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        
        return cert_pem, key_pem
