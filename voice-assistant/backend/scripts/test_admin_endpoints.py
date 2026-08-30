"""
Test script for admin API endpoints
Run this after starting the server to test the admin endpoints
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8002/api/v1/admin"

def test_admin_login(username: str, password: str) -> Optional[str]:
    """Test admin login and return access token"""
    print("🔐 Testing admin login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        params={"username": username, "password": password}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_endpoint(method: str, endpoint: str, token: str, params: dict = None):
    """Test an admin endpoint"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n📡 Testing {method} {endpoint}...")
    
    if method == "GET":
        response = requests.get(url, headers=headers, params=params)
    elif method == "POST":
        response = requests.post(url, headers=headers, json=params)
    else:
        print(f"❌ Unsupported method: {method}")
        return None
    
    if response.status_code == 200:
        print(f"✅ Success!")
        try:
            data = response.json()
            print(f"📊 Response: {json.dumps(data, indent=2)[:500]}...")
            return data
        except:
            print(f"📄 Response (non-JSON): {response.text[:200]}")
            return response.text
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"Error: {response.text[:200]}")
        return None

def main():
    print("=" * 60)
    print("🧪 Admin API Endpoints Test Script")
    print("=" * 60)
    
    # Step 1: Login
    username = input("\nEnter admin username: ").strip()
    password = input("Enter admin password: ").strip()
    
    token = test_admin_login(username, password)
    if not token:
        print("\n❌ Cannot proceed without authentication")
        return
    
    print("\n" + "=" * 60)
    print("Testing Admin Endpoints")
    print("=" * 60)
    
    # Test overview stats
    test_endpoint("GET", "/stats/overview", token)
    
    # Test score distribution
    test_endpoint("GET", "/stats/score-distribution", token)
    
    # Test question performance
    test_endpoint("GET", "/analytics/question-performance", token)
    
    # Test get all users
    test_endpoint("GET", "/users", token, {"skip": 0, "limit": 10})
    
    # Test get all interviews
    test_endpoint("GET", "/interviews", token, {"skip": 0, "limit": 10})
    
    # Test export (if you have interviews)
    print("\n📥 Testing export endpoint...")
    test_endpoint("GET", "/interviews/export", token, {"format": "json", "limit": 5})
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)
    print("\n💡 To test user details, use:")
    print("   GET /admin/users/{user_id}")
    print("\n💡 To test interview details, use:")
    print("   GET /admin/interviews/{session_id}")

if __name__ == "__main__":
    main()

