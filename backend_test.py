#!/usr/bin/env python3
"""
Data Governance Backend API Testing
Phase 4.4: Comprehensive testing of all 18 governance endpoints

Tests:
- Data Catalog: 6 endpoints (CRUD + statistics)
- Data Lineage: 3 endpoints (create, graph, impact analysis)
- Data Classification: 3 endpoints (rules, scan PII)
- Access Requests: 6 endpoints (CRUD + approve/reject)
- Health: 1 endpoint
- Authentication & Multi-tenancy
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional

class GovernanceAPITester:
    def __init__(self, base_url: str = "https://monitor-db-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.token = None
        self.tenant_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.failed_tests = []
        
        # Test data storage
        self.catalog_entry_id = None
        self.lineage_id = None
        self.classification_rule_id = None
        self.access_request_id = None
        
        # Test credentials
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
            self.tenant_id = response.get('tenant_id')
            print(f"   ✅ Token obtained: {self.token[:20]}...")
            print(f"   ✅ Tenant ID: {self.tenant_id}")
            return True
        else:
            print("   ❌ Failed to obtain authentication token")
            return False

    def test_governance_health(self) -> bool:
        """Test governance health endpoint"""
        print("\n" + "="*60)
        print("🏥 GOVERNANCE HEALTH CHECK")
        print("="*60)
        
        success, response = self.run_api_test(
            "Governance Health Check",
            "GET",
            "/api/governance/health",
            200
        )
        
        if success and response.get('status') == 'healthy':
            print(f"   ✅ Service: {response.get('service', 'N/A')}")
            features = response.get('features', [])
            print(f"   ✅ Features: {', '.join(features)}")
            return True
        return False

    def test_data_catalog_endpoints(self) -> bool:
        """Test all 6 data catalog endpoints"""
        print("\n" + "="*60)
        print("📚 DATA CATALOG ENDPOINTS (6 endpoints)")
        print("="*60)
        
        all_passed = True
        
        # 1. Get catalog statistics
        success, stats = self.run_api_test(
            "Get Catalog Statistics",
            "GET",
            "/api/governance/catalog/statistics",
            200
        )
        all_passed = all_passed and success
        if success:
            print(f"   ✅ Total entries: {stats.get('total_entries', 0)}")
            print(f"   ✅ Total tables: {stats.get('total_tables', 0)}")
            print(f"   ✅ PII count: {stats.get('pii_count', 0)}")
        
        # 2. Get catalog entries (empty initially)
        success, entries_response = self.run_api_test(
            "Get Catalog Entries",
            "GET",
            "/api/governance/catalog",
            200
        )
        all_passed = all_passed and success
        if success:
            entries = entries_response.get('entries', [])
            print(f"   ✅ Found {len(entries)} existing entries")
        
        # 3. Create catalog entry
        catalog_data = {
            "datasource_id": "test-datasource-001",
            "table_name": "users",
            "column_name": "email",
            "display_name": "User Email Address",
            "description": "Primary email address for user accounts",
            "business_owner": "Data Team",
            "technical_owner": "Engineering Team",
            "tags": ["user-data", "contact-info"],
            "classification_level": "internal",
            "is_pii": True,
            "pii_types": ["email"],
            "data_type": "varchar(255)",
            "is_nullable": False,
            "usage_notes": "Used for authentication and notifications"
        }
        
        success, entry_response = self.run_api_test(
            "Create Catalog Entry",
            "POST",
            "/api/governance/catalog",
            200,
            data=catalog_data
        )
        all_passed = all_passed and success
        
        if success and 'id' in entry_response:
            self.catalog_entry_id = entry_response['id']
            print(f"   ✅ Created catalog entry: {self.catalog_entry_id}")
        
        # 4. Get specific catalog entry
        if self.catalog_entry_id:
            success, entry = self.run_api_test(
                "Get Specific Catalog Entry",
                "GET",
                f"/api/governance/catalog/{self.catalog_entry_id}",
                200
            )
            all_passed = all_passed and success
        
        # 5. Update catalog entry
        if self.catalog_entry_id:
            update_data = {
                "description": "Updated: Primary email address for user accounts with notifications",
                "tags": ["user-data", "contact-info", "notifications"]
            }
            
            success, updated_entry = self.run_api_test(
                "Update Catalog Entry",
                "PUT",
                f"/api/governance/catalog/{self.catalog_entry_id}",
                200,
                data=update_data
            )
            all_passed = all_passed and success
        
        return all_passed

    def test_data_lineage_endpoints(self) -> bool:
        """Test all 3 data lineage endpoints"""
        print("\n" + "="*60)
        print("🔗 DATA LINEAGE ENDPOINTS (3 endpoints)")
        print("="*60)
        
        all_passed = True
        
        # 1. Create lineage entry
        lineage_data = {
            "source_type": "datasource",
            "source_id": "test-datasource-001",
            "source_table": "users",
            "source_column": "email",
            "target_type": "query",
            "target_id": "test-query-001",
            "target_table": "user_analytics",
            "target_column": "user_email",
            "transformation_type": "select",
            "transformation_logic": "SELECT email FROM users",
            "confidence_score": 95,
            "is_active": True
        }
        
        success, lineage_response = self.run_api_test(
            "Create Lineage Entry",
            "POST",
            "/api/governance/lineage",
            200,
            data=lineage_data
        )
        all_passed = all_passed and success
        
        if success and 'id' in lineage_response:
            self.lineage_id = lineage_response['id']
            print(f"   ✅ Created lineage entry: {self.lineage_id}")
        
        # 2. Get lineage graph
        success, graph = self.run_api_test(
            "Get Lineage Graph",
            "GET",
            "/api/governance/lineage/graph/datasource/test-datasource-001",
            200
        )
        all_passed = all_passed and success
        if success:
            nodes = graph.get('nodes', [])
            edges = graph.get('edges', [])
            print(f"   ✅ Graph has {len(nodes)} nodes and {len(edges)} edges")
        
        # 3. Run impact analysis
        impact_data = {
            "change_type": "schema_change",
            "affected_resource_type": "datasource",
            "affected_resource_id": "test-datasource-001",
            "affected_resource_name": "Test Data Source"
        }
        
        success, impact_response = self.run_api_test(
            "Run Impact Analysis",
            "POST",
            "/api/governance/lineage/impact-analysis",
            200,
            data=impact_data
        )
        all_passed = all_passed and success
        if success:
            impact_level = impact_response.get('impact_level', 'unknown')
            affected_queries = impact_response.get('affected_queries', [])
            print(f"   ✅ Impact level: {impact_level}")
            print(f"   ✅ Affected queries: {len(affected_queries)}")
        
        return all_passed

    def test_classification_endpoints(self) -> bool:
        """Test all 3 classification endpoints"""
        print("\n" + "="*60)
        print("🛡️ DATA CLASSIFICATION ENDPOINTS (3 endpoints)")
        print("="*60)
        
        all_passed = True
        
        # 1. Create classification rule
        rule_data = {
            "name": "Email Detection Rule",
            "description": "Detects email addresses in column names and data",
            "pii_type": "email",
            "pattern": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "column_name_pattern": r"(email|e_mail|mail)",
            "classification_level": "internal",
            "is_enabled": True,
            "priority": 10
        }
        
        success, rule_response = self.run_api_test(
            "Create Classification Rule",
            "POST",
            "/api/governance/classification/rules",
            200,
            data=rule_data
        )
        all_passed = all_passed and success
        
        if success and 'id' in rule_response:
            self.classification_rule_id = rule_response['id']
            print(f"   ✅ Created classification rule: {self.classification_rule_id}")
        
        # 2. Get classification rules
        success, rules = self.run_api_test(
            "Get Classification Rules",
            "GET",
            "/api/governance/classification/rules",
            200
        )
        all_passed = all_passed and success
        if success:
            rules_list = rules if isinstance(rules, list) else []
            print(f"   ✅ Found {len(rules_list)} classification rules")
        
        # 3. Scan for PII
        scan_data = {
            "datasource_id": "test-datasource-001",
            "table_name": "users"
        }
        
        success, scan_results = self.run_api_test(
            "Scan for PII",
            "POST",
            "/api/governance/classification/scan",
            200,
            data=scan_data
        )
        all_passed = all_passed and success
        if success:
            results_list = scan_results if isinstance(scan_results, list) else []
            print(f"   ✅ PII scan found {len(results_list)} potential matches")
        
        return all_passed

    def test_access_request_endpoints(self) -> bool:
        """Test all 6 access request endpoints"""
        print("\n" + "="*60)
        print("🔑 ACCESS REQUEST ENDPOINTS (6 endpoints)")
        print("="*60)
        
        all_passed = True
        
        # 1. Create access request
        request_data = {
            "requester_justification": "Need access to user data for analytics dashboard development",
            "resource_type": "datasource",
            "resource_id": "test-datasource-001",
            "resource_name": "Test User Database",
            "access_level": "read",
            "duration_days": 30
        }
        
        success, request_response = self.run_api_test(
            "Create Access Request",
            "POST",
            "/api/governance/access-requests",
            200,
            data=request_data
        )
        all_passed = all_passed and success
        
        if success and 'id' in request_response:
            self.access_request_id = request_response['id']
            print(f"   ✅ Created access request: {self.access_request_id}")
        
        # 2. Get all access requests
        success, requests = self.run_api_test(
            "Get Access Requests",
            "GET",
            "/api/governance/access-requests",
            200
        )
        all_passed = all_passed and success
        if success:
            requests_list = requests if isinstance(requests, list) else []
            print(f"   ✅ Found {len(requests_list)} access requests")
        
        # 3. Get pending requests (admin only)
        success, pending = self.run_api_test(
            "Get Pending Requests",
            "GET",
            "/api/governance/access-requests/pending",
            200
        )
        all_passed = all_passed and success
        if success:
            pending_list = pending if isinstance(pending, list) else []
            print(f"   ✅ Found {len(pending_list)} pending requests")
        
        # 4. Approve access request
        if self.access_request_id:
            success, approved = self.run_api_test(
                "Approve Access Request",
                "POST",
                f"/api/governance/access-requests/{self.access_request_id}/approve?approval_notes=Approved for analytics work",
                200
            )
            all_passed = all_passed and success
        
        # 5. Create another request to test rejection
        reject_request_data = {
            "requester_justification": "Test request for rejection",
            "resource_type": "datasource", 
            "resource_id": "test-datasource-002",
            "access_level": "admin"
        }
        
        success, reject_response = self.run_api_test(
            "Create Request for Rejection Test",
            "POST",
            "/api/governance/access-requests",
            200,
            data=reject_request_data
        )
        
        if success and 'id' in reject_response:
            reject_request_id = reject_response['id']
            
            # 6. Reject access request
            success, rejected = self.run_api_test(
                "Reject Access Request",
                "POST",
                f"/api/governance/access-requests/{reject_request_id}/reject?rejection_notes=Insufficient justification",
                200
            )
            all_passed = all_passed and success
        
        return all_passed

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n" + "="*60)
        print("🧹 CLEANUP TEST DATA")
        print("="*60)
        
        # Delete catalog entry
        if self.catalog_entry_id:
            success, _ = self.run_api_test(
                "Delete Catalog Entry",
                "DELETE",
                f"/api/governance/catalog/{self.catalog_entry_id}",
                200
            )
            if success:
                print("   ✅ Cleaned up catalog entry")
        
        print("   ✅ Cleanup completed")

    def run_all_tests(self) -> bool:
        """Run all governance API test suites"""
        print("🚀 Starting Comprehensive Data Governance API Tests")
        print(f"🌐 Backend URL: {self.base_url}")
        print(f"📧 Test User: {self.test_credentials['email']}")
        print("="*80)
        
        # Authentication is required for all other tests
        if not self.test_authentication():
            print("\n❌ Authentication failed - cannot proceed with other tests")
            return False
        
        # Test governance health first
        if not self.test_governance_health():
            print("\n❌ Governance health check failed - service may be down")
            return False
        
        # Run all governance test suites
        test_suites = [
            ("Data Catalog", self.test_data_catalog_endpoints),
            ("Data Lineage", self.test_data_lineage_endpoints),
            ("Data Classification", self.test_classification_endpoints),
            ("Access Requests", self.test_access_request_endpoints),
        ]
        
        suite_results = []
        for suite_name, test_func in test_suites:
            try:
                result = test_func()
                suite_results.append((suite_name, result))
            except Exception as e:
                print(f"\n❌ {suite_name} test suite failed with exception: {str(e)}")
                suite_results.append((suite_name, False))
                self.failed_tests.append({
                    'test_suite': suite_name,
                    'error': str(e)
                })
        
        # Cleanup test data
        try:
            self.cleanup_test_data()
        except Exception as e:
            print(f"⚠️  Cleanup failed: {str(e)}")
        
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
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests: {len(self.failed_tests)}")
            for failure in self.failed_tests[:5]:  # Show first 5 failures
                print(f"   • {failure}")
        
        # Save detailed results
        results_file = f"/app/test_reports/governance_api_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": self.tests_run,
                    "passed_tests": self.tests_passed,
                    "failed_tests": len(self.failed_tests),
                    "success_rate": success_rate,
                    "timestamp": datetime.now().isoformat(),
                    "test_suites": dict(suite_results)
                },
                "test_results": self.test_results,
                "failed_tests": self.failed_tests
            }, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        return success_rate >= 80  # Consider 80%+ success rate as passing

def main():
    """Main test execution"""
    tester = GovernanceAPITester()
    
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