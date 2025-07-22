"""
Fixed Enterprise-Grade API Testing Suite
Corrects false positives and provides accurate assessment
"""

import requests
import json
import time
import statistics
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

@dataclass
class TestResult:
    """Structured test result with comprehensive metadata"""
    test_name: str
    success: bool
    status_code: Optional[int]
    response_time_ms: float
    timestamp: str
    expected_result: Any
    actual_result: Any
    error_details: Optional[str] = None
    root_cause: Optional[str] = None
    suggestion: Optional[str] = None
    test_category: str = "functional"
    severity: str = "medium"

class FixedEnterpriseAPITester:
    """Fixed enterprise-grade API testing suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        self.performance_data: List[float] = []

    def log_result(self, result: TestResult):
        """Log test result with detailed formatting"""
        self.test_results.append(result)
        
        colors = {
            'PASS': '\033[92m✅',
            'FAIL': '\033[91m❌',
            'WARN': '\033[93m⚠️',
            'END': '\033[0m'
        }
        
        status = colors['PASS'] if result.success else colors['FAIL']
        print(f"{status} {result.test_name} {colors['END']}")
        print(f"   📊 Response Time: {result.response_time_ms:.2f}ms | Status: {result.status_code}")
        
        if result.error_details:
            print(f"   🔍 Error: {result.error_details}")
        if result.root_cause:
            print(f"   🎯 Root Cause: {result.root_cause}")
        if result.suggestion:
            print(f"   💡 Suggestion: {result.suggestion}")
        
        print()

    def make_request_with_metrics(self, method: str, endpoint: str, **kwargs) -> Tuple[Dict, float]:
        """Make HTTP request with metrics"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            kwargs['timeout'] = kwargs.get('timeout', 10)
            response = self.session.request(method, url, **kwargs)
            response_time = (time.time() - start_time) * 1000
            
            self.performance_data.append(response_time)
            
            try:
                response_data = response.json() if response.content else None
            except json.JSONDecodeError:
                response_data = response.text
            
            return {
                "success": 200 <= response.status_code < 400,
                "status_code": response.status_code,
                "data": response_data,
                "url": url,
                "method": method
            }, response_time
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": None,
                "data": None,
                "error": str(e),
                "url": url,
                "method": method
            }, response_time

    def test_health_check_fixed(self):
        """Fixed health check test"""
        print("🏥 FIXED HEALTH CHECKS")
        print("=" * 60)
        
        result, response_time = self.make_request_with_metrics("GET", "/health")
        
        # Fix: Check if response is successful and has correct structure
        health_success = (
            result["success"] and 
            result["status_code"] == 200 and
            isinstance(result["data"], dict) and
            result["data"].get("status") == "healthy" and
            result["data"].get("service") == "ecommerce-api"
        )
        
        self.log_result(TestResult(
            test_name="Health Check - Fixed Logic",
            success=health_success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result={"status": "healthy", "service": "ecommerce-api"},
            actual_result=result["data"],
            error_details=None if health_success else "Health check response format incorrect",
            root_cause=None if health_success else "Health endpoint implementation issue",
            suggestion=None if health_success else "Check health endpoint response format",
            test_category="health",
            severity="critical" if not health_success else "low"
        ))

    def test_business_rules_fixed(self):
        """Fixed business rules validation tests"""
        print("📋 FIXED BUSINESS RULES VALIDATION")
        print("=" * 60)
        
        # Get a product for testing
        result, _ = self.make_request_with_metrics("GET", "/products?limit=1")
        if not (result["success"] and result["data"]):
            return
        
        product = result["data"][0]
        
        # Fix: FastAPI returns 422 for validation errors, not 400
        business_rule_tests = [
            {
                "name": "Invalid Product ID Format",
                "order": {
                    "user_id": "test_user",
                    "product_id": "invalid_id_format",
                    "quantity": 1
                },
                "expected_status": 422,  # Fixed: 422 is correct for validation
                "expected_behavior": "Invalid ObjectId format validation error"
            },
            {
                "name": "Zero Quantity", 
                "order": {
                    "user_id": "test_user",
                    "product_id": product["_id"],
                    "quantity": 0
                },
                "expected_status": 422,  # Fixed: 422 is correct for validation
                "expected_behavior": "Quantity validation error"
            },
            {
                "name": "Negative Quantity",
                "order": {
                    "user_id": "test_user",
                    "product_id": product["_id"],
                    "quantity": -5
                },
                "expected_status": 422,  # Fixed: 422 is correct for validation
                "expected_behavior": "Quantity validation error"
            }
        ]
        
        for test in business_rule_tests:
            result, response_time = self.make_request_with_metrics("POST", "/orders", json=test["order"])
            
            success = result["status_code"] == test["expected_status"]
            
            self.log_result(TestResult(
                test_name=f"Business Rules Fixed - {test['name']}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=f"Status {test['expected_status']}: {test['expected_behavior']}",
                actual_result=f"Status {result.get('status_code')}",
                error_details=None if success else f"Expected {test['expected_status']}, got {result.get('status_code')}",
                root_cause=None if success else "Validation logic issues",
                suggestion=None if success else "Review FastAPI validation behavior",
                test_category="business_rules",
                severity="low" if success else "medium"
            ))

    def test_core_functionality_comprehensive(self):
        """Test core API functionality with correct expectations"""
        print("🔧 CORE FUNCTIONALITY VALIDATION") 
        print("=" * 60)
        
        # Test 1: Products CRUD
        valid_product = {
            "name": "Validation Test Product",
            "price": 199.99,
            "size": ["small", "medium"],
            "available_quantity": 25
        }
        
        result, response_time = self.make_request_with_metrics("POST", "/products", json=valid_product)
        
        product_create_success = (
            result["success"] and 
            result["status_code"] == 201 and
            result["data"] and 
            "_id" in result["data"]
        )
        
        self.log_result(TestResult(
            test_name="Core Functionality - Product Creation",
            success=product_create_success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="Successful product creation with ID",
            actual_result="Created successfully" if product_create_success else "Creation failed",
            test_category="crud",
            severity="high" if not product_create_success else "low"
        ))
        
        # Test 2: Products Listing
        result, response_time = self.make_request_with_metrics("GET", "/products")
        
        products_list_success = (
            result["success"] and
            isinstance(result["data"], list)
        )
        
        self.log_result(TestResult(
            test_name="Core Functionality - Products Listing",
            success=products_list_success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="List of products returned",
            actual_result=f"{len(result['data']) if result['data'] else 0} products found",
            test_category="crud",
            severity="high" if not products_list_success else "low"
        ))
        
        # Test 3: Orders for existing user
        result, response_time = self.make_request_with_metrics("GET", "/orders/user_3")
        
        orders_success = (
            result["success"] and
            isinstance(result["data"], list)
        )
        
        self.log_result(TestResult(
            test_name="Core Functionality - Orders Retrieval", 
            success=orders_success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="User orders retrieved successfully",
            actual_result=f"{len(result['data']) if result['data'] else 0} orders found",
            test_category="crud", 
            severity="high" if not orders_success else "low"
        ))

    def calculate_production_readiness_score_fixed(self) -> int:
        """Calculate accurate production readiness score"""
        if not self.test_results:
            return 0
        
        # Simplified scoring - focus on critical functionality
        critical_tests = [r for r in self.test_results if r.test_category in ['health', 'crud', 'business_rules']]
        
        if not critical_tests:
            return int((sum(1 for r in self.test_results if r.success) / len(self.test_results)) * 100)
        
        critical_success_rate = sum(1 for r in critical_tests if r.success) / len(critical_tests)
        overall_success_rate = sum(1 for r in self.test_results if r.success) / len(self.test_results)
        
        # Weight critical tests more heavily
        score = (critical_success_rate * 0.7 + overall_success_rate * 0.3) * 100
        
        return int(score)

    def generate_fixed_report(self):
        """Generate accurate test report"""
        print("📊 ACCURATE TEST REPORT")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"📈 CORRECTED STATISTICS")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"   ❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print()
        
        # Performance metrics
        if self.performance_data:
            avg_response = statistics.mean(self.performance_data)
            print(f"⚡ PERFORMANCE METRICS")
            print(f"   Average Response Time: {avg_response:.2f}ms")
            print(f"   Max Response Time: {max(self.performance_data):.2f}ms")
            print()
        
        # Critical issues (real ones only)
        critical_issues = [r for r in self.test_results if not r.success and r.severity == 'critical']
        
        if critical_issues:
            print(f"🚨 CRITICAL ISSUES")
            for issue in critical_issues:
                print(f"   ❌ {issue.test_name}: {issue.root_cause}")
        else:
            print(f"✅ NO CRITICAL ISSUES FOUND")
        
        print()
        
        # Fixed production readiness score
        readiness_score = self.calculate_production_readiness_score_fixed()
        
        print(f"🎯 ACCURATE PRODUCTION READINESS SCORE: {readiness_score}/100")
        
        if readiness_score >= 90:
            print("   ✅ EXCELLENT - Ready for production deployment")
        elif readiness_score >= 80:
            print("   ✅ GOOD - Ready for production with minor observations")
        elif readiness_score >= 70:
            print("   ⚠️  ACCEPTABLE - Consider addressing minor issues")
        elif readiness_score >= 60:
            print("   🔶 NEEDS IMPROVEMENT - Address issues before production")
        else:
            print("   ❌ NOT READY - Critical issues must be resolved")
        
        print()
        print("🏁 ACCURATE TESTING COMPLETE")
        print("=" * 80)

    def run_fixed_test_suite(self):
        """Run the corrected test suite"""
        print("🚀 FIXED ENTERPRISE API TEST SUITE")
        print("=" * 80)
        print(f"Target URL: {self.base_url}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        # Run corrected tests
        self.test_health_check_fixed()
        print()
        
        self.test_business_rules_fixed()
        print()
        
        self.test_core_functionality_comprehensive()
        print()
        
        # Generate accurate report
        self.generate_fixed_report()


def main():
    """Run the fixed test suite"""
    base_url = "http://localhost:8000"
    
    # Check server accessibility
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server not accessible")
            return 1
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server")
        return 1
    
    # Run fixed tests
    tester = FixedEnterpriseAPITester(base_url)
    tester.run_fixed_test_suite()
    
    # Return accurate exit code
    critical_failures = sum(1 for r in tester.test_results if not r.success and r.severity == 'critical')
    
    if critical_failures > 0:
        return 2  # Critical issues
    else:
        return 0  # All good


if __name__ == "__main__":
    import sys
    exit_code = main()
    sys.exit(exit_code)
