"""
Enterprise-Grade API Testing Suite for FastAPI E-commerce Microservice
Comprehensive testing with detailed debugging, performance metrics, and root cause analysis

Purpose: Production-ready API validation with enterprise-level debugging capabilities
"""

import requests
import json
import time
import threading
import statistics
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from collections import defaultdict
import sys

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
    severity: str = "medium"  # low, medium, high, critical

@dataclass
class PerformanceMetrics:
    """Performance metrics for API calls"""
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    p95_response_time: float
    p99_response_time: float
    throughput_rps: float
    success_rate: float

class EnterpriseAPITester:
    """Enterprise-grade API testing suite with comprehensive debugging capabilities"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.test_results: List[TestResult] = []
        self.performance_data: List[float] = []
        self.created_resources: List[Dict] = []  # For cleanup
        
        # Test configuration
        self.timeout = 10  # seconds
        self.max_retries = 3
        self.parallel_requests = 5
        
        # Initialize session with headers
        self.session.headers.update({
            'User-Agent': 'Enterprise-API-Tester/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def log_result(self, result: TestResult):
        """Log test result with detailed formatting"""
        self.test_results.append(result)
        
        # Color coding for terminal output
        colors = {
            'PASS': '\033[92m✅',    # Green
            'FAIL': '\033[91m❌',    # Red
            'WARN': '\033[93m⚠️',    # Yellow
            'INFO': '\033[94mℹ️',    # Blue
            'END': '\033[0m'         # End color
        }
        
        status = colors['PASS'] if result.success else colors['FAIL']
        severity_color = {
            'low': colors['INFO'],
            'medium': colors['WARN'], 
            'high': colors['FAIL'],
            'critical': colors['FAIL']
        }
        
        print(f"{status} {result.test_name} {colors['END']}")
        print(f"   📊 Response Time: {result.response_time_ms:.2f}ms | Status: {result.status_code}")
        
        if result.error_details:
            print(f"   🔍 Error: {result.error_details}")
        
        if result.root_cause:
            print(f"   🎯 Root Cause: {result.root_cause}")
            
        if result.suggestion:
            print(f"   💡 Suggestion: {result.suggestion}")
            
        if result.severity in ['high', 'critical']:
            sev_color = severity_color.get(result.severity, colors['WARN'])
            print(f"   {sev_color}⚡ SEVERITY: {result.severity.upper()} {colors['END']}")
        
        print()

    def make_request_with_metrics(self, method: str, endpoint: str, **kwargs) -> Tuple[Dict, float]:
        """Make HTTP request with comprehensive error handling and metrics"""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            # Add timeout to kwargs
            kwargs['timeout'] = kwargs.get('timeout', self.timeout)
            
            response = self.session.request(method, url, **kwargs)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            self.performance_data.append(response_time)
            
            # Parse response data
            try:
                response_data = response.json() if response.content else None
            except json.JSONDecodeError:
                response_data = response.text
            
            return {
                "success": 200 <= response.status_code < 400,
                "status_code": response.status_code,
                "data": response_data,
                "headers": dict(response.headers),
                "url": url,
                "method": method
            }, response_time
            
        except requests.exceptions.Timeout:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": 408,
                "data": None,
                "error": "Request timeout",
                "url": url,
                "method": method
            }, response_time
            
        except requests.exceptions.ConnectionError:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": None,
                "data": None,
                "error": "Connection error - server may be down",
                "url": url,
                "method": method
            }, response_time
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "status_code": None,
                "data": None,
                "error": f"Unexpected error: {str(e)}",
                "url": url,
                "method": method
            }, response_time

    def test_server_health_comprehensive(self):
        """Comprehensive server health checks"""
        print("🏥 COMPREHENSIVE HEALTH CHECKS")
        print("=" * 60)
        
        # 1. Basic health check
        result, response_time = self.make_request_with_metrics("GET", "/health")
        
        expected_health = {"status": "healthy", "service": "ecommerce-api"}
        success = (result["success"] and 
                  result["data"] == expected_health and 
                  response_time < 1000)  # Under 1 second
        
        self.log_result(TestResult(
            test_name="Health Check - Basic",
            success=success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result=expected_health,
            actual_result=result["data"],
            error_details=result.get("error") if not success else None,
            root_cause="Server not responding correctly" if not success else None,
            suggestion="Check if FastAPI server is running and accessible" if not success else None,
            test_category="health",
            severity="critical" if not success else "low"
        ))
        
        # 2. Health check performance under load
        self._test_health_under_load()
        
        # 3. Database connectivity check
        self._test_database_connectivity()

    def _test_health_under_load(self):
        """Test health endpoint under concurrent load"""
        def health_request():
            result, response_time = self.make_request_with_metrics("GET", "/health")
            return result["success"], response_time
        
        # Run 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(health_request) for _ in range(10)]
            results = [future.result() for future in as_completed(futures)]
        
        success_count = sum(1 for success, _ in results if success)
        avg_response_time = statistics.mean([rt for _, rt in results])
        
        load_test_success = success_count == 10 and avg_response_time < 2000
        
        self.log_result(TestResult(
            test_name="Health Check - Load Test (10 concurrent)",
            success=load_test_success,
            status_code=200 if load_test_success else 500,
            response_time_ms=avg_response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="10/10 successful responses under 2000ms",
            actual_result=f"{success_count}/10 successful, avg {avg_response_time:.2f}ms",
            error_details=f"Only {success_count}/10 requests succeeded" if not load_test_success else None,
            root_cause="Server performance issues under load" if not load_test_success else None,
            suggestion="Check server resources and connection pool settings" if not load_test_success else None,
            test_category="performance",
            severity="high" if not load_test_success else "low"
        ))

    def _test_database_connectivity(self):
        """Test database connectivity indirectly through products endpoint"""
        result, response_time = self.make_request_with_metrics("GET", "/products?limit=1")
        
        db_healthy = result["success"] and isinstance(result["data"], list)
        
        self.log_result(TestResult(
            test_name="Database Connectivity Check",
            success=db_healthy,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="Successful database query response",
            actual_result="Connected" if db_healthy else "Connection failed",
            error_details=result.get("error") if not db_healthy else None,
            root_cause="Database connection or query issues" if not db_healthy else None,
            suggestion="Check MongoDB connection string and network connectivity" if not db_healthy else None,
            test_category="database",
            severity="critical" if not db_healthy else "low"
        ))

    def test_products_api_comprehensive(self):
        """Comprehensive product API testing"""
        print("📦 COMPREHENSIVE PRODUCTS API TESTING")
        print("=" * 60)
        
        # 1. Basic CRUD operations
        self._test_products_crud()
        
        # 2. Advanced filtering and search
        self._test_products_filtering()
        
        # 3. Pagination edge cases
        self._test_products_pagination_edge_cases()
        
        # 4. Performance testing
        self._test_products_performance()
        
        # 5. Data validation
        self._test_products_validation()
        
        # 6. Concurrent operations
        self._test_products_concurrent_operations()

    def _test_products_crud(self):
        """Test basic CRUD operations for products"""
        
        # CREATE - Valid product
        valid_product = {
            "name": "Enterprise Test Product",
            "price": 999.99,
            "size": ["small", "medium", "large"],
            "available_quantity": 100
        }
        
        result, response_time = self.make_request_with_metrics("POST", "/products", json=valid_product)
        
        create_success = (result["success"] and 
                         result["status_code"] == 201 and
                         result["data"] and
                         "_id" in result["data"])
        
        created_product_id = result["data"].get("_id") if create_success else None
        if created_product_id:
            self.created_resources.append({"type": "product", "id": created_product_id})
        
        self.log_result(TestResult(
            test_name="Products CRUD - Create Valid Product",
            success=create_success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="201 status with product ID",
            actual_result=result["data"],
            error_details=result.get("error") if not create_success else None,
            root_cause="Product creation endpoint issues" if not create_success else None,
            suggestion="Check product schema validation and database write permissions" if not create_success else None,
            test_category="crud",
            severity="high" if not create_success else "low"
        ))
        
        # CREATE - Invalid product (multiple validation errors)
        invalid_product = {
            "name": "",  # Empty name
            "price": -100,  # Negative price
            "size": [],  # Empty size array
            "available_quantity": -10  # Negative quantity
        }
        
        result, response_time = self.make_request_with_metrics("POST", "/products", json=invalid_product)
        
        validation_success = (not result["success"] and 
                            result["status_code"] == 400)
        
        self.log_result(TestResult(
            test_name="Products CRUD - Create Invalid Product (Validation)",
            success=validation_success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="400 status with validation errors",
            actual_result=result["data"],
            error_details="Expected validation error" if not validation_success else None,
            root_cause="Input validation not working correctly" if not validation_success else None,
            suggestion="Check Pydantic validation rules and error handling" if not validation_success else None,
            test_category="validation",
            severity="medium" if not validation_success else "low"
        ))

    def _test_products_filtering(self):
        """Test advanced filtering capabilities"""
        
        test_cases = [
            {
                "name": "Filter by Name - Exact Match",
                "params": {"name": "Gaming Laptop"},
                "expected_behavior": "Return products with 'Gaming Laptop' in name"
            },
            {
                "name": "Filter by Name - Partial Match", 
                "params": {"name": "laptop"},
                "expected_behavior": "Return products containing 'laptop' (case-insensitive)"
            },
            {
                "name": "Filter by Size",
                "params": {"size": "large"},
                "expected_behavior": "Return products with 'large' size option"
            },
            {
                "name": "Combined Filters",
                "params": {"name": "gaming", "size": "large"},
                "expected_behavior": "Return products matching both name and size criteria"
            },
            {
                "name": "Non-existent Filter",
                "params": {"name": "NonExistentProduct12345"},
                "expected_behavior": "Return empty array"
            }
        ]
        
        for test_case in test_cases:
            result, response_time = self.make_request_with_metrics("GET", "/products", params=test_case["params"])
            
            success = (result["success"] and 
                      isinstance(result["data"], list))
            
            # Additional validation based on test case
            if test_case["name"] == "Non-existent Filter":
                success = success and len(result["data"]) == 0
            
            self.log_result(TestResult(
                test_name=f"Products Filtering - {test_case['name']}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=test_case["expected_behavior"],
                actual_result=f"Returned {len(result['data']) if result['data'] else 0} products",
                error_details=result.get("error") if not success else None,
                root_cause="Filtering logic issues" if not success else None,
                suggestion="Check MongoDB query construction and regex patterns" if not success else None,
                test_category="filtering",
                severity="medium" if not success else "low"
            ))

    def _test_products_pagination_edge_cases(self):
        """Test pagination edge cases and boundary conditions"""
        
        edge_cases = [
            {"params": {"limit": 0}, "expected_status": 422, "test": "Zero Limit"},
            {"params": {"limit": -1}, "expected_status": 422, "test": "Negative Limit"},
            {"params": {"limit": 101}, "expected_status": 422, "test": "Limit Too High"},
            {"params": {"offset": -1}, "expected_status": 422, "test": "Negative Offset"},
            {"params": {"limit": 5, "offset": 0}, "expected_status": 200, "test": "Valid Pagination"},
            {"params": {"limit": 1, "offset": 99999}, "expected_status": 200, "test": "High Offset"},
        ]
        
        for case in edge_cases:
            result, response_time = self.make_request_with_metrics("GET", "/products", params=case["params"])
            
            if case["expected_status"] == 200:
                success = result["success"] and isinstance(result["data"], list)
            else:
                success = result["status_code"] == case["expected_status"]
            
            self.log_result(TestResult(
                test_name=f"Products Pagination - {case['test']}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=f"Status {case['expected_status']}",
                actual_result=f"Status {result.get('status_code')}",
                error_details=result.get("error") if not success else None,
                root_cause="Pagination validation issues" if not success else None,
                suggestion="Check FastAPI Query parameter validation" if not success else None,
                test_category="pagination",
                severity="medium" if not success else "low"
            ))

    def _test_products_performance(self):
        """Test product API performance under various loads"""
        
        # Test response time for large result sets
        result, response_time = self.make_request_with_metrics("GET", "/products?limit=100")
        
        performance_acceptable = response_time < 3000  # Under 3 seconds for 100 products
        
        self.log_result(TestResult(
            test_name="Products Performance - Large Result Set",
            success=performance_acceptable and result["success"],
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="Response under 3000ms",
            actual_result=f"Response in {response_time:.2f}ms",
            error_details="Response time too slow" if not performance_acceptable else None,
            root_cause="Database query optimization needed" if not performance_acceptable else None,
            suggestion="Check database indexes and query optimization" if not performance_acceptable else None,
            test_category="performance",
            severity="medium" if not performance_acceptable else "low"
        ))

    def _test_products_validation(self):
        """Test comprehensive input validation"""
        
        validation_tests = [
            {
                "name": "SQL Injection Attempt",
                "params": {"name": "'; DROP TABLE products; --"},
                "expected": "Safe handling of malicious input"
            },
            {
                "name": "XSS Attempt",
                "params": {"name": "<script>alert('xss')</script>"},
                "expected": "Safe handling of script tags"
            },
            {
                "name": "Unicode Edge Cases",
                "params": {"name": "测试产品🎉"},
                "expected": "Proper unicode handling"
            },
            {
                "name": "Very Long Name",
                "params": {"name": "A" * 1000},
                "expected": "Proper handling of long strings"
            }
        ]
        
        for test in validation_tests:
            result, response_time = self.make_request_with_metrics("GET", "/products", params=test["params"])
            
            # Should not crash the server
            success = result["status_code"] != 500
            
            self.log_result(TestResult(
                test_name=f"Products Security - {test['name']}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=test["expected"],
                actual_result="Handled safely" if success else "Server error",
                error_details=result.get("error") if not success else None,
                root_cause="Input sanitization issues" if not success else None,
                suggestion="Implement proper input validation and sanitization" if not success else None,
                test_category="security",
                severity="high" if not success else "low"
            ))

    def _test_products_concurrent_operations(self):
        """Test concurrent product operations"""
        
        def create_product(index):
            product_data = {
                "name": f"Concurrent Test Product {index}",
                "price": 99.99 + index,
                "size": ["medium"],
                "available_quantity": 50
            }
            result, response_time = self.make_request_with_metrics("POST", "/products", json=product_data)
            return result["success"], response_time, result.get("data", {}).get("_id")
        
        # Create 5 products concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_product, i) for i in range(5)]
            results = [future.result() for future in as_completed(futures)]
        
        success_count = sum(1 for success, _, _ in results if success)
        avg_response_time = statistics.mean([rt for _, rt, _ in results])
        created_ids = [pid for _, _, pid in results if pid]
        
        # Add created products to cleanup list
        for product_id in created_ids:
            self.created_resources.append({"type": "product", "id": product_id})
        
        concurrent_success = success_count >= 4  # Allow for 1 failure due to race conditions
        
        self.log_result(TestResult(
            test_name="Products Concurrency - Parallel Creation",
            success=concurrent_success,
            status_code=201 if concurrent_success else 500,
            response_time_ms=avg_response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="4+ successful concurrent creations",
            actual_result=f"{success_count}/5 successful creations",
            error_details=f"Only {success_count}/5 succeeded" if not concurrent_success else None,
            root_cause="Database concurrency issues" if not concurrent_success else None,
            suggestion="Check database connection pooling and transaction handling" if not concurrent_success else None,
            test_category="concurrency",
            severity="medium" if not concurrent_success else "low"
        ))

    def test_orders_api_comprehensive(self):
        """Comprehensive order API testing"""
        print("🛒 COMPREHENSIVE ORDERS API TESTING")
        print("=" * 60)
        
        # 1. Order lifecycle testing
        self._test_orders_lifecycle()
        
        # 2. Order validation and business rules
        self._test_orders_business_rules()
        
        # 3. Order pagination and filtering
        self._test_orders_pagination()
        
        # 4. Order performance testing
        self._test_orders_performance()
        
        # 5. Order data integrity
        self._test_orders_data_integrity()

    def _test_orders_lifecycle(self):
        """Test complete order lifecycle"""
        
        # First, ensure we have a product to order
        result, _ = self.make_request_with_metrics("GET", "/products?limit=1")
        
        if not (result["success"] and result["data"]):
            self.log_result(TestResult(
                test_name="Orders Lifecycle - Prerequisites",
                success=False,
                status_code=result.get("status_code"),
                response_time_ms=0,
                timestamp=datetime.now().isoformat(),
                expected_result="At least one product available",
                actual_result="No products found",
                error_details="Cannot test orders without products",
                root_cause="No products in database",
                suggestion="Seed database with test products first",
                test_category="prerequisites",
                severity="critical"
            ))
            return
        
        product = result["data"][0]
        product_id = product["_id"]
        
        # Test valid order creation
        valid_order = {
            "user_id": "enterprise_test_user",
            "product_id": product_id,
            "quantity": 1
        }
        
        result, response_time = self.make_request_with_metrics("POST", "/orders", json=valid_order)
        
        order_success = (result["success"] and 
                        result["status_code"] == 201 and
                        result["data"] and
                        "_id" in result["data"])
        
        if order_success:
            order_id = result["data"]["_id"]
            self.created_resources.append({"type": "order", "id": order_id, "user_id": "enterprise_test_user"})
        
        self.log_result(TestResult(
            test_name="Orders Lifecycle - Create Valid Order",
            success=order_success,
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="201 status with order ID",
            actual_result=result["data"],
            error_details=result.get("error") if not order_success else None,
            root_cause="Order creation endpoint issues" if not order_success else None,
            suggestion="Check order schema validation and product availability" if not order_success else None,
            test_category="crud",
            severity="high" if not order_success else "low"
        ))

    def _test_orders_business_rules(self):
        """Test order business rules and validation"""
        
        # Get a product for testing
        result, _ = self.make_request_with_metrics("GET", "/products?limit=1")
        if not (result["success"] and result["data"]):
            return
        
        product = result["data"][0]
        
        business_rule_tests = [
            {
                "name": "Invalid Product ID",
                "order": {
                    "user_id": "test_user",
                    "product_id": "507f1f77bcf86cd799439011",  # Valid ObjectId format but doesn't exist
                    "quantity": 1
                },
                "expected_status": 404,
                "expected_behavior": "Product not found error"
            },
            {
                "name": "Invalid Product ID Format",
                "order": {
                    "user_id": "test_user",
                    "product_id": "invalid_id_format",
                    "quantity": 1
                },
                "expected_status": 400,
                "expected_behavior": "Invalid ObjectId format error"
            },
            {
                "name": "Zero Quantity",
                "order": {
                    "user_id": "test_user",
                    "product_id": product["_id"],
                    "quantity": 0
                },
                "expected_status": 400,
                "expected_behavior": "Quantity must be positive"
            },
            {
                "name": "Negative Quantity",
                "order": {
                    "user_id": "test_user",
                    "product_id": product["_id"],
                    "quantity": -5
                },
                "expected_status": 400,
                "expected_behavior": "Quantity must be positive"
            },
            {
                "name": "Excessive Quantity",
                "order": {
                    "user_id": "test_user",
                    "product_id": product["_id"],
                    "quantity": product["available_quantity"] + 100
                },
                "expected_status": 400,
                "expected_behavior": "Insufficient quantity available"
            }
        ]
        
        for test in business_rule_tests:
            result, response_time = self.make_request_with_metrics("POST", "/orders", json=test["order"])
            
            success = result["status_code"] == test["expected_status"]
            
            self.log_result(TestResult(
                test_name=f"Orders Business Rules - {test['name']}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=f"Status {test['expected_status']}: {test['expected_behavior']}",
                actual_result=result["data"],
                error_details=f"Expected {test['expected_status']}, got {result.get('status_code')}" if not success else None,
                root_cause="Business rule validation issues" if not success else None,
                suggestion="Check order validation logic and error handling" if not success else None,
                test_category="business_rules",
                severity="medium" if not success else "low"
            ))

    def _test_orders_pagination(self):
        """Test order pagination and user filtering"""
        
        # Test retrieving orders for existing users
        user_tests = ["user_1", "user_2", "user_3", "nonexistent_user"]
        
        for user_id in user_tests:
            result, response_time = self.make_request_with_metrics("GET", f"/orders/{user_id}")
            
            success = result["success"] and isinstance(result["data"], list)
            
            expected_result = "Empty list for nonexistent user" if user_id == "nonexistent_user" else "List of orders"
            
            self.log_result(TestResult(
                test_name=f"Orders Pagination - Get Orders for {user_id}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=expected_result,
                actual_result=f"Retrieved {len(result['data']) if result['data'] else 0} orders",
                error_details=result.get("error") if not success else None,
                root_cause="Order retrieval issues" if not success else None,
                suggestion="Check user order filtering logic" if not success else None,
                test_category="retrieval",
                severity="medium" if not success else "low"
            ))
        
        # Test pagination parameters
        if user_tests:
            user_id = user_tests[0]  # Use first user
            
            pagination_tests = [
                {"params": {"limit": 2, "offset": 0}, "test": "Valid Pagination"},
                {"params": {"limit": -1}, "expected_status": 422, "test": "Negative Limit"},
                {"params": {"limit": 101}, "expected_status": 422, "test": "Limit Too High"},
                {"params": {"offset": -1}, "expected_status": 422, "test": "Negative Offset"},
            ]
            
            for test in pagination_tests:
                result, response_time = self.make_request_with_metrics("GET", f"/orders/{user_id}", params=test["params"])
                
                expected_status = test.get("expected_status", 200)
                success = result["status_code"] == expected_status
                
                self.log_result(TestResult(
                    test_name=f"Orders Pagination - {test['test']}",
                    success=success,
                    status_code=result.get("status_code"),
                    response_time_ms=response_time,
                    timestamp=datetime.now().isoformat(),
                    expected_result=f"Status {expected_status}",
                    actual_result=f"Status {result.get('status_code')}",
                    error_details=result.get("error") if not success else None,
                    root_cause="Order pagination validation issues" if not success else None,
                    suggestion="Check FastAPI parameter validation for orders" if not success else None,
                    test_category="pagination",
                    severity="medium" if not success else "low"
                ))

    def _test_orders_performance(self):
        """Test order API performance"""
        
        # Test retrieving large number of orders
        result, response_time = self.make_request_with_metrics("GET", "/orders/user_1?limit=50")
        
        performance_acceptable = response_time < 2000  # Under 2 seconds
        
        self.log_result(TestResult(
            test_name="Orders Performance - Large Result Set",
            success=performance_acceptable and result["success"],
            status_code=result.get("status_code"),
            response_time_ms=response_time,
            timestamp=datetime.now().isoformat(),
            expected_result="Response under 2000ms",
            actual_result=f"Response in {response_time:.2f}ms",
            error_details="Response time too slow" if not performance_acceptable else None,
            root_cause="Order query optimization needed" if not performance_acceptable else None,
            suggestion="Check database indexes on user_id and created_at fields" if not performance_acceptable else None,
            test_category="performance",
            severity="medium" if not performance_acceptable else "low"
        ))

    def _test_orders_data_integrity(self):
        """Test order data integrity and relationships"""
        
        # Create an order and verify all fields are present and correct
        result, _ = self.make_request_with_metrics("GET", "/products?limit=1")
        if not (result["success"] and result["data"]):
            return
        
        product = result["data"][0]
        
        test_order = {
            "user_id": "data_integrity_test_user",
            "product_id": product["_id"],
            "quantity": 2
        }
        
        result, response_time = self.make_request_with_metrics("POST", "/orders", json=test_order)
        
        if result["success"] and result["data"]:
            order_data = result["data"]
            
            # Verify all required fields are present
            required_fields = ["_id", "user_id", "product_id", "quantity", "created_at"]
            missing_fields = [field for field in required_fields if field not in order_data]
            
            # Verify data types and values
            integrity_checks = [
                order_data.get("user_id") == test_order["user_id"],
                order_data.get("product_id") == test_order["product_id"],
                order_data.get("quantity") == test_order["quantity"],
                isinstance(order_data.get("created_at"), str),  # Should be ISO datetime string
                len(missing_fields) == 0
            ]
            
            data_integrity_success = all(integrity_checks)
            
            if order_data.get("_id"):
                self.created_resources.append({
                    "type": "order", 
                    "id": order_data["_id"], 
                    "user_id": "data_integrity_test_user"
                })
            
            self.log_result(TestResult(
                test_name="Orders Data Integrity - Field Completeness",
                success=data_integrity_success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result="All required fields present with correct values",
                actual_result=f"Missing fields: {missing_fields}" if missing_fields else "All fields present",
                error_details=f"Missing fields: {missing_fields}" if missing_fields else None,
                root_cause="Order response schema issues" if not data_integrity_success else None,
                suggestion="Check OrderOut schema definition and serialization" if not data_integrity_success else None,
                test_category="data_integrity",
                severity="medium" if not data_integrity_success else "low"
            ))

    def test_api_documentation_and_metadata(self):
        """Test API documentation and metadata endpoints"""
        print("📚 API DOCUMENTATION & METADATA TESTING")
        print("=" * 60)
        
        doc_endpoints = [
            {"endpoint": "/docs", "name": "Swagger UI", "content_type": "text/html"},
            {"endpoint": "/redoc", "name": "ReDoc", "content_type": "text/html"},
            {"endpoint": "/openapi.json", "name": "OpenAPI Spec", "content_type": "application/json"},
        ]
        
        for doc in doc_endpoints:
            result, response_time = self.make_request_with_metrics("GET", doc["endpoint"])
            
            # For HTML endpoints, check if we get HTML content
            # For JSON endpoint, check if we get valid JSON
            if doc["content_type"] == "text/html":
                success = (result["success"] and 
                          result["status_code"] == 200 and
                          isinstance(result["data"], str))
            else:
                success = (result["success"] and 
                          result["status_code"] == 200 and
                          isinstance(result["data"], dict))
            
            self.log_result(TestResult(
                test_name=f"API Documentation - {doc['name']}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=f"Accessible {doc['name']} documentation",
                actual_result="Documentation accessible" if success else "Documentation not accessible",
                error_details=result.get("error") if not success else None,
                root_cause="Documentation generation issues" if not success else None,
                suggestion="Check FastAPI documentation configuration" if not success else None,
                test_category="documentation",
                severity="low" if not success else "low"
            ))

    def test_error_handling_and_edge_cases(self):
        """Test comprehensive error handling and edge cases"""
        print("⚠️  ERROR HANDLING & EDGE CASES TESTING")
        print("=" * 60)
        
        error_scenarios = [
            {
                "name": "Non-existent Endpoint",
                "request": ("GET", "/api/v1/nonexistent"),
                "expected_status": 404,
                "description": "Should return 404 for non-existent endpoints"
            },
            {
                "name": "Malformed JSON",
                "request": ("POST", "/products"),
                "data": '{"invalid": json}',  # Malformed JSON
                "headers": {"Content-Type": "application/json"},
                "expected_status": 422,
                "description": "Should handle malformed JSON gracefully"
            },
            {
                "name": "Wrong Content-Type",
                "request": ("POST", "/products"),
                "data": "not json data",
                "headers": {"Content-Type": "text/plain"},
                "expected_status": 422,
                "description": "Should reject non-JSON content for JSON endpoints"
            },
            {
                "name": "Empty Request Body",
                "request": ("POST", "/products"),
                "data": "",
                "headers": {"Content-Type": "application/json"},
                "expected_status": 422,
                "description": "Should handle empty request body"
            }
        ]
        
        for scenario in error_scenarios:
            method, endpoint = scenario["request"]
            
            kwargs = {}
            if "data" in scenario:
                kwargs["data"] = scenario["data"]
            if "headers" in scenario:
                kwargs["headers"] = scenario["headers"]
            
            result, response_time = self.make_request_with_metrics(method, endpoint, **kwargs)
            
            expected_status = scenario["expected_status"]
            success = result["status_code"] == expected_status
            
            self.log_result(TestResult(
                test_name=f"Error Handling - {scenario['name']}",
                success=success,
                status_code=result.get("status_code"),
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat(),
                expected_result=f"Status {expected_status}: {scenario['description']}",
                actual_result=f"Status {result.get('status_code')}",
                error_details=f"Expected {expected_status}, got {result.get('status_code')}" if not success else None,
                root_cause="Error handling not implemented correctly" if not success else None,
                suggestion="Check FastAPI error handlers and middleware" if not success else None,
                test_category="error_handling",
                severity="medium" if not success else "low"
            ))

    def calculate_performance_metrics(self) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""
        if not self.performance_data:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0)
        
        response_times = self.performance_data
        response_times.sort()
        
        n = len(response_times)
        
        return PerformanceMetrics(
            avg_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            p95_response_time=response_times[int(0.95 * n)] if n > 0 else 0,
            p99_response_time=response_times[int(0.99 * n)] if n > 0 else 0,
            throughput_rps=n / (max(response_times) / 1000) if response_times else 0,
            success_rate=(sum(1 for r in self.test_results if r.success) / len(self.test_results) * 100) if self.test_results else 0
        )

    def cleanup_test_resources(self):
        """Clean up resources created during testing"""
        print("🧹 CLEANING UP TEST RESOURCES")
        print("=" * 60)
        
        cleanup_count = 0
        
        # Note: In a production system, you would implement DELETE endpoints
        # For now, we'll just report what would be cleaned up
        for resource in self.created_resources:
            print(f"   Would clean up {resource['type']}: {resource['id']}")
            cleanup_count += 1
        
        print(f"   Total resources to cleanup: {cleanup_count}")
        print()

    def generate_comprehensive_report(self):
        """Generate comprehensive test report with insights and recommendations"""
        
        print("📊 COMPREHENSIVE TEST REPORT")
        print("=" * 80)
        
        # Overall statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.success)
        failed_tests = total_tests - passed_tests
        
        print(f"📈 OVERALL STATISTICS")
        print(f"   Total Tests Executed: {total_tests}")
        print(f"   ✅ Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
        print(f"   ❌ Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        print()
        
        # Performance metrics
        perf_metrics = self.calculate_performance_metrics()
        print(f"⚡ PERFORMANCE METRICS")
        print(f"   Average Response Time: {perf_metrics.avg_response_time:.2f}ms")
        print(f"   95th Percentile: {perf_metrics.p95_response_time:.2f}ms")
        print(f"   99th Percentile: {perf_metrics.p99_response_time:.2f}ms")
        print(f"   Min/Max Response Time: {perf_metrics.min_response_time:.2f}ms / {perf_metrics.max_response_time:.2f}ms")
        print(f"   Success Rate: {perf_metrics.success_rate:.1f}%")
        print()
        
        # Test categories breakdown
        categories = defaultdict(list)
        for result in self.test_results:
            categories[result.test_category].append(result)
        
        print(f"📋 RESULTS BY CATEGORY")
        for category, results in categories.items():
            passed = sum(1 for r in results if r.success)
            total = len(results)
            print(f"   {category.upper()}: {passed}/{total} passed ({passed/total*100:.1f}%)")
        print()
        
        # Critical and high severity failures
        critical_failures = [r for r in self.test_results if not r.success and r.severity in ['critical', 'high']]
        
        if critical_failures:
            print(f"🚨 CRITICAL/HIGH SEVERITY ISSUES")
            for failure in critical_failures:
                print(f"   ❌ {failure.test_name}")
                print(f"      Root Cause: {failure.root_cause}")
                print(f"      Suggestion: {failure.suggestion}")
                print(f"      Severity: {failure.severity.upper()}")
                print()
        
        # Recommendations based on test results
        print(f"💡 RECOMMENDATIONS")
        
        if perf_metrics.avg_response_time > 1000:
            print("   🔧 Performance: Consider optimizing database queries and adding caching")
        
        if perf_metrics.success_rate < 95:
            print("   🔧 Reliability: Address failing test cases to improve overall stability")
        
        if failed_tests > 0:
            print("   🔧 Quality: Review and fix failing tests before production deployment")
        
        # Database-specific recommendations
        db_tests = [r for r in self.test_results if r.test_category in ['database', 'crud']]
        db_failures = [r for r in db_tests if not r.success]
        
        if db_failures:
            print("   🔧 Database: Review MongoDB connection settings and query optimization")
        
        # Security recommendations
        security_tests = [r for r in self.test_results if r.test_category == 'security']
        security_failures = [r for r in security_tests if not r.success]
        
        if security_failures:
            print("   🔧 Security: Implement proper input validation and sanitization")
        
        print()
        
        # Production readiness assessment
        readiness_score = self._calculate_production_readiness_score()
        
        print(f"🎯 PRODUCTION READINESS SCORE: {readiness_score}/100")
        
        if readiness_score >= 90:
            print("   ✅ READY FOR PRODUCTION - All critical systems functioning well")
        elif readiness_score >= 75:
            print("   ⚠️  MOSTLY READY - Address minor issues before production deployment")
        elif readiness_score >= 50:
            print("   🔶 NEEDS WORK - Several issues must be resolved before production")
        else:
            print("   ❌ NOT READY - Critical issues must be resolved")
        
        print()
        print("🏁 TESTING COMPLETE")
        print("=" * 80)

    def _calculate_production_readiness_score(self) -> int:
        """Calculate production readiness score based on test results"""
        if not self.test_results:
            return 0
        
        # Weight different categories differently
        category_weights = {
            'health': 0.25,      # Health checks are critical
            'crud': 0.20,        # Core functionality
            'database': 0.15,    # Database connectivity
            'security': 0.15,    # Security is important
            'performance': 0.10, # Performance matters
            'error_handling': 0.10,  # Error handling
            'business_rules': 0.05   # Business logic
        }
        
        total_score = 0
        total_weight = 0
        
        for category, weight in category_weights.items():
            category_tests = [r for r in self.test_results if r.test_category == category]
            if category_tests:
                category_success_rate = sum(1 for r in category_tests if r.success) / len(category_tests)
                total_score += category_success_rate * weight
                total_weight += weight
        
        # Add remaining categories with lower weight
        other_tests = [r for r in self.test_results if r.test_category not in category_weights]
        if other_tests:
            remaining_weight = 1 - total_weight
            other_success_rate = sum(1 for r in other_tests if r.success) / len(other_tests)
            total_score += other_success_rate * remaining_weight
        
        return int(total_score * 100)

    def save_detailed_report(self, filename: str = "enterprise_test_report.json"):
        """Save detailed test report to JSON file"""
        
        report_data = {
            "metadata": {
                "test_suite": "Enterprise FastAPI E-commerce API Test Suite",
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "total_tests": len(self.test_results),
                "duration_seconds": sum(r.response_time_ms for r in self.test_results) / 1000
            },
            "summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.success),
                "failed": sum(1 for r in self.test_results if not r.success),
                "success_rate": (sum(1 for r in self.test_results if r.success) / len(self.test_results) * 100) if self.test_results else 0,
                "production_readiness_score": self._calculate_production_readiness_score()
            },
            "performance_metrics": asdict(self.calculate_performance_metrics()),
            "test_results": [asdict(result) for result in self.test_results],
            "categories": {
                category: {
                    "total": len([r for r in self.test_results if r.test_category == category]),
                    "passed": len([r for r in self.test_results if r.test_category == category and r.success]),
                    "failed": len([r for r in self.test_results if r.test_category == category and not r.success])
                }
                for category in set(r.test_category for r in self.test_results)
            },
            "critical_issues": [
                asdict(r) for r in self.test_results 
                if not r.success and r.severity in ['critical', 'high']
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {filename}")

    def run_comprehensive_test_suite(self):
        """Run the complete enterprise test suite"""
        
        print("🚀 ENTERPRISE API TEST SUITE")
        print("=" * 80)
        print(f"Target URL: {self.base_url}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
        try:
            # 1. Health and infrastructure checks
            self.test_server_health_comprehensive()
            print()
            
            # 2. Products API comprehensive testing
            self.test_products_api_comprehensive()
            print()
            
            # 3. Orders API comprehensive testing  
            self.test_orders_api_comprehensive()
            print()
            
            # 4. API documentation and metadata
            self.test_api_documentation_and_metadata()
            print()
            
            # 5. Error handling and edge cases
            self.test_error_handling_and_edge_cases()
            print()
            
            # 6. Cleanup test resources
            self.cleanup_test_resources()
            
        except KeyboardInterrupt:
            print("\n⚠️  Test suite interrupted by user")
        except Exception as e:
            print(f"\n❌ Unexpected error in test suite: {str(e)}")
            traceback.print_exc()
        
        finally:
            # 7. Generate comprehensive report
            self.generate_comprehensive_report()
            
            # 8. Save detailed report
            self.save_detailed_report()


def main():
    """Main function to run comprehensive API testing"""
    
    # Configuration - easily changeable for different environments
    TEST_CONFIGS = {
        "local": "http://localhost:8000",
        "staging": "https://your-staging-url.com",
        "production": "https://your-production-url.com"
    }
    
    # Default to local testing
    environment = "local"
    base_url = TEST_CONFIGS.get(environment, "http://localhost:8000")
    
    # Initialize the enterprise tester
    tester = EnterpriseAPITester(base_url)
    
    # Check if server is accessible before running tests
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server health check failed. Ensure your FastAPI server is running.")
            print(f"   Response: {response.status_code} - {response.text}")
            return 1
            
    except requests.exceptions.RequestException as e:
        print("❌ Cannot connect to server. Please ensure your FastAPI server is running.")
        print(f"   URL: {base_url}")
        print(f"   Error: {str(e)}")
        return 1
    
    # Run the comprehensive test suite
    tester.run_comprehensive_test_suite()
    
    # Return appropriate exit code based on test results
    failed_tests = sum(1 for r in tester.test_results if not r.success)
    critical_failures = sum(1 for r in tester.test_results if not r.success and r.severity == 'critical')
    
    if critical_failures > 0:
        print(f"\n❌ CRITICAL FAILURES DETECTED: {critical_failures}")
        return 2  # Critical failure exit code
    elif failed_tests > 0:
        print(f"\n⚠️  Some tests failed: {failed_tests}")
        return 1  # General failure exit code
    else:
        print("\n✅ ALL TESTS PASSED")
        return 0  # Success exit code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
