#!/usr/bin/env python3
"""
Test script to verify login API works correctly
"""

import requests
import json

def test_login():
    """Test the login API with different scenarios"""
    
    base_url = "http://127.0.0.1:5000"
    
    # Test cases
    test_cases = [
        {
            "name": "Valid admin login",
            "data": {"username": "admin", "password": "123456"},
            "expected_status": 200
        },
        {
            "name": "Valid teacher login", 
            "data": {"username": "teacher", "password": "123456"},
            "expected_status": 200
        },
        {
            "name": "Valid student login",
            "data": {"username": "student", "password": "123456"},
            "expected_status": 200
        },
        {
            "name": "Invalid password",
            "data": {"username": "admin", "password": "wrong"},
            "expected_status": 401
        },
        {
            "name": "Non-existent user",
            "data": {"username": "nonexistent", "password": "123456"},
            "expected_status": 401
        }
    ]
    
    print("Testing Login API...")
    print("=" * 50)
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Data: {test_case['data']}")
        
        try:
            response = requests.post(
                f"{base_url}/login",
                data=test_case['data'],
                headers={
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            try:
                json_response = response.json()
                print(f"Response: {json.dumps(json_response, indent=2)}")
                
                # Check if test passed
                if response.status_code == test_case['expected_status']:
                    if json_response.get('success'):
                        print("✅ TEST PASSED")
                    else:
                        print("❌ TEST FAILED - No success flag in response")
                else:
                    print(f"❌ TEST FAILED - Expected {test_case['expected_status']}, got {response.status_code}")
                    
            except ValueError:
                print(f"Response Text: {response.text}")
                if response.status_code == test_case['expected_status']:
                    print("✅ TEST PASSED (HTML response)")
                else:
                    print(f"❌ TEST FAILED - Expected {test_case['expected_status']}, got {response.status_code}")
                    
        except requests.exceptions.RequestException as e:
            print(f"❌ NETWORK ERROR: {e}")
        
        print("-" * 40)

if __name__ == '__main__':
    test_login()
