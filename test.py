"""
Comprehensive Test Script for Admin API Endpoints
Tests all admin endpoints including rankings, comparisons, and top performers

Usage:
    python scripts/test_admin_endpoints.py

Requirements:
    - Server running on http://localhost:8000
    - Admin account created
    - requests library installed
"""
import requests
import json
import sys
from typing import Optional, Dict, Any, List
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1/admin"
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 30  # Request timeout in seconds

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "errors": []
}


def print_header(text: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def print_test(name: str):
    """Print test name"""
    print(f"\n🧪 Testing: {name}")
    print("-" * 80)


def print_success(message: str = "✅ PASSED"):
    """Print success message"""
    print(f"✅ {message}")
    test_results["passed"] += 1


def print_failure(message: str, error: str = ""):
    """Print failure message"""
    print(f"❌ {message}")
    if error:
        print(f"   Error: {error}")
    test_results["failed"] += 1
    test_results["errors"].append(f"{message}: {error}")


def print_skip(message: str):
    """Print skip message"""
    print(f"⏭️  SKIPPED: {message}")
    test_results["skipped"] += 1


def admin_signup(username: str, email: str, password: str) -> Optional[Dict]:
    """Create first admin user (public signup)"""
    print_test("Admin Signup (First Admin)")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup",
            json={
                "username": username,
                "email": email,
                "password": password
            },
            timeout=TIMEOUT
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"Admin created successfully! Username: {data.get('username')}")
            return data
        elif response.status_code == 403:
            # Admin already exists, that's okay
            print_skip("Admin already exists (signup only works for first admin)")
            return None
        else:
            print_failure(f"Signup failed: {response.status_code}", response.text[:200])
            return None
    except requests.exceptions.RequestException as e:
        print_failure("Signup request failed", str(e))
        return None


def test_admin_login(username: str, password: str) -> Optional[str]:
    """Test admin login and return access token"""
    print_test("Admin Login")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            params={"username": username, "password": password},
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print_success(f"Login successful! Token: {token[:30]}...")
                return token
            else:
                print_failure("Login response missing access_token")
                return None
        else:
            print_failure(f"Login failed: {response.status_code}", response.text[:200])
            return None
    except requests.exceptions.RequestException as e:
        print_failure("Login request failed", str(e))
        return None


def test_endpoint(
    method: str,
    endpoint: str,
    token: str,
    params: Optional[Dict] = None,
    body: Optional[Any] = None,
    expected_status: int = 200,
    description: str = ""
) -> Optional[Any]:
    """Test an admin endpoint with comprehensive error handling"""
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{BASE_URL}{endpoint}"
    
    test_name = description or f"{method} {endpoint}"
    print(f"   📡 {test_name}")
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=body, params=params, timeout=TIMEOUT)
        else:
            print_failure(f"Unsupported method: {method}")
            return None
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                # Print summary for large responses
                success_msg = ""
                if isinstance(data, dict):
                    if "rankings" in data and len(data.get("rankings", [])) > 0:
                        success_msg = f"Returned {len(data['rankings'])} rankings"
                    elif "users" in data and len(data.get("users", [])) > 0:
                        success_msg = f"Returned {len(data['users'])} users"
                    elif "interviews" in data and isinstance(data["interviews"], list):
                        success_msg = f"Returned {len(data['interviews'])} interviews"
                    else:
                        success_msg = f"Response keys: {list(data.keys())[:5]}"
                elif isinstance(data, list):
                    success_msg = f"Returned {len(data)} items"
                else:
                    success_msg = "Success"
                
                print_success(success_msg)
                return data
            except json.JSONDecodeError:
                # Non-JSON response (like CSV export)
                print_success(f"Non-JSON response, length: {len(response.text)} bytes")
                return response.text
        else:
            error_msg = response.text[:200] if response.text else "No error message"
            print_failure(f"Expected {expected_status}, got {response.status_code}", error_msg)
            return None
    except requests.exceptions.Timeout:
        print_failure("Request timeout", f"Endpoint took longer than {TIMEOUT} seconds")
        return None
    except requests.exceptions.RequestException as e:
        print_failure("Request failed", str(e))
        return None
    except Exception as e:
        print_failure("Unexpected error", str(e))
        return None


def test_statistics_endpoints(token: str):
    """Test all statistics endpoints"""
    print_header("STATISTICS ENDPOINTS")
    
    # Overview stats
    print_test("Overview Statistics")
    test_endpoint("GET", "/stats/overview", token, description="Get dashboard overview")
    
    # Score distribution
    print_test("Score Distribution")
    test_endpoint("GET", "/stats/score-distribution", token, description="Get score distribution")
    
    # Question performance
    print_test("Question Performance")
    test_endpoint("GET", "/analytics/question-performance", token, description="Get question performance stats")


def test_user_management_endpoints(token: str):
    """Test user management endpoints"""
    print_header("USER MANAGEMENT ENDPOINTS")
    
    # Get all users
    print_test("Get All Users")
    users_data = test_endpoint(
        "GET", "/users", token,
        params={"skip": 0, "limit": 10},
        description="Get all users with pagination"
    )
    
    # Get user details (if we have users)
    if users_data and len(users_data) > 0:
        first_user_id = users_data[0].get("id")
        if first_user_id:
            print_test(f"Get User Details (ID: {first_user_id})")
            test_endpoint(
                "GET", f"/users/{first_user_id}", token,
                description=f"Get details for user {first_user_id}"
            )
    else:
        print_skip("No users found to test user details endpoint")


def test_interview_management_endpoints(token: str):
    """Test interview management endpoints"""
    print_header("INTERVIEW MANAGEMENT ENDPOINTS")
    
    # Get all interviews
    print_test("Get All Interviews")
    interviews_data = test_endpoint(
        "GET", "/interviews", token,
        params={"skip": 0, "limit": 10},
        description="Get all interviews with pagination"
    )
    
    # Get interview with filters
    print_test("Get Interviews with Filters")
    test_endpoint(
        "GET", "/interviews", token,
        params={"skip": 0, "limit": 5, "min_score": 70},
        description="Get interviews with min_score filter"
    )
    
    # Get interview details (if we have interviews)
    if interviews_data and len(interviews_data) > 0:
        first_session_id = interviews_data[0].get("session_id")
        if first_session_id:
            print_test(f"Get Interview Details (Session: {first_session_id[:20]}...)")
            test_endpoint(
                "GET", f"/interviews/{first_session_id}", token,
                description=f"Get details for interview {first_session_id[:20]}"
            )
    else:
        print_skip("No interviews found to test interview details endpoint")
    
    # Test export
    print_test("Export Interviews (JSON)")
    test_endpoint(
        "GET", "/interviews/export", token,
        params={"format": "json", "limit": 5, "include_transcript": False},
        description="Export interviews as JSON"
    )
    
    # Test transcript status
    print_test("Get Transcript Status")
    test_endpoint(
        "GET", "/interviews/transcript-status", token,
        description="Get transcript status statistics"
    )


def test_ranking_endpoints(token: str):
    """Test user ranking endpoints"""
    print_header("USER RANKING ENDPOINTS")
    
    # Test different sort options
    sort_options = [
        ("average_score", "Average Score"),
        ("best_score", "Best Score"),
        ("latest_score", "Latest Score"),
        ("total_interviews", "Total Interviews"),
        ("improvement", "Improvement")
    ]
    
    for sort_by, description in sort_options:
        print_test(f"User Rankings - {description}")
        rankings_data = test_endpoint(
            "GET", "/analytics/user-rankings", token,
            params={"sort_by": sort_by, "limit": 10, "min_interviews": 1},
            description=f"Get rankings sorted by {sort_by}"
        )
        
        # Validate response structure
        if rankings_data and isinstance(rankings_data, dict):
            if "rankings" in rankings_data:
                print(f"      📊 Found {len(rankings_data['rankings'])} ranked users")
                if len(rankings_data['rankings']) > 0:
                    top_user = rankings_data['rankings'][0]
                    print(f"      🏆 Top user: {top_user.get('email', 'N/A')} (Rank: {top_user.get('rank', 'N/A')})")


def test_comparison_endpoints(token: str):
    """Test user comparison endpoints"""
    print_header("USER COMPARISON ENDPOINTS")
    
    # First, get some user IDs
    print_test("Getting User IDs for Comparison")
    users_data = test_endpoint(
        "GET", "/users", token,
        params={"skip": 0, "limit": 10},
        description="Get users for comparison test"
    )
    
    if users_data and len(users_data) >= 2:
        user_ids = [u.get("id") for u in users_data[:3] if u.get("id")]
        
        if len(user_ids) >= 2:
            print_test(f"Compare Users (IDs: {user_ids})")
            comparison_data = test_endpoint(
                "POST", "/analytics/compare-users", token,
                body=user_ids,
                description=f"Compare {len(user_ids)} users"
            )
            
            # Validate comparison structure
            if comparison_data and isinstance(comparison_data, dict):
                if "comparison_summary" in comparison_data:
                    summary = comparison_data["comparison_summary"]
                    print(f"      📊 Comparison Summary:")
                    if "best_average_score" in summary:
                        best = summary["best_average_score"]
                        print(f"         Best Average: {best.get('value', 'N/A')} (User: {best.get('user_email', 'N/A')})")
                    if "most_improved" in summary:
                        improved = summary["most_improved"]
                        print(f"         Most Improved: {improved.get('value', 'N/A')} (User: {improved.get('user_email', 'N/A')})")
        else:
            print_skip("Not enough valid user IDs for comparison")
    else:
        print_skip("Not enough users found for comparison test")
    
    # Test error cases
    print_test("Compare Users - Error Cases")
    
    # Test with less than 2 users
    test_endpoint(
        "POST", "/analytics/compare-users", token,
        body=[1],
        expected_status=400,
        description="Compare with only 1 user (should fail)"
    )
    
    # Test with more than 10 users
    test_endpoint(
        "POST", "/analytics/compare-users", token,
        body=list(range(1, 12)),
        expected_status=400,
        description="Compare with 11 users (should fail)"
    )


def test_top_performers_endpoints(token: str):
    """Test top performers endpoints"""
    print_header("TOP PERFORMERS ENDPOINTS")
    
    print_test("Get Top Performers")
    top_performers = test_endpoint(
        "GET", "/analytics/top-performers", token,
        params={"limit": 10, "min_interviews": 1},
        description="Get top performers in all categories"
    )
    
    # Validate response structure
    if top_performers and isinstance(top_performers, dict):
        categories = [
            "top_by_average_score",
            "top_by_best_score",
            "top_by_latest_score",
            "most_improved",
            "most_active"
        ]
        
        print(f"      📊 Top Performers Categories:")
        for category in categories:
            if category in top_performers:
                count = len(top_performers[category]) if isinstance(top_performers[category], list) else 0
                print(f"         {category}: {count} users")


def test_error_handling(token: str):
    """Test error handling and edge cases"""
    print_header("ERROR HANDLING & EDGE CASES")
    
    # Test invalid user ID
    print_test("Invalid User ID")
    test_endpoint(
        "GET", "/users/999999", token,
        expected_status=404,
        description="Get non-existent user (should return 404)"
    )
    
    # Test invalid session ID
    print_test("Invalid Session ID")
    test_endpoint(
        "GET", "/interviews/invalid_session_id_12345", token,
        expected_status=404,
        description="Get non-existent interview (should return 404)"
    )
    
    # Test invalid sort option
    print_test("Invalid Sort Option")
    test_endpoint(
        "GET", "/analytics/user-rankings", token,
        params={"sort_by": "invalid_sort"},
        expected_status=422,  # Validation error is correct
        description="Invalid sort option (should return 422 validation error)"
    )
    
    # Test invalid limit
    print_test("Invalid Limit Parameter")
    test_endpoint(
        "GET", "/analytics/user-rankings", token,
        params={"limit": 2000},  # Exceeds max
        expected_status=422,  # Validation error is correct
        description="Limit exceeding maximum (should return 422 validation error)"
    )


def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = test_results["passed"] + test_results["failed"] + test_results["skipped"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"✅ Passed: {test_results['passed']} ({pass_rate:.1f}%)")
    print(f"❌ Failed: {test_results['failed']}")
    print(f"⏭️  Skipped: {test_results['skipped']}")
    
    if test_results["errors"]:
        print("\n❌ Errors Encountered:")
        for error in test_results["errors"][:10]:  # Show first 10 errors
            print(f"   - {error}")
        if len(test_results["errors"]) > 10:
            print(f"   ... and {len(test_results['errors']) - 10} more errors")
    
    print("\n" + "=" * 80)
    
    if test_results["failed"] == 0:
        print("🎉 All tests passed!")
    else:
        print(f"⚠️  {test_results['failed']} test(s) failed. Please review errors above.")
    
    print("=" * 80 + "\n")


def main():
    """Main test function"""
    print_header("ADMIN API COMPREHENSIVE TEST SUITE")
    print(f"Testing endpoints at: {BASE_URL}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("⚠️  Warning: Server health check failed")
    except requests.exceptions.RequestException:
        print("❌ ERROR: Cannot connect to server at http://localhost:8000")
        print("   Please make sure the server is running!")
        sys.exit(1)
    
    # Admin signup/login flow
    print("\n" + "-" * 80)
    print("Admin Account Setup")
    print("-" * 80)
    print("If this is your first admin, we'll create one. Otherwise, we'll login.")
    print()
    
    username = input("Enter admin username: ").strip()
    email = input("Enter admin email: ").strip()
    password = input("Enter admin password: ").strip()
    
    if not username or not email or not password:
        print("❌ Username, email, and password are required!")
        sys.exit(1)
    
    # Try to signup first (will work if no admins exist)
    signup_result = admin_signup(username, email, password)
    
    # Login (whether we just signed up or admin already existed)
    token = test_admin_login(username, password)
    if not token:
        print("\n❌ Cannot proceed without authentication")
        print("   If admin already exists, make sure you're using correct credentials.")
        sys.exit(1)
    
    # Run all test suites
    try:
        test_statistics_endpoints(token)
        test_user_management_endpoints(token)
        test_interview_management_endpoints(token)
        test_ranking_endpoints(token)
        test_comparison_endpoints(token)
        test_top_performers_endpoints(token)
        test_error_handling(token)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if test_results["failed"] == 0 else 1)


if __name__ == "__main__":
    main()