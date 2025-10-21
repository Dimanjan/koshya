#!/usr/bin/env python3
"""
Comprehensive test script for Koshya Voucher System
Tests all user operations and API endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class VoucherSystemTester:
    def __init__(self):
        self.token = None
        self.user = None
        self.test_results = []
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {status}: {message}")
        
    def test_result(self, test_name, success, details=""):
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        self.log(f"{status} - {test_name}: {details}")
        
    def make_request(self, method, endpoint, data=None, headers=None):
        """Make API request with error handling"""
        url = f"{API_BASE}{endpoint}"
        if headers is None:
            headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Token {self.token}"
            
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            return response
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            return None

    def test_server_availability(self):
        """Test if server is running"""
        try:
            response = requests.get(f"{BASE_URL}/", timeout=5)
            self.test_result("Server Availability", response.status_code == 200, 
                           f"Status: {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.test_result("Server Availability", False, f"Error: {e}")
            return False

    def test_user_registration(self):
        """Test user registration"""
        test_username = f"testuser_{int(time.time())}"
        data = {
            "username": test_username,
            "email": f"{test_username}@example.com",
            "password": "testpass123"
        }
        
        response = self.make_request("POST", "/register/", data)
        if response and response.status_code == 201:
            self.test_result("User Registration", True, f"Created user: {test_username}")
            return test_username
        else:
            self.test_result("User Registration", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return None

    def test_user_login(self, username):
        """Test user login"""
        data = {
            "username": username,
            "password": "testpass123"
        }
        
        response = self.make_request("POST", "/get-token/", data)
        if response and response.status_code == 200:
            result = response.json()
            self.token = result.get("token")
            self.user = result.get("user")
            self.test_result("User Login", True, f"Token received for {username}")
            return True
        else:
            self.test_result("User Login", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_statistics(self):
        """Test statistics endpoint"""
        response = self.make_request("GET", "/statistics/")
        if response and response.status_code == 200:
            stats = response.json()
            self.test_result("Get Statistics", True, 
                           f"Total vouchers: {stats.get('total_vouchers', 0)}")
            return True
        else:
            self.test_result("Get Statistics", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_voucher_creation(self):
        """Test voucher creation"""
        data = {"initial_value": 500}
        response = self.make_request("POST", "/vouchers/", data)
        if response and response.status_code == 201:
            voucher = response.json()
            self.test_result("Voucher Creation", True, 
                           f"Created voucher: {voucher.get('code', 'Unknown')}")
            return voucher.get('id')
        else:
            self.test_result("Voucher Creation", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return None

    def test_voucher_listing(self):
        """Test voucher listing"""
        response = self.make_request("GET", "/vouchers/")
        if response and response.status_code == 200:
            vouchers = response.json()
            count = len(vouchers.get('results', vouchers)) if isinstance(vouchers, dict) else len(vouchers)
            self.test_result("Voucher Listing", True, f"Retrieved {count} vouchers")
            return True
        else:
            self.test_result("Voucher Listing", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_voucher_recharge(self, voucher_code):
        """Test voucher recharge"""
        data = {"amount": 200}
        response = self.make_request("POST", f"/vouchers/{voucher_code}/recharge/", data)
        if response and response.status_code == 200:
            result = response.json()
            self.test_result("Voucher Recharge", True, 
                           f"Recharged {voucher_code} with Rs 200")
            return True
        else:
            self.test_result("Voucher Recharge", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_voucher_disable(self, voucher_id):
        """Test voucher disable"""
        response = self.make_request("DELETE", f"/vouchers/{voucher_id}/")
        if response and response.status_code == 200:
            result = response.json()
            self.test_result("Voucher Disable", True, 
                           f"Disabled voucher: {result.get('voucher_code', 'Unknown')}")
            return True
        else:
            self.test_result("Voucher Disable", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_disabled_vouchers(self):
        """Test disabled vouchers listing"""
        response = self.make_request("GET", "/vouchers/disabled/")
        if response and response.status_code == 200:
            vouchers = response.json()
            count = len(vouchers.get('results', vouchers)) if isinstance(vouchers, dict) else len(vouchers)
            self.test_result("Disabled Vouchers", True, f"Retrieved {count} disabled vouchers")
            return True
        else:
            self.test_result("Disabled Vouchers", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_voucher_enable(self, voucher_id):
        """Test voucher enable"""
        response = self.make_request("POST", f"/vouchers/{voucher_id}/enable/")
        if response and response.status_code == 200:
            result = response.json()
            self.test_result("Voucher Enable", True, 
                           f"Enabled voucher: {result.get('voucher_code', 'Unknown')}")
            return True
        else:
            self.test_result("Voucher Enable", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_mark_sold(self, voucher_id):
        """Test mark voucher as sold"""
        response = self.make_request("POST", f"/vouchers/{voucher_id}/mark-sold/")
        if response and response.status_code == 200:
            result = response.json()
            self.test_result("Mark Voucher Sold", True, 
                           f"Marked sold: {result.get('voucher_code', 'Unknown')}")
            return True
        else:
            self.test_result("Mark Voucher Sold", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_sold_vouchers(self):
        """Test sold vouchers listing"""
        response = self.make_request("GET", "/vouchers/sold/")
        if response and response.status_code == 200:
            vouchers = response.json()
            count = len(vouchers.get('results', vouchers)) if isinstance(vouchers, dict) else len(vouchers)
            self.test_result("Sold Vouchers", True, f"Retrieved {count} sold vouchers")
            return True
        else:
            self.test_result("Sold Vouchers", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def test_public_payment(self, voucher_code):
        """Test public payment endpoint"""
        data = {
            "voucher_code": voucher_code,
            "amount": 100
        }
        response = self.make_request("POST", "/pay/", data)
        if response and response.status_code == 200:
            result = response.json()
            self.test_result("Public Payment", True, 
                           f"Payment successful, remaining: Rs {result.get('remaining_balance', 0)}")
            return True
        else:
            self.test_result("Public Payment", False, 
                           f"Status: {response.status_code if response else 'No response'}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        self.log("Starting comprehensive test suite for Koshya Voucher System")
        self.log("=" * 60)
        
        # Test server availability
        if not self.test_server_availability():
            self.log("Server not available, stopping tests", "ERROR")
            return
            
        # Test user operations
        self.log("\n--- Testing User Operations ---")
        username = self.test_user_registration()
        if username:
            self.test_user_login(username)
        
        # Test API operations
        self.log("\n--- Testing API Operations ---")
        self.test_statistics()
        
        # Test voucher operations
        self.log("\n--- Testing Voucher Operations ---")
        voucher_id = self.test_voucher_creation()
        if voucher_id:
            # Get voucher details for further tests
            response = self.make_request("GET", f"/vouchers/{voucher_id}/")
            if response and response.status_code == 200:
                voucher_data = response.json()
                voucher_code = voucher_data.get('code')
                
                # Test voucher operations
                self.test_voucher_recharge(voucher_code)
                self.test_voucher_disable(voucher_id)
                self.test_disabled_vouchers()
                self.test_voucher_enable(voucher_id)
                self.test_mark_sold(voucher_id)
                self.test_sold_vouchers()
                
                # Test public payment (create another voucher for payment)
                payment_voucher_id = self.test_voucher_creation()
                if payment_voucher_id:
                    payment_response = self.make_request("GET", f"/vouchers/{payment_voucher_id}/")
                    if payment_response and payment_response.status_code == 200:
                        payment_voucher_data = payment_response.json()
                        payment_voucher_code = payment_voucher_data.get('code')
                        self.test_public_payment(payment_voucher_code)
        
        self.test_voucher_listing()
        
        # Print summary
        self.log("\n" + "=" * 60)
        self.log("TEST SUMMARY")
        self.log("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        self.log(f"Total Tests: {total_tests}")
        self.log(f"Passed: {passed_tests}")
        self.log(f"Failed: {failed_tests}")
        self.log(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            self.log("\nFailed Tests:")
            for result in self.test_results:
                if not result['success']:
                    self.log(f"  - {result['test']}: {result['details']}")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        self.log(f"\nDetailed results saved to: test_operations/test_results.json")
        return failed_tests == 0

def main():
    """Main test runner"""
    tester = VoucherSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
