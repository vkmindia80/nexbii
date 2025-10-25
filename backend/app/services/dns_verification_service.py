"""
DNS Verification Service
Handles DNS verification for custom domains using CNAME, TXT, and HTTP methods.
"""

import dns.resolver
import requests
import logging
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class DNSVerificationService:
    """Service for verifying custom domain ownership"""
    
    @staticmethod
    def verify_cname_record(domain: str, expected_value: str) -> Dict[str, any]:
        """
        Verify CNAME record for domain verification.
        Expected CNAME: <verification_token>.nexbii.com
        
        Args:
            domain: The domain to verify (e.g., analytics.company.com)
            expected_value: Expected CNAME value (e.g., verify-abc123.nexbii.com)
        
        Returns:
            dict: {"verified": bool, "actual_value": str, "error": str}
        """
        try:
            # Query CNAME records
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            answers = resolver.resolve(domain, 'CNAME')
            
            for rdata in answers:
                cname_value = str(rdata.target).rstrip('.')
                logger.info(f"Found CNAME record for {domain}: {cname_value}")
                
                if cname_value == expected_value:
                    return {
                        "verified": True,
                        "actual_value": cname_value,
                        "error": None,
                        "verified_at": datetime.utcnow().isoformat()
                    }
            
            return {
                "verified": False,
                "actual_value": str(answers[0].target).rstrip('.') if answers else None,
                "error": f"CNAME does not match. Expected: {expected_value}"
            }
            
        except dns.resolver.NXDOMAIN:
            return {
                "verified": False,
                "actual_value": None,
                "error": f"Domain {domain} does not exist"
            }
        except dns.resolver.NoAnswer:
            return {
                "verified": False,
                "actual_value": None,
                "error": f"No CNAME record found for {domain}"
            }
        except Exception as e:
            logger.error(f"DNS verification error: {str(e)}")
            return {
                "verified": False,
                "actual_value": None,
                "error": f"DNS lookup failed: {str(e)}"
            }
    
    @staticmethod
    def verify_txt_record(domain: str, expected_token: str) -> Dict[str, any]:
        """
        Verify TXT record for domain verification.
        Expected TXT: nexbii-verification=<token>
        
        Args:
            domain: The domain to verify
            expected_token: Expected verification token
        
        Returns:
            dict: {"verified": bool, "actual_value": str, "error": str}
        """
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            answers = resolver.resolve(domain, 'TXT')
            
            for rdata in answers:
                txt_value = str(rdata).strip('"')
                logger.info(f"Found TXT record for {domain}: {txt_value}")
                
                # Check for nexbii-verification=<token>
                if txt_value.startswith('nexbii-verification='):
                    token = txt_value.split('=', 1)[1]
                    if token == expected_token:
                        return {
                            "verified": True,
                            "actual_value": txt_value,
                            "error": None,
                            "verified_at": datetime.utcnow().isoformat()
                        }
            
            return {
                "verified": False,
                "actual_value": None,
                "error": f"TXT record not found or does not match. Expected: nexbii-verification={expected_token}"
            }
            
        except dns.resolver.NXDOMAIN:
            return {
                "verified": False,
                "actual_value": None,
                "error": f"Domain {domain} does not exist"
            }
        except dns.resolver.NoAnswer:
            return {
                "verified": False,
                "actual_value": None,
                "error": f"No TXT record found for {domain}"
            }
        except Exception as e:
            logger.error(f"TXT verification error: {str(e)}")
            return {
                "verified": False,
                "actual_value": None,
                "error": f"DNS lookup failed: {str(e)}"
            }
    
    @staticmethod
    def verify_http_file(domain: str, expected_token: str) -> Dict[str, any]:
        """
        Verify domain ownership via HTTP file.
        Expected file: http://<domain>/.well-known/nexbii-verification.txt
        Content should be: <token>
        
        Args:
            domain: The domain to verify
            expected_token: Expected verification token in the file
        
        Returns:
            dict: {"verified": bool, "actual_value": str, "error": str}
        """
        try:
            verification_url = f"http://{domain}/.well-known/nexbii-verification.txt"
            
            response = requests.get(verification_url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            content = response.text.strip()
            logger.info(f"HTTP verification file content: {content}")
            
            if content == expected_token:
                return {
                    "verified": True,
                    "actual_value": content,
                    "error": None,
                    "verified_at": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "verified": False,
                    "actual_value": content,
                    "error": f"Token mismatch. Expected: {expected_token}"
                }
            
        except requests.RequestException as e:
            logger.error(f"HTTP verification error: {str(e)}")
            return {
                "verified": False,
                "actual_value": None,
                "error": f"HTTP verification failed: {str(e)}"
            }
    
    @staticmethod
    def verify_domain(domain: str, verification_method: str, verification_token: str) -> Dict[str, any]:
        """
        Verify domain using specified method.
        
        Args:
            domain: The domain to verify
            verification_method: "cname", "txt", or "http"
            verification_token: Verification token
        
        Returns:
            dict: Verification result
        """
        if verification_method == "cname":
            expected_value = f"verify-{verification_token}.nexbii.com"
            return DNSVerificationService.verify_cname_record(domain, expected_value)
        
        elif verification_method == "txt":
            return DNSVerificationService.verify_txt_record(domain, verification_token)
        
        elif verification_method == "http":
            return DNSVerificationService.verify_http_file(domain, verification_token)
        
        else:
            return {
                "verified": False,
                "actual_value": None,
                "error": f"Invalid verification method: {verification_method}"
            }
    
    @staticmethod
    def get_verification_instructions(domain: str, verification_method: str, verification_token: str) -> Dict[str, str]:
        """
        Get user-friendly instructions for domain verification.
        
        Returns:
            dict: Instructions for the specified method
        """
        if verification_method == "cname":
            return {
                "method": "CNAME Record",
                "title": "Add CNAME Record to Your DNS",
                "instructions": f"""
                1. Log in to your domain registrar (GoDaddy, Namecheap, etc.)
                2. Navigate to DNS Management for {domain}
                3. Add a new CNAME record:
                   - Host/Name: {domain}
                   - Points to: verify-{verification_token}.nexbii.com
                   - TTL: 3600 (or default)
                4. Save the record
                5. Wait 5-10 minutes for DNS propagation
                6. Click "Verify Domain" below
                """,
                "record_type": "CNAME",
                "host": domain,
                "value": f"verify-{verification_token}.nexbii.com"
            }
        
        elif verification_method == "txt":
            return {
                "method": "TXT Record",
                "title": "Add TXT Record to Your DNS",
                "instructions": f"""
                1. Log in to your domain registrar (GoDaddy, Namecheap, etc.)
                2. Navigate to DNS Management for {domain}
                3. Add a new TXT record:
                   - Host/Name: {domain} (or @)
                   - Value: nexbii-verification={verification_token}
                   - TTL: 3600 (or default)
                4. Save the record
                5. Wait 5-10 minutes for DNS propagation
                6. Click "Verify Domain" below
                """,
                "record_type": "TXT",
                "host": domain,
                "value": f"nexbii-verification={verification_token}"
            }
        
        elif verification_method == "http":
            return {
                "method": "HTTP File",
                "title": "Upload Verification File to Your Website",
                "instructions": f"""
                1. Create a file named: nexbii-verification.txt
                2. Add this content to the file: {verification_token}
                3. Upload the file to: http://{domain}/.well-known/nexbii-verification.txt
                4. Make sure the file is publicly accessible
                5. Click "Verify Domain" below
                """,
                "file_name": "nexbii-verification.txt",
                "file_content": verification_token,
                "file_location": f"http://{domain}/.well-known/nexbii-verification.txt"
            }
        
        return {
            "method": "Unknown",
            "title": "Invalid Verification Method",
            "instructions": "Please select a valid verification method.",
            "error": f"Unknown method: {verification_method}"
        }
