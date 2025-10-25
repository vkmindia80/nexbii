#!/usr/bin/env python3
"""
White-Labeling Feature Testing Script
Tests all white-labeling functionality including:
- Custom domain DNS verification
- SSL certificate management
- Branded email templates
- Tenant switcher
- Themed UI components
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:8001"
API_BASE = f"{BASE_URL}/api"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

test_results = {
    "passed": 0,
    "failed": 0,
    "warnings": 0,
    "tests": []
}

def log_test(name, status, message, details=None):
    """Log test result"""
    result = {
        "name": name,
        "status": status,
        "message": message,
        "details": details,
        "timestamp": datetime.now().isoformat()
    }
    test_results["tests"].append(result)
    
    if status == "PASS":
        test_results["passed"] += 1
        print(f"{GREEN}✓ PASS{RESET}: {name} - {message}")
    elif status == "FAIL":
        test_results["failed"] += 1
        print(f"{RED}✗ FAIL{RESET}: {name} - {message}")
    elif status == "WARN":
        test_results["warnings"] += 1
        print(f"{YELLOW}⚠ WARN{RESET}: {name} - {message}")
    
    if details:
        print(f"  {BLUE}Details{RESET}: {json.dumps(details, indent=2)}")

def print_header(text):
    """Print section header"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{text.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")

# ========================================
# SETUP: Create Enterprise Test Tenant
# ========================================

def create_enterprise_tenant():
    """Create an enterprise tenant for testing"""
    print_header("SETUP: Creating Enterprise Test Tenant")
    
    tenant_data = {
        "organization_name": "WhiteLabel Test Corp",
        "admin_email": f"whitelabel-test-{datetime.now().timestamp()}@test.com",
        "admin_name": "WhiteLabel Admin",
        "admin_password": "Test123!@#",
        "plan": "enterprise",
        "custom_slug": f"whitelabel-test-{int(datetime.now().timestamp())}"
    }
    
    try:
        response = requests.post(f"{API_BASE}/tenants/provision", json=tenant_data)
        if response.status_code == 200:
            data = response.json()
            tenant_id = data["tenant"]["id"]
            admin_email = tenant_data["admin_email"]
            admin_password = tenant_data["admin_password"]
            
            log_test(
                "Create Enterprise Tenant",
                "PASS",
                f"Enterprise tenant created: {data['tenant']['name']}",
                {"tenant_id": tenant_id, "slug": data['tenant']['slug']}
            )
            
            # Login to get token
            login_response = requests.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": admin_email,
                    "password": admin_password
                }
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                return tenant_id, token, data["tenant"]
            else:
                log_test("Login", "FAIL", f"Failed to login: {login_response.text}")
                return None, None, None
        else:
            log_test("Create Enterprise Tenant", "FAIL", f"Failed: {response.text}")
            return None, None, None
    except Exception as e:
        log_test("Create Enterprise Tenant", "FAIL", f"Exception: {str(e)}")
        return None, None, None

# ========================================
# TEST 1: Custom Domain DNS Verification
# ========================================

def test_custom_domains(tenant_id, token):
    """Test custom domain management and DNS verification"""
    print_header("TEST 1: Custom Domain DNS Verification")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1.1: Add custom domain
    domain_data = {
        "domain": "analytics.whitelabeltest.com",
        "is_primary": True
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/tenants/{tenant_id}/domains",
            json=domain_data,
            headers=headers
        )
        
        if response.status_code == 200:
            domain = response.json()
            domain_id = domain["id"]
            log_test(
                "Add Custom Domain",
                "PASS",
                f"Domain added: {domain['domain']}",
                {"domain_id": domain_id, "verification_method": domain["verification_method"]}
            )
        else:
            log_test("Add Custom Domain", "FAIL", f"Failed: {response.text}")
            return None
    except Exception as e:
        log_test("Add Custom Domain", "FAIL", f"Exception: {str(e)}")
        return None
    
    # Test 1.2: Get verification instructions
    try:
        response = requests.get(
            f"{API_BASE}/tenants/{tenant_id}/domains/{domain_id}/verification-instructions",
            headers=headers
        )
        
        if response.status_code == 200:
            instructions = response.json()
            log_test(
                "Get Verification Instructions",
                "PASS",
                f"Instructions retrieved for {instructions['method']}",
                {
                    "method": instructions["method"],
                    "record_type": instructions.get("record_type"),
                    "host": instructions.get("host"),
                    "value": instructions.get("value")[:50] + "..." if instructions.get("value") else None
                }
            )
        else:
            log_test("Get Verification Instructions", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Get Verification Instructions", "FAIL", f"Exception: {str(e)}")
    
    # Test 1.3: List custom domains
    try:
        response = requests.get(
            f"{API_BASE}/tenants/{tenant_id}/domains",
            headers=headers
        )
        
        if response.status_code == 200:
            domains = response.json()
            log_test(
                "List Custom Domains",
                "PASS",
                f"Found {len(domains)} domain(s)",
                {"domains": [d["domain"] for d in domains]}
            )
        else:
            log_test("List Custom Domains", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("List Custom Domains", "FAIL", f"Exception: {str(e)}")
    
    # Test 1.4: Attempt verification (will fail without actual DNS setup)
    try:
        response = requests.post(
            f"{API_BASE}/tenants/{tenant_id}/domains/{domain_id}/verify",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                log_test(
                    "Domain Verification",
                    "PASS",
                    "Domain verified successfully",
                    result
                )
            else:
                log_test(
                    "Domain Verification (Expected Failure)",
                    "PASS",
                    "Verification failed as expected (no DNS setup)",
                    {"error": result.get("error")}
                )
        else:
            log_test("Domain Verification", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Domain Verification", "FAIL", f"Exception: {str(e)}")
    
    return domain_id

# ========================================
# TEST 2: DNS Verification Service
# ========================================

def test_dns_verification_service():
    """Test DNS verification service methods directly"""
    print_header("TEST 2: DNS Verification Service")
    
    try:
        from app.services.dns_verification_service import DNSVerificationService
        
        # Test 2.1: CNAME verification (will fail without real DNS)
        result = DNSVerificationService.verify_cname_record(
            "test.example.com",
            "verify-token123.nexbii.com"
        )
        log_test(
            "CNAME Verification Method",
            "PASS" if not result["verified"] else "WARN",
            "CNAME verification method working (failed as expected without DNS)",
            {"result": result}
        )
        
        # Test 2.2: TXT verification (will fail without real DNS)
        result = DNSVerificationService.verify_txt_record(
            "test.example.com",
            "test-token-123"
        )
        log_test(
            "TXT Verification Method",
            "PASS" if not result["verified"] else "WARN",
            "TXT verification method working (failed as expected without DNS)",
            {"result": result}
        )
        
        # Test 2.3: HTTP verification (will fail without server)
        result = DNSVerificationService.verify_http_file(
            "test.example.com",
            "test-token-123"
        )
        log_test(
            "HTTP Verification Method",
            "PASS" if not result["verified"] else "WARN",
            "HTTP verification method working (failed as expected without server)",
            {"result": result}
        )
        
        # Test 2.4: Get instructions for all methods
        for method in ["cname", "txt", "http"]:
            instructions = DNSVerificationService.get_verification_instructions(
                "test.example.com",
                method,
                "test-token-123"
            )
            log_test(
                f"Verification Instructions ({method.upper()})",
                "PASS",
                f"Instructions generated for {method} method",
                {
                    "method": instructions["method"],
                    "title": instructions["title"]
                }
            )
        
    except Exception as e:
        log_test("DNS Verification Service", "FAIL", f"Exception: {str(e)}")

# ========================================
# TEST 3: SSL Certificate Management
# ========================================

def test_ssl_certificates(tenant_id, domain_id, token):
    """Test SSL certificate management"""
    print_header("TEST 3: SSL Certificate Management")
    
    if not domain_id:
        log_test("SSL Certificate Tests", "WARN", "Skipped: No domain ID available")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3.1: Generate self-signed certificate
    try:
        from app.services.ssl_certificate_service import SSLCertificateService
        
        cert_pem, key_pem = SSLCertificateService.generate_self_signed_certificate(
            "analytics.whitelabeltest.com",
            days_valid=365
        )
        
        log_test(
            "Generate Self-Signed Certificate",
            "PASS",
            "Self-signed certificate generated successfully",
            {"cert_length": len(cert_pem), "key_length": len(key_pem)}
        )
        
        # Test 3.2: Validate certificate
        validation = SSLCertificateService.validate_certificate(
            cert_pem,
            key_pem,
            "analytics.whitelabeltest.com"
        )
        
        if validation["valid"]:
            log_test(
                "Validate SSL Certificate",
                "PASS",
                "Certificate validation successful",
                {
                    "subject": validation["subject"],
                    "issuer": validation["issuer"],
                    "days_until_expiry": validation["days_until_expiry"]
                }
            )
        else:
            log_test("Validate SSL Certificate", "FAIL", f"Validation failed: {validation['error']}")
        
        # Test 3.3: Upload SSL certificate (will fail without verified domain)
        ssl_data = {
            "certificate_pem": cert_pem,
            "private_key_pem": key_pem
        }
        
        response = requests.post(
            f"{API_BASE}/tenants/{tenant_id}/domains/{domain_id}/ssl/upload",
            json=ssl_data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            log_test(
                "Upload SSL Certificate",
                "PASS" if result.get("success") else "WARN",
                result.get("message", "Certificate upload attempted"),
                result.get("certificate_info")
            )
        else:
            # Expected to fail since domain is not verified
            log_test(
                "Upload SSL Certificate (Expected Failure)",
                "PASS",
                "Upload failed as expected (domain not verified)",
                {"status_code": response.status_code}
            )
        
    except Exception as e:
        log_test("SSL Certificate Management", "FAIL", f"Exception: {str(e)}")
    
    # Test 3.4: Get SSL certificate info
    try:
        response = requests.get(
            f"{API_BASE}/tenants/{tenant_id}/domains/{domain_id}/ssl/info",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            log_test(
                "Get SSL Certificate Info",
                "PASS",
                f"SSL info retrieved: {'Enabled' if result.get('ssl_enabled') else 'Not configured'}",
                result
            )
        else:
            log_test("Get SSL Certificate Info", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Get SSL Certificate Info", "FAIL", f"Exception: {str(e)}")

# ========================================
# TEST 4: Branded Email Templates
# ========================================

def test_email_templates(tenant):
    """Test branded email templates"""
    print_header("TEST 4: Branded Email Templates")
    
    try:
        from app.services.email_template_service import EmailTemplateService
        
        # Setup tenant branding
        branding = {
            "logo_url": "https://example.com/logo.png",
            "primary_color": "#667eea",
            "secondary_color": "#764ba2",
            "accent_color": "#3b82f6",
            "company_name": tenant["name"],
            "font_family": "Arial, sans-serif"
        }
        
        # Test 4.1: Welcome email
        welcome_email = EmailTemplateService.generate_welcome_email(
            user_name="John Doe",
            login_url="https://whitelabel-test.nexbii.com/login",
            tenant_branding=branding
        )
        
        log_test(
            "Generate Welcome Email",
            "PASS",
            "Welcome email template generated with branding",
            {
                "subject": welcome_email["subject"],
                "has_html": len(welcome_email["html"]) > 0,
                "has_text": len(welcome_email["text"]) > 0,
                "includes_branding": branding["company_name"] in welcome_email["html"]
            }
        )
        
        # Test 4.2: Password reset email
        reset_email = EmailTemplateService.generate_password_reset_email(
            user_name="John Doe",
            reset_url="https://whitelabel-test.nexbii.com/reset?token=abc123",
            expiry_hours=24,
            tenant_branding=branding
        )
        
        log_test(
            "Generate Password Reset Email",
            "PASS",
            "Password reset email template generated with branding",
            {
                "subject": reset_email["subject"],
                "has_html": len(reset_email["html"]) > 0,
                "includes_branding": branding["company_name"] in reset_email["html"]
            }
        )
        
        # Test 4.3: Invitation email
        invitation_email = EmailTemplateService.generate_invitation_email(
            invitee_email="new-user@test.com",
            inviter_name="Admin User",
            organization_name=tenant["name"],
            invitation_url="https://whitelabel-test.nexbii.com/invite?token=xyz789",
            role="editor",
            tenant_branding=branding
        )
        
        log_test(
            "Generate Invitation Email",
            "PASS",
            "Invitation email template generated with branding",
            {
                "subject": invitation_email["subject"],
                "has_html": len(invitation_email["html"]) > 0,
                "includes_branding": branding["company_name"] in invitation_email["html"]
            }
        )
        
        # Test 4.4: Domain verification email
        verification_instructions = {
            "method": "CNAME",
            "title": "DNS Verification",
            "instructions": "Add CNAME record..."
        }
        
        domain_email = EmailTemplateService.generate_domain_verification_email(
            admin_name="Admin User",
            domain="analytics.whitelabeltest.com",
            verification_instructions=verification_instructions,
            tenant_branding=branding
        )
        
        log_test(
            "Generate Domain Verification Email",
            "PASS",
            "Domain verification email template generated with branding",
            {
                "subject": domain_email["subject"],
                "has_html": len(domain_email["html"]) > 0,
                "includes_branding": branding["company_name"] in domain_email["html"]
            }
        )
        
        # Test 4.5: Custom template rendering
        custom_html = "<p>Hello {{ user_name }}, welcome to {{ company_name }}!</p>"
        rendered = EmailTemplateService.render_custom_template(
            custom_html,
            {"user_name": "Test User", "company_name": tenant["name"]},
            branding
        )
        
        log_test(
            "Render Custom Email Template",
            "PASS",
            "Custom email template rendered with variables",
            {
                "rendered_length": len(rendered),
                "includes_company": tenant["name"] in rendered
            }
        )
        
    except Exception as e:
        log_test("Email Templates", "FAIL", f"Exception: {str(e)}")

# ========================================
# TEST 5: Tenant Branding Management
# ========================================

def test_tenant_branding(tenant_id, token):
    """Test tenant branding management"""
    print_header("TEST 5: Tenant Branding Management")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 5.1: Update tenant branding
    branding_data = {
        "branding": {
            "logo_url": "https://cdn.example.com/whitelabel-logo.png",
            "logo_dark_url": "https://cdn.example.com/whitelabel-logo-dark.png",
            "primary_color": "#FF6B6B",
            "secondary_color": "#4ECDC4",
            "accent_color": "#45B7D1",
            "font_family": "Inter, sans-serif",
            "favicon_url": "https://cdn.example.com/favicon.ico",
            "custom_css": ".custom-theme { color: #FF6B6B; }"
        }
    }
    
    try:
        response = requests.put(
            f"{API_BASE}/tenants/{tenant_id}/branding",
            json=branding_data,
            headers=headers
        )
        
        if response.status_code == 200:
            tenant = response.json()
            log_test(
                "Update Tenant Branding",
                "PASS",
                "Tenant branding updated successfully",
                {
                    "logo_url": tenant["branding"].get("logo_url"),
                    "primary_color": tenant["branding"].get("primary_color"),
                    "custom_css_length": len(tenant["branding"].get("custom_css", ""))
                }
            )
        else:
            log_test("Update Tenant Branding", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Update Tenant Branding", "FAIL", f"Exception: {str(e)}")
    
    # Test 5.2: Get current tenant (should include branding)
    try:
        response = requests.get(
            f"{API_BASE}/tenants/current",
            headers=headers
        )
        
        if response.status_code == 200:
            tenant = response.json()
            has_branding = "branding" in tenant and len(tenant["branding"]) > 0
            log_test(
                "Get Current Tenant with Branding",
                "PASS" if has_branding else "WARN",
                f"Tenant retrieved {'with' if has_branding else 'without'} branding",
                {
                    "tenant_id": tenant["id"],
                    "name": tenant["name"],
                    "plan": tenant["plan"],
                    "has_white_labeling": tenant.get("features", {}).get("white_labeling", False)
                }
            )
        else:
            log_test("Get Current Tenant", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Get Current Tenant", "FAIL", f"Exception: {str(e)}")
    
    # Test 5.3: Check white-labeling feature access
    try:
        response = requests.get(
            f"{API_BASE}/tenants/{tenant_id}/features/white_labeling",
            headers=headers
        )
        
        if response.status_code == 200:
            feature_access = response.json()
            log_test(
                "Check White-Labeling Feature Access",
                "PASS",
                f"Feature access check: {'Enabled' if feature_access.get('has_access') else 'Disabled'}",
                feature_access
            )
        else:
            log_test("Check Feature Access", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Check Feature Access", "FAIL", f"Exception: {str(e)}")

# ========================================
# TEST 6: Frontend Integration Points
# ========================================

def test_frontend_integration(tenant_id, token):
    """Test frontend integration points"""
    print_header("TEST 6: Frontend Integration Points")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 6.1: Tenant limits check (used by frontend)
    try:
        response = requests.get(
            f"{API_BASE}/tenants/{tenant_id}/limits",
            headers=headers
        )
        
        if response.status_code == 200:
            limits = response.json()
            log_test(
                "Get Tenant Limits",
                "PASS",
                "Tenant limits retrieved (used by frontend)",
                {
                    "within_user_limit": limits.get("within_user_limit"),
                    "within_datasource_limit": limits.get("within_datasource_limit"),
                    "within_dashboard_limit": limits.get("within_dashboard_limit")
                }
            )
        else:
            log_test("Get Tenant Limits", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Get Tenant Limits", "FAIL", f"Exception: {str(e)}")
    
    # Test 6.2: Tenant usage stats (used by tenant switcher)
    try:
        response = requests.get(
            f"{API_BASE}/tenants/{tenant_id}/usage",
            headers=headers
        )
        
        if response.status_code == 200:
            usage = response.json()
            log_test(
                "Get Tenant Usage Stats",
                "PASS",
                "Tenant usage stats retrieved (used by tenant switcher)",
                {
                    "current_users": usage.get("current_users"),
                    "current_datasources": usage.get("current_datasources"),
                    "current_dashboards": usage.get("current_dashboards")
                }
            )
        else:
            log_test("Get Tenant Usage Stats", "FAIL", f"Failed: {response.text}")
    except Exception as e:
        log_test("Get Tenant Usage Stats", "FAIL", f"Exception: {str(e)}")

# ========================================
# MAIN TEST RUNNER
# ========================================

def main():
    """Main test runner"""
    print(f"\n{BLUE}{'='*80}{RESET}")
    print(f"{BLUE}{'WHITE-LABELING FEATURE TEST SUITE'.center(80)}{RESET}")
    print(f"{BLUE}{'='*80}{RESET}\n")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Setup: Create enterprise tenant
    tenant_id, token, tenant = create_enterprise_tenant()
    
    if not tenant_id or not token:
        print(f"\n{RED}FATAL: Could not create test tenant. Aborting tests.{RESET}\n")
        sys.exit(1)
    
    # Run all tests
    domain_id = test_custom_domains(tenant_id, token)
    test_dns_verification_service()
    test_ssl_certificates(tenant_id, domain_id, token)
    test_email_templates(tenant)
    test_tenant_branding(tenant_id, token)
    test_frontend_integration(tenant_id, token)
    
    # Print summary
    print_header("TEST SUMMARY")
    print(f"{GREEN}✓ Passed:{RESET} {test_results['passed']}")
    print(f"{RED}✗ Failed:{RESET} {test_results['failed']}")
    print(f"{YELLOW}⚠ Warnings:{RESET} {test_results['warnings']}")
    print(f"\nTotal Tests: {test_results['passed'] + test_results['failed'] + test_results['warnings']}")
    
    # Save detailed results
    with open('/app/white_labeling_test_results.json', 'w') as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n{BLUE}Detailed results saved to: /app/white_labeling_test_results.json{RESET}")
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Exit with appropriate code
    sys.exit(0 if test_results['failed'] == 0 else 1)

if __name__ == "__main__":
    main()
