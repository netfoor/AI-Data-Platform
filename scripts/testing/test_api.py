#!/usr/bin/env python3
"""
Test script for AI Data Platform API endpoints
"""
import requests
import time
import json

def test_endpoint(url, endpoint_name):
    """Test a single API endpoint"""
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
        return response.status_code == 200
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test all API endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("⏳ Waiting 3 seconds for server to start...")
    time.sleep(3)
    
    print("🧪 Testing AI Data Platform API endpoints...")
    print(f"Base URL: {base_url}")
    print("-" * 50)
    
    # Test all endpoints
    endpoints = [
        ("/", "root endpoint"),
        ("/health", "health endpoint"),
        ("/metrics", "metrics endpoint"),
        ("/time-analysis", "time analysis endpoint"),
        ("/daily-trends?days=7", "daily trends endpoint (7 days)"),
        ("/platform-metrics", "platform metrics endpoint"),
        ("/docs", "API documentation")
    ]
    
    success_count = 0
    total_endpoints = len(endpoints)
    
    for i, (endpoint, name) in enumerate(endpoints, 1):
        print(f"{i}. Testing {name} ({endpoint})...")
        if test_endpoint(base_url + endpoint, name):
            success_count += 1
        print()
    
    print("✅ API testing completed!")
    print(f"📊 Results: {success_count}/{total_endpoints} endpoints working")
    
    if success_count == total_endpoints:
        print("🎉 All API endpoints are working perfectly!")
    else:
        print(f"⚠️  {total_endpoints - success_count} endpoint(s) need attention")

if __name__ == "__main__":
    main()
