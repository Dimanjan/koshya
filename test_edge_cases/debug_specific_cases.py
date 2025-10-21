#!/usr/bin/env python3
"""
Debug specific failing edge cases
"""

import requests
import json
import time

def debug_insufficient_balance():
    """Debug insufficient balance case"""
    print("=== DEBUGGING INSUFFICIENT BALANCE ===")
    
    # Setup
    username = f"debug_{int(time.time())}"
    register_data = {"username": username, "email": f"{username}@example.com", "password": "testpass123"}
    requests.post("http://localhost:8000/api/register/", json=register_data)
    
    login_response = requests.post("http://localhost:8000/api/get-token/", 
                                 json={"username": username, "password": "testpass123"})
    token = login_response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    
    # Create voucher with small balance
    voucher_data = {"initial_value": 50}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    voucher_code = voucher_response.json().get('code')
    
    # Try payment with insufficient balance
    payment_data = {"voucher_code": voucher_code, "amount": 100}
    payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
    
    print(f"Status: {payment_response.status_code}")
    print(f"Response: {payment_response.text}")
    
    if payment_response.status_code == 400:
        result = payment_response.json()
        print(f"Parsed JSON: {result}")
        
        # Try all possible error message locations
        error_msg1 = result.get('error', '')
        error_msg2 = result.get('non_field_errors', [''])[0]
        error_msg3 = result.get('amount', [''])[0] if isinstance(result.get('amount'), list) else result.get('amount', '')
        error_msg4 = result.get('voucher_code', [''])[0] if isinstance(result.get('voucher_code'), list) else result.get('voucher_code', '')
        
        print(f"Error method 1 (error): '{error_msg1}'")
        print(f"Error method 2 (non_field_errors): '{error_msg2}'")
        print(f"Error method 3 (amount): '{error_msg3}'")
        print(f"Error method 4 (voucher_code): '{error_msg4}'")
        
        # Check if any contain "Insufficient balance"
        for i, msg in enumerate([error_msg1, error_msg2, error_msg3, error_msg4], 1):
            if "Insufficient balance" in msg:
                print(f"✅ Found 'Insufficient balance' in method {i}: '{msg}'")
            else:
                print(f"❌ 'Insufficient balance' not found in method {i}: '{msg}'")

def debug_disabled_voucher():
    """Debug disabled voucher case"""
    print("\n=== DEBUGGING DISABLED VOUCHER ===")
    
    # Setup
    username = f"debug2_{int(time.time())}"
    register_data = {"username": username, "email": f"{username}@example.com", "password": "testpass123"}
    requests.post("http://localhost:8000/api/register/", json=register_data)
    
    login_response = requests.post("http://localhost:8000/api/get-token/", 
                                 json={"username": username, "password": "testpass123"})
    token = login_response.json().get("token")
    headers = {"Authorization": f"Token {token}"}
    
    # Create voucher
    voucher_data = {"initial_value": 500}
    voucher_response = requests.post("http://localhost:8000/api/vouchers/", 
                                   json=voucher_data, headers=headers)
    voucher_id = voucher_response.json().get('id')
    voucher_code = voucher_response.json().get('code')
    
    # Disable voucher
    disable_response = requests.delete(f"http://localhost:8000/api/vouchers/{voucher_id}/", headers=headers)
    print(f"Disable status: {disable_response.status_code}")
    
    # Try payment with disabled voucher
    payment_data = {"voucher_code": voucher_code, "amount": 100}
    payment_response = requests.post("http://localhost:8000/api/pay/", json=payment_data)
    
    print(f"Payment status: {payment_response.status_code}")
    print(f"Payment response: {payment_response.text}")
    
    if payment_response.status_code == 400:
        result = payment_response.json()
        print(f"Parsed JSON: {result}")
        
        # Try all possible error message locations
        error_msg1 = result.get('error', '')
        error_msg2 = result.get('non_field_errors', [''])[0]
        error_msg3 = result.get('amount', [''])[0] if isinstance(result.get('amount'), list) else result.get('amount', '')
        error_msg4 = result.get('voucher_code', [''])[0] if isinstance(result.get('voucher_code'), list) else result.get('voucher_code', '')
        
        print(f"Error method 1 (error): '{error_msg1}'")
        print(f"Error method 2 (non_field_errors): '{error_msg2}'")
        print(f"Error method 3 (amount): '{error_msg3}'")
        print(f"Error method 4 (voucher_code): '{error_msg4}'")
        
        # Check if any contain "disabled" or "sold"
        for i, msg in enumerate([error_msg1, error_msg2, error_msg3, error_msg4], 1):
            if "disabled" in msg.lower() or "sold" in msg.lower():
                print(f"✅ Found 'disabled/sold' in method {i}: '{msg}'")
            else:
                print(f"❌ 'disabled/sold' not found in method {i}: '{msg}'")

if __name__ == "__main__":
    debug_insufficient_balance()
    debug_disabled_voucher()
