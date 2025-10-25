#!/usr/bin/env python3
"""
Backend Services Direct Testing
Tests DNS verification, SSL, and email template services
"""

import sys
sys.path.insert(0, '/app/backend')

from app.services.dns_verification_service import DNSVerificationService
from app.services.ssl_certificate_service import SSLCertificateService
from app.services.email_template_service import EmailTemplateService
import json

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

def log_test(name, status, details=None):
    if status == "PASS":
        print(f"{GREEN}✓ PASS{RESET}: {name}")
    else:
        print(f"{RED}✗ FAIL{RESET}: {name}")
    if details:
        print(f"  Details: {json.dumps(details, indent=2)}")

# Test DNS Verification Service
print_header("DNS Verification Service")

# Test CNAME
result = DNSVerificationService.verify_cname_record(
    "test.example.com",
    "verify-token123.nexbii.com"
)
log_test(
    "CNAME Verification",
    "PASS" if not result["verified"] and result["error"] else "FAIL",
    {"verified": result["verified"], "error": result["error"]}
)

# Test TXT
result = DNSVerificationService.verify_txt_record(
    "test.example.com",
    "test-token-123"
)
log_test(
    "TXT Verification",
    "PASS" if not result["verified"] and result["error"] else "FAIL",
    {"verified": result["verified"], "error": result["error"]}
)

# Test HTTP
result = DNSVerificationService.verify_http_file(
    "test.example.com",
    "test-token-123"
)
log_test(
    "HTTP Verification",
    "PASS" if not result["verified"] and result["error"] else "FAIL",
    {"verified": result["verified"], "error": result["error"]}
)

# Test instructions
for method in ["cname", "txt", "http"]:
    instructions = DNSVerificationService.get_verification_instructions(
        "test.example.com",
        method,
        "test-token-123"
    )
    log_test(
        f"Get {method.upper()} Instructions",
        "PASS",
        {"method": instructions["method"], "title": instructions["title"]}
    )

# Test SSL Certificate Service
print_header("SSL Certificate Service")

# Generate self-signed certificate
cert_pem, key_pem = SSLCertificateService.generate_self_signed_certificate(
    "test.whitelabel.com",
    days_valid=365
)
log_test(
    "Generate Self-Signed Certificate",
    "PASS" if cert_pem and key_pem else "FAIL",
    {"cert_length": len(cert_pem), "key_length": len(key_pem)}
)

# Validate certificate
validation = SSLCertificateService.validate_certificate(
    cert_pem,
    key_pem,
    "test.whitelabel.com"
)
log_test(
    "Validate Certificate",
    "PASS" if validation["valid"] else "FAIL",
    {
        "valid": validation["valid"],
        "subject": validation.get("subject"),
        "days_until_expiry": validation.get("days_until_expiry")
    }
)

# Test Email Template Service
print_header("Email Template Service")

branding = {
    "logo_url": "https://example.com/logo.png",
    "primary_color": "#667eea",
    "secondary_color": "#764ba2",
    "company_name": "Test Company"
}

# Welcome email
welcome = EmailTemplateService.generate_welcome_email(
    "John Doe",
    "https://test.com/login",
    branding
)
log_test(
    "Generate Welcome Email",
    "PASS" if welcome and "Test Company" in welcome["html"] else "FAIL",
    {"subject": welcome["subject"], "has_branding": "Test Company" in welcome["html"]}
)

# Password reset email
reset = EmailTemplateService.generate_password_reset_email(
    "John Doe",
    "https://test.com/reset?token=abc",
    24,
    branding
)
log_test(
    "Generate Password Reset Email",
    "PASS" if reset and "Test Company" in reset["html"] else "FAIL",
    {"subject": reset["subject"], "has_branding": "Test Company" in reset["html"]}
)

# Invitation email
invitation = EmailTemplateService.generate_invitation_email(
    "new@test.com",
    "Admin",
    "Test Org",
    "https://test.com/invite?token=xyz",
    "editor",
    branding
)
log_test(
    "Generate Invitation Email",
    "PASS" if invitation and "Test Company" in invitation["html"] else "FAIL",
    {"subject": invitation["subject"], "has_branding": "Test Company" in invitation["html"]}
)

# Domain verification email
domain = EmailTemplateService.generate_domain_verification_email(
    "Admin",
    "analytics.test.com",
    {"method": "CNAME", "title": "DNS Verification", "instructions": "Add CNAME record..."},
    branding
)
log_test(
    "Generate Domain Verification Email",
    "PASS" if domain and "Test Company" in domain["html"] else "FAIL",
    {"subject": domain["subject"], "has_branding": "Test Company" in domain["html"]}
)

# Custom template
custom = EmailTemplateService.render_custom_template(
    "<p>Hello {{ name }}</p>",
    {"name": "Test User", "company_name": "Test Company"},
    branding
)
log_test(
    "Render Custom Template",
    "PASS" if custom and "Test User" in custom else "FAIL",
    {"has_content": "Test User" in custom}
)

print(f"\n{BLUE}All backend service tests completed!{RESET}\n")
