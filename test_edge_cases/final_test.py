#!/usr/bin/env python3
"""
Final comprehensive edge case test
"""

import requests
import json
import time

def test_edge_cases():
    """Test all edge cases comprehensively"""
    print("=== FINAL EDGE CASE TESTING ===")
    
    # Setup
    username = f"finaltest_{int(time.time())}"
    register_data = {"username": username, "email": f"{username}@example.com", "password": "testpass123"}
    
    # Register user
    register_response = requests.post("http://localhost:8000/api/register/", json=register_data)
    if register_response.status_code != 201:
        print(f"❌ Registration failed: {register_response.text}")
        return False
    
    # Login
    login_response = requests.post("http://localhost:8000/api/get-token/", 
                                 json={"username": username, "password": "testpass123"})
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    
    passed_tests = 0
    total_tests = 0
    
    # Test 1: Insufficient Balance
    print("\n1. Testing Insufficient Balance...")
    total_tests += 1
    voucher_data = {"initial_value": 50}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_code = voucher_response.json().get('code')
        payment_data = {"voucher_code": voucher_code, "amount": 100}
        payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
        if payment_response.status_code == 400:
            result = payment_response.json()
            error_msg = result.get('non_field_errors', [''])[0] if result.get('non_field_errors') else ''
            if "Insufficient balance" in error_msg:
                print("   ✅ PASS: Insufficient balance correctly rejected")
                passed_tests += 1
            else:
                print(f"   ❌ FAIL: Wrong error message: '{error_msg}'")
        else:
            print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 2: Invalid Voucher Code
    print("\n2. Testing Invalid Voucher Code...")
    total_tests += 1
    payment_data = {"voucher_code": "INVALID123", "amount": 100}
    payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
    if payment_response.status_code == 400:
        result = payment_response.json()
        error_msg = result.get('voucher_code', [''])[0] if isinstance(result.get('voucher_code'), list) else result.get('voucher_code', '')
        if "Invalid voucher code" in error_msg:
            print("   ✅ PASS: Invalid voucher code correctly rejected")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Wrong error message: '{error_msg}'")
    else:
        print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 3: Disabled Voucher
    print("\n3. Testing Disabled Voucher...")
    total_tests += 1
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_id = voucher_response.json().get('id')
        voucher_code = voucher_response.json().get('code')
        
        # Disable voucher
        disable_response = requests.delete(f"http://localhost:8000/api/vouchers/{voucher_id}/", headers=headers)
        if disable_response.status_code == 200:
            # Try payment with disabled voucher
            payment_data = {"voucher_code": voucher_code, "amount": 100}
            payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
            if payment_response.status_code == 400:
                result = payment_response.json()
                error_msg = result.get('non_field_errors', [''])[0] if result.get('non_field_errors') else ''
                if "disabled" in error_msg.lower() or "sold" in error_msg.lower():
                    print("   ✅ PASS: Disabled voucher correctly rejected")
                    passed_tests += 1
                else:
                    print(f"   ❌ FAIL: Wrong error message: '{error_msg}'")
            else:
                print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 4: Sold Voucher
    print("\n4. Testing Sold Voucher...")
    total_tests += 1
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_id = voucher_response.json().get('id')
        voucher_code = voucher_response.json().get('code')
        
        # Mark as sold
        sold_response = requests.post(f"http://localhost:8000/api/vouchers/{voucher_id}/mark-sold/", headers=headers)
        if sold_response.status_code == 200:
            # Try payment with sold voucher
            payment_data = {"voucher_code": voucher_code, "amount": 100}
            payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
            if payment_response.status_code == 400:
                result = payment_response.json()
                error_msg = result.get('non_field_errors', [''])[0] if result.get('non_field_errors') else ''
                if "disabled" in error_msg.lower() or "sold" in error_msg.lower():
                    print("   ✅ PASS: Sold voucher correctly rejected")
                    passed_tests += 1
                else:
                    print(f"   ❌ FAIL: Wrong error message: '{error_msg}'")
            else:
                print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 5: Negative Amount
    print("\n5. Testing Negative Amount...")
    total_tests += 1
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_code = voucher_response.json().get('code')
        payment_data = {"voucher_code": voucher_code, "amount": -100}
        payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
        if payment_response.status_code == 400:
            print("   ✅ PASS: Negative amount correctly rejected")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 6: Zero Amount
    print("\n6. Testing Zero Amount...")
    total_tests += 1
    payment_data = {"voucher_code": voucher_code, "amount": 0}
    payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
    if payment_response.status_code == 400:
        print("   ✅ PASS: Zero amount correctly rejected")
        passed_tests += 1
    else:
        print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 7: Invalid Recharge Amount
    print("\n7. Testing Invalid Recharge Amount...")
    total_tests += 1
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_code = voucher_response.json().get('code')
        recharge_data = {"amount": 999}  # Invalid amount
        recharge_response = requests.post(f"http://localhost:8000/api/vouchers/{voucher_code}/recharge/", 
                                        json=recharge_data, headers=headers)
        if recharge_response.status_code == 400:
            print("   ✅ PASS: Invalid recharge amount correctly rejected")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Expected 400, got {recharge_response.status_code}")
    
    # Test 8: Duplicate Username
    print("\n8. Testing Duplicate Username...")
    total_tests += 1
    duplicate_data = {"username": username, "email": "different@example.com", "password": "differentpass"}
    duplicate_response = requests.post("http://localhost:8000/api/register/", json=duplicate_data)
    if duplicate_response.status_code == 400:
        result = duplicate_response.json()
        if "already exists" in result.get('error', '').lower():
            print("   ✅ PASS: Duplicate username correctly rejected")
            passed_tests += 1
        else:
            print(f"   ❌ FAIL: Wrong error message: {result.get('error')}")
    else:
        print(f"   ❌ FAIL: Expected 400, got {duplicate_response.status_code}")
    
    # Test 9: Invalid Login
    print("\n9. Testing Invalid Login...")
    total_tests += 1
    invalid_login_response = requests.post("http://localhost:8000/api/get-token/", 
                                        json={"username": "nonexistent", "password": "wrong"})
    if invalid_login_response.status_code == 401:
        print("   ✅ PASS: Invalid login correctly rejected")
        passed_tests += 1
    else:
        print(f"   ❌ FAIL: Expected 401, got {invalid_login_response.status_code}")
    
    # Test 10: Unauthorized Access
    print("\n10. Testing Unauthorized Access...")
    total_tests += 1
    unauthorized_response = requests.get("http://localhost:8000/api/vouchers/")
    if unauthorized_response.status_code == 401:
        print("   ✅ PASS: Unauthorized access correctly rejected")
        passed_tests += 1
    else:
        print(f"   ❌ FAIL: Expected 401, got {unauthorized_response.status_code}")
    
    # Summary
    print(f"\n=== EDGE CASE TEST SUMMARY ===")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL EDGE CASE TESTS PASSED!")
        return True
    else:
        print(f"\n❌ {total_tests - passed_tests} tests failed")
        return False

if __name__ == "__main__":
    test_edge_cases()
