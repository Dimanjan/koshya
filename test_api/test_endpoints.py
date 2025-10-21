#!/usr/bin/env python3
"""
API Endpoint Testing Script for Voucher System
Tests all endpoints and reports any errors
"""

import requests
import json
import sys
import time

BASE_URL = "http://localhost:8000/api"
ADMIN_USERNAME = "koshya"  # Actual superuser username
ADMIN_PASSWORD = "testpass123"  # Updated superuser password

def test_auth_endpoint():
    """Test authentication endpoint"""
    print("🔐 Testing authentication endpoint...")
    
    # Test with valid credentials
    auth_data = {
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    }
    
    try:
        response = requests.post(f"{BASE_URL}/get-token/", json=auth_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print(f"   ✅ Token received: {token_data.get('token', 'N/A')[:20]}...")
            return token_data.get('token')
        else:
            print(f"   ❌ Auth failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Auth error: {e}")
        return None

def test_voucher_creation(token):
    """Test voucher creation"""
    print("\n🎫 Testing voucher creation...")
    
    headers = {"Authorization": f"Token {token}"}
    voucher_data = {"initial_value": 100.00}
    
    try:
        response = requests.post(f"{BASE_URL}/vouchers/", json=voucher_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 201:
            voucher = response.json()
            print(f"   ✅ Voucher created: {voucher}")
            return voucher
        else:
            print(f"   ❌ Voucher creation failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Voucher creation error: {e}")
        return None

def test_voucher_listing(token):
    """Test voucher listing"""
    print("\n📋 Testing voucher listing...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/vouchers/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            vouchers = response.json()
            print(f"   ✅ Found {len(vouchers.get('results', vouchers))} vouchers")
            return vouchers
        else:
            print(f"   ❌ Voucher listing failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Voucher listing error: {e}")
        return None

def test_voucher_detail(token, voucher_id):
    """Test voucher detail view"""
    print(f"\n🔍 Testing voucher detail for ID {voucher_id}...")
    
    headers = {"Authorization": f"Token {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/vouchers/{voucher_id}/", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            voucher = response.json()
            print(f"   ✅ Voucher details: {voucher.get('code', 'N/A')} - ${voucher.get('balance', 'N/A')}")
            return voucher
        else:
            print(f"   ❌ Voucher detail failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Voucher detail error: {e}")
        return None

def test_voucher_recharge(token, voucher_code):
    """Test voucher recharge"""
    print(f"\n💰 Testing voucher recharge for {voucher_code}...")
    
    headers = {"Authorization": f"Token {token}"}
    recharge_data = {"amount": 200}
    
    try:
        response = requests.post(f"{BASE_URL}/vouchers/{voucher_code}/recharge/", 
                                json=recharge_data, headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Recharge successful: {result}")
            return result
        else:
            print(f"   ❌ Recharge failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Recharge error: {e}")
        return None

def test_payment_endpoint(voucher_code):
    """Test public payment endpoint"""
    print(f"\n💳 Testing payment with voucher {voucher_code}...")
    
    payment_data = {
        "voucher_code": voucher_code,
        "amount": 50.00
    }
    
    try:
        response = requests.post(f"{BASE_URL}/pay/", json=payment_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Payment successful: {result}")
            return result
        else:
            print(f"   ❌ Payment failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Payment error: {e}")
        return None

def main():
    """Run all tests"""
    print("🚀 Starting API Endpoint Tests")
    print("=" * 50)
    
    # Test authentication
    token = test_auth_endpoint()
    if not token:
        print("\n❌ Authentication failed - cannot proceed with other tests")
        return False
    
    # Test voucher creation
    voucher = test_voucher_creation(token)
    if not voucher:
        print("\n❌ Voucher creation failed - cannot proceed with other tests")
        return False
    
    voucher_id = voucher.get('id')
    voucher_code = voucher.get('code')
    
    # Test voucher listing
    test_voucher_listing(token)
    
    # Test voucher detail
    test_voucher_detail(token, voucher_id)
    
    # Test voucher recharge
    test_voucher_recharge(token, voucher_code)
    
    # Test payment endpoint
    test_payment_endpoint(voucher_code)
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
