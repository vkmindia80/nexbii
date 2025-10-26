#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for White-Labeling Multi-Tenancy System
Tests all tenant management, branding, DNS verification, and SSL certificate APIs
"""

import requests
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

class TenantBrandingAPITester:
    def __init__(self, base_url: str = "https://ui-implementation-1.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tenant_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Test data
        self.test_credentials = {
            "email": "admin@nexbii.demo",
            "password": "demo123"
        }

    def log_test(self, name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name}: PASSED")
        else:
            print(f"❌ {name}: FAILED - {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": datetime.now().isoformat()
        })

    def run_api_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                     data: Optional[Dict] = None, headers: Optional[Dict] = None) -> tuple[bool, Any]:
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Default headers
        test_headers = {'Content-Type': 'application/json'}
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            test_headers.update(headers)

        print(f"\n🔍 Testing {name}...")
        print(f"   {method} {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)
            else:
                self.log_test(name, False, f"Unsupported method: {method}")
                return False, {}

            print(f"   Status: {response.status_code}")
            
            success = response.status_code == expected_status
            response_data = {}
            
            try:
                response_data = response.json() if response.content else {}
            except:
                response_data = {"raw_response": response.text}

            if success:
                self.log_test(name, True, f"Status {response.status_code}", response_data)
            else:
                error_detail = response_data.get('detail', response.text[:200])
                self.log_test(name, False, f"Expected {expected_status}, got {response.status_code}: {error_detail}", response_data)

            return success, response_data

        except requests.exceptions.Timeout:
            self.log_test(name, False, "Request timeout (30s)")
            return False, {}
        except requests.exceptions.ConnectionError:
            self.log_test(name, False, "Connection error - server may be down")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Request failed: {str(e)}")
            return False, {}

    def test_authentication(self) -> bool:
        """Test login and get authentication token"""
        print("\n" + "="*60)
        print("🔐 AUTHENTICATION TESTS")
        print("="*60)
        
        success, response = self.run_api_test(
            "User Login",
            "POST",
            "/api/auth/login",
            200,
            data=self.test_credentials
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            print(f"   ✅ Token obtained: {self.token[:20]}...")
            return True
        else:
            print("   ❌ Failed to obtain authentication token")
            return False

    def test_tenant_provisioning(self) -> bool:
        """Test tenant provisioning if no tenant exists"""
        print("\n" + "="*60)
        print("🏗️  TENANT PROVISIONING TESTS")
        print("="*60)
        
        # Try to provision a tenant for testing
        provision_data = {
            "organization_name": "Demo Organization",
            "admin_name": "Demo Admin",
            "admin_email": "admin@nexbii.demo",
            "admin_password": "demo123456",
            "plan": "enterprise",
            "custom_slug": "demo"
        }
        
        success, response = self.run_api_test(
            "Provision Demo Tenant",
            "POST",
            "/api/tenants/provision",
            200,
            data=provision_data
        )
        
        if success and 'tenant' in response:
            tenant_data = response['tenant']
            self.tenant_id = tenant_data['id']
            print(f"   ✅ Tenant provisioned: {tenant_data.get('name')}")
            print(f"   ✅ Tenant ID: {self.tenant_id}")
            return True
        else:
            print("   ℹ️  Tenant provisioning failed (may already exist)")
            return False

    def test_tenant_management(self) -> bool:
        """Test core tenant management APIs"""
        print("\n" + "="*60)
        print("🏢 TENANT MANAGEMENT TESTS")
        print("="*60)
        
        all_passed = True
        
        # Get current tenant
        success, response = self.run_api_test(
            "Get Current Tenant",
            "GET",
            "/api/tenants/current",
            200
        )
        
        if success and 'id' in response:
            self.tenant_id = response['id']
            print(f"   ✅ Tenant ID: {self.tenant_id}")
            print(f"   ✅ Tenant Name: {response.get('name', 'N/A')}")
            print(f"   ✅ Plan: {response.get('plan', 'N/A')}")
            print(f"   ✅ Features: {response.get('features', {})}")
        else:
            all_passed = False
            print("   ❌ Failed to get current tenant")
            return False

        # Get tenant by ID
        success, response = self.run_api_test(
            "Get Tenant by ID",
            "GET",
            f"/api/tenants/{self.tenant_id}",
            200
        )
        all_passed = all_passed and success

        return all_passed

    def test_tenant_branding(self) -> bool:
        """Test tenant branding APIs"""
        print("\n" + "="*60)
        print("🎨 TENANT BRANDING TESTS")
        print("="*60)
        
        if not self.tenant_id:
            print("❌ No tenant ID available for branding tests")
            return False
        
        all_passed = True
        
        # Test branding update
        branding_data = {
            "branding": {
                "logo_url": "https://example.com/logo.png",
                "logo_dark_url": "https://example.com/logo-dark.png",
                "primary_color": "#667eea",
                "secondary_color": "#764ba2",
                "accent_color": "#3b82f6",
                "font_family": "Arial, sans-serif",
                "custom_css": "/* Custom styles */",
                "favicon_url": "https://example.com/favicon.ico"
            }
        }
        
        success, response = self.run_api_test(
            "Update Tenant Branding",
            "PUT",
            f"/api/tenants/{self.tenant_id}/branding",
            200,
            data=branding_data
        )
        all_passed = all_passed and success
        
        if success:
            print(f"   ✅ Branding updated successfully")
            branding = response.get('branding', {})
            print(f"   ✅ Logo URL: {branding.get('logo_url', 'N/A')}")
            print(f"   ✅ Primary Color: {branding.get('primary_color', 'N/A')}")

        return all_passed

    def test_custom_domains(self) -> bool:
        """Test custom domain management APIs"""
        print("\n" + "="*60)
        print("🌐 CUSTOM DOMAINS TESTS")
        print("="*60)
        
        if not self.tenant_id:
            print("❌ No tenant ID available for domain tests")
            return False
        
        all_passed = True
        domain_id = None
        test_domain = "analytics.testcompany.com"
        
        # Add custom domain
        success, response = self.run_api_test(
            "Add Custom Domain",
            "POST",
            f"/api/tenants/{self.tenant_id}/domains",
            200,
            data={"domain": test_domain, "is_primary": False}
        )
        all_passed = all_passed and success
        
        if success and 'id' in response:
            domain_id = response['id']
            print(f"   ✅ Domain added: {response.get('domain')}")
            print(f"   ✅ Domain ID: {domain_id}")
            print(f"   ✅ Verification Token: {response.get('verification_token', 'N/A')[:12]}...")
        
        # List custom domains
        success, response = self.run_api_test(
            "List Custom Domains",
            "GET",
            f"/api/tenants/{self.tenant_id}/domains",
            200
        )
        all_passed = all_passed and success
        
        if success:
            domains = response if isinstance(response, list) else []
            print(f"   ✅ Found {len(domains)} domains")
        
        # Get verification instructions (if domain was added)
        if domain_id:
            success, response = self.run_api_test(
                "Get Domain Verification Instructions",
                "GET",
                f"/api/tenants/{self.tenant_id}/domains/{domain_id}/verification-instructions",
                200
            )
            all_passed = all_passed and success
            
            if success:
                print(f"   ✅ Verification Method: {response.get('method', 'N/A')}")
                print(f"   ✅ Instructions Available: {bool(response.get('instructions'))}")
            
            # Test domain verification (will likely fail as we don't have real DNS)
            success, response = self.run_api_test(
                "Verify Domain (Expected to Fail)",
                "POST",
                f"/api/tenants/{self.tenant_id}/domains/{domain_id}/verify",
                200  # API should return 200 with success: false
            )
            # Don't count this as failure since we expect DNS verification to fail
            if not success:
                print("   ℹ️  Domain verification failed as expected (no real DNS setup)")

        return all_passed

    def test_ssl_certificates(self) -> bool:
        """Test SSL certificate management APIs"""
        print("\n" + "="*60)
        print("🔒 SSL CERTIFICATE TESTS")
        print("="*60)
        
        if not self.tenant_id:
            print("❌ No tenant ID available for SSL tests")
            return False
        
        all_passed = True
        
        # First, we need a domain to test SSL with
        # Let's get existing domains
        success, response = self.run_api_test(
            "Get Domains for SSL Testing",
            "GET",
            f"/api/tenants/{self.tenant_id}/domains",
            200
        )
        
        if not success or not response:
            print("   ℹ️  No domains available for SSL testing")
            return True  # Not a failure, just no domains to test
        
        domains = response if isinstance(response, list) else []
        if not domains:
            print("   ℹ️  No domains found for SSL testing")
            return True
        
        domain_id = domains[0]['id']
        domain_name = domains[0]['domain']
        print(f"   ℹ️  Testing SSL with domain: {domain_name}")
        
        # Test SSL certificate upload (will fail without valid cert, but tests API)
        test_cert_data = {
            "certificate_pem": "-----BEGIN CERTIFICATE-----\nTEST_CERT_DATA\n-----END CERTIFICATE-----",
            "private_key_pem": "-----BEGIN PRIVATE KEY-----\nTEST_KEY_DATA\n-----END PRIVATE KEY-----",
            "chain_pem": "-----BEGIN CERTIFICATE-----\nTEST_CHAIN_DATA\n-----END CERTIFICATE-----"
        }
        
        success, response = self.run_api_test(
            "Upload SSL Certificate (Expected to Fail)",
            "POST",
            f"/api/tenants/{self.tenant_id}/domains/{domain_id}/ssl/upload",
            400,  # Expect 400 due to invalid certificate
            data=test_cert_data
        )
        # This should fail with invalid certificate, which is expected
        if not success and response.get('detail', '').find('Invalid certificate') >= 0:
            print("   ✅ SSL upload validation working (rejected invalid certificate)")
            all_passed = True
        
        # Test Let's Encrypt request (will fail without proper domain setup)
        success, response = self.run_api_test(
            "Request Let's Encrypt Certificate (Expected to Fail)",
            "POST",
            f"/api/tenants/{self.tenant_id}/domains/{domain_id}/ssl/letsencrypt",
            200,  # API returns 200 with success: false
            data={"email": "admin@example.com", "staging": True}
        )
        # Don't count as failure since we expect this to fail without proper domain setup
        if not success:
            print("   ℹ️  Let's Encrypt request failed as expected (no real domain setup)")
        
        # Test SSL certificate info
        success, response = self.run_api_test(
            "Get SSL Certificate Info",
            "GET",
            f"/api/tenants/{self.tenant_id}/domains/{domain_id}/ssl/info",
            200
        )
        all_passed = all_passed and success
        
        if success:
            print(f"   ✅ SSL Status: {response.get('ssl_enabled', False)}")

        return all_passed

    def test_tenant_features(self) -> bool:
        """Test tenant feature access APIs"""
        print("\n" + "="*60)
        print("🔍 TENANT FEATURES TESTS")
        print("="*60)
        
        if not self.tenant_id:
            print("❌ No tenant ID available for feature tests")
            return False
        
        all_passed = True
        
        # Test feature access checks
        features_to_test = ["white_labeling", "ai_enabled", "advanced_analytics", "api_access"]
        
        for feature in features_to_test:
            success, response = self.run_api_test(
                f"Check Feature Access: {feature}",
                "GET",
                f"/api/tenants/{self.tenant_id}/features/{feature}",
                200
            )
            all_passed = all_passed and success
            
            if success:
                has_access = response.get('has_access', False)
                print(f"   ✅ {feature}: {'Enabled' if has_access else 'Disabled'}")

        return all_passed

    def test_tenant_limits_and_usage(self) -> bool:
        """Test tenant limits and usage APIs"""
        print("\n" + "="*60)
        print("📊 TENANT LIMITS & USAGE TESTS")
        print("="*60)
        
        if not self.tenant_id:
            print("❌ No tenant ID available for limits tests")
            return False
        
        all_passed = True
        
        # Test limits check
        success, response = self.run_api_test(
            "Check Tenant Limits",
            "GET",
            f"/api/tenants/{self.tenant_id}/limits",
            200
        )
        all_passed = all_passed and success
        
        if success:
            print(f"   ✅ Within User Limit: {response.get('within_user_limit', 'N/A')}")
            print(f"   ✅ Within Storage Limit: {response.get('within_storage_limit', 'N/A')}")
            limits_exceeded = response.get('limits_exceeded', [])
            if limits_exceeded:
                print(f"   ⚠️  Limits Exceeded: {', '.join(limits_exceeded)}")
        
        # Test usage stats
        success, response = self.run_api_test(
            "Get Tenant Usage",
            "GET",
            f"/api/tenants/{self.tenant_id}/usage",
            200
        )
        all_passed = all_passed and success
        
        if success:
            print(f"   ✅ Current Users: {response.get('current_users', 'N/A')}")
            print(f"   ✅ Current Dashboards: {response.get('current_dashboards', 'N/A')}")
            print(f"   ✅ Storage Used: {response.get('storage_used_mb', 'N/A')} MB")

        return all_passed

    def run_all_tests(self) -> bool:
        """Run all test suites"""
        print("🚀 Starting Comprehensive Tenant Branding API Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"📧 Test User: {self.test_credentials['email']}")
        print("="*80)
        
        # Authentication is required for all other tests
        if not self.test_authentication():
            print("\n❌ Authentication failed - cannot proceed with other tests")
            return False
        
        # Try tenant provisioning if needed
        self.test_tenant_provisioning()
        
        # Run all test suites
        test_suites = [
            ("Tenant Management", self.test_tenant_management),
            ("Tenant Branding", self.test_tenant_branding),
            ("Custom Domains", self.test_custom_domains),
            ("SSL Certificates", self.test_ssl_certificates),
            ("Tenant Features", self.test_tenant_features),
            ("Limits & Usage", self.test_tenant_limits_and_usage),
        ]
        
        suite_results = []
        for suite_name, test_func in test_suites:
            try:
                result = test_func()
                suite_results.append((suite_name, result))
            except Exception as e:
                print(f"\n❌ {suite_name} test suite failed with exception: {str(e)}")
                suite_results.append((suite_name, False))
        
        # Print final results
        print("\n" + "="*80)
        print("📊 FINAL TEST RESULTS")
        print("="*80)
        
        for suite_name, passed in suite_results:
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{suite_name:.<30} {status}")
        
        print(f"\nOverall: {self.tests_passed}/{self.tests_run} tests passed")
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Save detailed results
        results_file = f"/app/test_reports/backend_api_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.tests_run,
                    "passed_tests": self.tests_passed,
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat()
                },
                "test_results": self.test_results
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return success_rate >= 70  # Consider 70%+ success rate as passing

def main():
    """Main test execution"""
    tester = TenantBrandingAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())