import requests
import sys
import json
from datetime import datetime

class ElectronicsStoreAPITester:
    def __init__(self, base_url="https://smart-picks-12.preview.emergentagent.com/api"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": response.status_code,
                "success": success,
                "response_data": None,
                "error": None
            }

            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    result["response_data"] = response.json()
                except:
                    result["response_data"] = response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    result["error"] = error_data
                    print(f"   Error: {error_data}")
                except:
                    result["error"] = response.text
                    print(f"   Error: {response.text}")

            self.test_results.append(result)
            return success, result["response_data"] if success else {}

        except Exception as e:
            print(f"❌ Failed - Network Error: {str(e)}")
            result = {
                "test_name": name,
                "endpoint": endpoint,
                "method": method,
                "expected_status": expected_status,
                "actual_status": "ERROR",
                "success": False,
                "response_data": None,
                "error": str(e)
            }
            self.test_results.append(result)
            return False, {}

    def test_login(self, username, password):
        """Test login endpoint"""
        success, response = self.run_test(
            f"Login with {username}",
            "POST",
            "auth/login",
            200,
            data={"username": username, "password": password}
        )
        
        if success and 'user_id' in response:
            print(f"   ✓ Login successful for user: {response.get('username')}")
            print(f"   ✓ User ID: {response.get('user_id')}")
            print(f"   ✓ Profile: {response.get('profile', {})}")
            return response.get('user_id'), response
        return None, {}

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        success, response = self.run_test(
            "Login with invalid credentials",
            "POST",
            "auth/login",
            401,
            data={"username": "invalid_user", "password": "wrong_pass"}
        )
        return success

    def test_get_all_products(self):
        """Test get all products endpoint"""
        success, response = self.run_test(
            "Get all products",
            "GET",
            "products",
            200
        )
        
        if success and isinstance(response, list):
            print(f"   ✓ Found {len(response)} products")
            if len(response) > 0:
                print(f"   ✓ Sample product: {response[0].get('name', 'Unknown')}")
            return response
        return []

    def test_get_product_by_id(self, product_id):
        """Test get specific product endpoint"""
        success, response = self.run_test(
            f"Get product by ID: {product_id}",
            "GET",
            f"products/{product_id}",
            200
        )
        
        if success:
            print(f"   ✓ Product name: {response.get('name', 'Unknown')}")
            print(f"   ✓ Brand: {response.get('brand', 'Unknown')}")
            print(f"   ✓ Price: {response.get('price', 0)} RON")
            return response
        return {}

    def test_invalid_product_id(self):
        """Test get product with invalid ID"""
        success, response = self.run_test(
            "Get product with invalid ID",
            "GET",
            "products/invalid-id-123",
            404
        )
        return success

    def test_get_recommendations(self, user_id):
        """Test get recommendations endpoint"""
        success, response = self.run_test(
            f"Get recommendations for user: {user_id}",
            "GET",
            f"recommendations/{user_id}",
            200
        )
        
        if success:
            products = response.get('products', [])
            reason = response.get('reason', '')
            print(f"   ✓ Found {len(products)} recommended products")
            print(f"   ✓ Reason: {reason}")
            if products:
                for i, product in enumerate(products, 1):
                    print(f"   ✓ Recommendation {i}: {product.get('name', 'Unknown')}")
            return response
        return {}

    def test_invalid_user_recommendations(self):
        """Test recommendations with invalid user ID"""
        success, response = self.run_test(
            "Get recommendations for invalid user",
            "GET",
            "recommendations/invalid-user-123",
            404
        )
        return success

    def test_api_root(self):
        """Test API root endpoint"""
        success, response = self.run_test(
            "API Root endpoint",
            "GET",
            "",
            200
        )
        return success, response

def main():
    print("🚀 Starting Electronics Store API Testing")
    print("=" * 60)
    
    tester = ElectronicsStoreAPITester()
    
    # Test API root
    print("\n📍 Testing API Root")
    tester.test_api_root()
    
    # Test login with all hardcoded users
    print("\n🔐 Testing Authentication")
    users_to_test = [
        ("john_tech", "pass123"),
        ("maria_smart", "pass123"),
        ("alex_gamer", "pass123")
    ]
    
    valid_user_ids = []
    for username, password in users_to_test:
        user_id, user_data = tester.test_login(username, password)
        if user_id:
            valid_user_ids.append((user_id, username, user_data))
    
    # Test invalid login
    tester.test_invalid_login()
    
    # Test products endpoints
    print("\n📦 Testing Products")
    products = tester.test_get_all_products()
    
    # Test specific product if products exist
    if products and len(products) > 0:
        # Test first product
        first_product_id = products[0].get('id')
        if first_product_id:
            tester.test_get_product_by_id(first_product_id)
        
        # Test another product if available
        if len(products) > 1:
            second_product_id = products[1].get('id')
            if second_product_id:
                tester.test_get_product_by_id(second_product_id)
    
    # Test invalid product ID
    tester.test_invalid_product_id()
    
    # Test recommendations for valid users
    print("\n🎯 Testing Recommendations")
    for user_id, username, user_data in valid_user_ids:
        tester.test_get_recommendations(user_id)
    
    # Test invalid user recommendations
    tester.test_invalid_user_recommendations()
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests run: {tester.tests_run}")
    print(f"Tests passed: {tester.tests_passed}")
    print(f"Tests failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success rate: {(tester.tests_passed / tester.tests_run * 100):.1f}%")
    
    # Print failed tests
    failed_tests = [test for test in tester.test_results if not test["success"]]
    if failed_tests:
        print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
        for test in failed_tests:
            print(f"   • {test['test_name']}: {test['actual_status']} (expected {test['expected_status']})")
            if test['error']:
                print(f"     Error: {test['error']}")
    
    # Save detailed results to JSON
    results_file = f"/app/test_reports/backend_api_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": tester.tests_run,
                "passed_tests": tester.tests_passed,
                "failed_tests": tester.tests_run - tester.tests_passed,
                "success_rate": tester.tests_passed / tester.tests_run * 100 if tester.tests_run > 0 else 0
            },
            "test_results": tester.test_results
        }, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())