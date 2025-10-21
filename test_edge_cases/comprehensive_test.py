#!/usr/bin/env python3
"""
Comprehensive edge case test with detailed debugging
"""

import requests
import json
import time

def test_all_edge_cases():
    """Test all edge cases with detailed debugging"""
    print("=== COMPREHENSIVE EDGE CASE TESTING ===")
    
    # Setup
    username = f"comptest_{int(time.time())}"
    register_data = {
        "username": username,
        "email": f"{username}@example.com",
        "password": "testpass123"
    }
    
    print(f"1. Registering user: {username}")
    register_response = requests.post("http://localhost:8000/api/register/", json=register_data)
    print(f"   Status: {register_response.status_code}")
    
    if register_response.status_code != 201:
        print(f"   ❌ Registration failed: {register_response.text}")
        return False
    
    print("2. Logging in...")
    login_response = requests.post("http://localhost:8000/api/get-token/", 
                                 json={"username": username, "password": "testpass123"})
    print(f"   Status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"   ❌ Login failed: {login_response.text}")
        return False
    
    token = login_response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    
    print("\n=== TESTING PAYMENT EDGE CASES ===")
    
    # Test 1: Insufficient Balance
    print("\n3. Testing Insufficient Balance...")
    voucher_data = {"initial_value": 50}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_code = voucher_response.json().get('code')
        payment_data = {"voucher_code": voucher_code, "amount": 100}
        payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
        print(f"   Payment status: {payment_response.status_code}")
        if payment_response.status_code == 400:
            result = payment_response.json()
            # Extract error message from different possible locations
            error_msg = ''
            if result.get('error'):
                error_msg = result.get('error')
            elif result.get('non_field_errors'):
                error_msg = result.get('non_field_errors')[0]
            elif result.get('amount'):
                if isinstance(result.get('amount'), list):
                    error_msg = result.get('amount')[0]
                else:
                    error_msg = result.get('amount')
            elif result.get('voucher_code'):
                if isinstance(result.get('voucher_code'), list):
                    error_msg = result.get('voucher_code')[0]
                else:
                    error_msg = result.get('voucher_code')
            if "Insufficient balance" in error_msg:
                print("   ✅ PASS: Insufficient balance correctly rejected")
            else:
                print(f"   ❌ FAIL: Wrong error message: '{error_msg}'")
                print(f"   Full response: {result}")
        else:
            print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 2: Invalid Voucher Code
    print("\n4. Testing Invalid Voucher Code...")
    payment_data = {"voucher_code": "INVALID123", "amount": 100}
    payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
    print(f"   Payment status: {payment_response.status_code}")
    if payment_response.status_code == 400:
        result = payment_response.json()
        error_msg = (result.get('error') or 
                   result.get('non_field_errors', [''])[0] or
                   result.get('voucher_code', [''])[0] if isinstance(result.get('voucher_code'), list) else result.get('voucher_code', ''))
        if "Invalid voucher code" in error_msg:
            print("   ✅ PASS: Invalid voucher code correctly rejected")
        else:
            print(f"   ❌ FAIL: Wrong error message: {error_msg}")
    else:
        print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 3: Disabled Voucher
    print("\n5. Testing Disabled Voucher...")
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_id = voucher_response.json().get('id')
        voucher_code = voucher_response.json().get('code')
        
        # Disable voucher
        disable_response = requests.delete(f"http://localhost:8000/api/vouchers/{voucher_id}/", headers=headers)
        print(f"   Disable status: {disable_response.status_code}")
        
        if disable_response.status_code == 200:
            # Try payment with disabled voucher
            payment_data = {"voucher_code": voucher_code, "amount": 100}
            payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
            print(f"   Payment status: {payment_response.status_code}")
            if payment_response.status_code == 400:
                result = payment_response.json()
                # Extract error message from different possible locations
                error_msg = ''
                if result.get('error'):
                    error_msg = result.get('error')
                elif result.get('non_field_errors'):
                    error_msg = result.get('non_field_errors')[0]
                elif result.get('amount'):
                    if isinstance(result.get('amount'), list):
                        error_msg = result.get('amount')[0]
                    else:
                        error_msg = result.get('amount')
                elif result.get('voucher_code'):
                    if isinstance(result.get('voucher_code'), list):
                        error_msg = result.get('voucher_code')[0]
                    else:
                        error_msg = result.get('voucher_code')
                if "disabled" in error_msg.lower() or "sold" in error_msg.lower():
                    print("   ✅ PASS: Disabled voucher correctly rejected")
                else:
                    print(f"   ❌ FAIL: Wrong error message: '{error_msg}'")
                    print(f"   Full response: {result}")
            else:
                print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 4: Sold Voucher
    print("\n6. Testing Sold Voucher...")
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_id = voucher_response.json().get('id')
        voucher_code = voucher_response.json().get('code')
        
        # Mark as sold
        sold_response = requests.post(f"http://localhost:8000/api/vouchers/{voucher_id}/mark-sold/", headers=headers)
        print(f"   Mark sold status: {sold_response.status_code}")
        
        if sold_response.status_code == 200:
            # Try payment with sold voucher
            payment_data = {"voucher_code": voucher_code, "amount": 100}
            payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
            print(f"   Payment status: {payment_response.status_code}")
            if payment_response.status_code == 400:
                result = payment_response.json()
                # Extract error message from different possible locations
                error_msg = ''
                if result.get('error'):
                    error_msg = result.get('error')
                elif result.get('non_field_errors'):
                    error_msg = result.get('non_field_errors')[0]
                elif result.get('amount'):
                    if isinstance(result.get('amount'), list):
                        error_msg = result.get('amount')[0]
                    else:
                        error_msg = result.get('amount')
                elif result.get('voucher_code'):
                    if isinstance(result.get('voucher_code'), list):
                        error_msg = result.get('voucher_code')[0]
                    else:
                        error_msg = result.get('voucher_code')
                if "disabled" in error_msg.lower() or "sold" in error_msg.lower():
                    print("   ✅ PASS: Sold voucher correctly rejected")
                else:
                    print(f"   ❌ FAIL: Wrong error message: '{error_msg}'")
                    print(f"   Full response: {result}")
            else:
                print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 5: Negative Amount
    print("\n7. Testing Negative Amount...")
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    if voucher_response.status_code == 201:
        voucher_code = voucher_response.json().get('code')
        payment_data = {"voucher_code": voucher_code, "amount": -100}
        payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
        print(f"   Payment status: {payment_response.status_code}")
        if payment_response.status_code == 400:
            print("   ✅ PASS: Negative amount correctly rejected")
        else:
            print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    # Test 6: Zero Amount
    print("\n8. Testing Zero Amount...")
    payment_data = {"voucher_code": voucher_code, "amount": 0}
    payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
    print(f"   Payment status: {payment_response.status_code}")
    if payment_response.status_code == 400:
        print("   ✅ PASS: Zero amount correctly rejected")
    else:
        print(f"   ❌ FAIL: Expected 400, got {payment_response.status_code}")
    
    print("\n=== TESTING AUTHENTICATION EDGE CASES ===")
    
    # Test 7: Duplicate Username
    print("\n9. Testing Duplicate Username...")
    duplicate_data = {
        "username": username,  # Same username as before
        "email": "different@example.com",
        "password": "differentpass"
    }
    duplicate_response = requests.post("http://localhost:8000/api/register/", json=duplicate_data)
    print(f"   Registration status: {duplicate_response.status_code}")
    if duplicate_response.status_code == 400:
        result = duplicate_response.json()
        if "already exists" in result.get('error', '').lower():
            print("   ✅ PASS: Duplicate username correctly rejected")
        else:
            print(f"   ❌ FAIL: Wrong error message: {result.get('error')}")
    else:
        print(f"   ❌ FAIL: Expected 400, got {duplicate_response.status_code}")
    
    # Test 8: Invalid Login
    print("\n10. Testing Invalid Login...")
    invalid_login_response = requests.post("http://localhost:8000/api/get-token/", 
                                         json={"username": "nonexistent", "password": "wrong"})
    print(f"   Login status: {invalid_login_response.status_code}")
    if invalid_login_response.status_code == 401:
        print("   ✅ PASS: Invalid login correctly rejected")
    else:
        print(f"   ❌ FAIL: Expected 401, got {invalid_login_response.status_code}")
    
    # Test 9: Unauthorized Access
    print("\n11. Testing Unauthorized Access...")
    unauthorized_response = requests.get("http://localhost:8000/api/vouchers/")
    print(f"   Access status: {unauthorized_response.status_code}")
    if unauthorized_response.status_code == 401:
        print("   ✅ PASS: Unauthorized access correctly rejected")
    else:
        print(f"   ❌ FAIL: Expected 401, got {unauthorized_response.status_code}")
    
    print("\n=== EDGE CASE TESTING COMPLETE ===")
    return True

if __name__ == "__main__":
    test_all_edge_cases()
