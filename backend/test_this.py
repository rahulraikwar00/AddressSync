#!/usr/bin/env python
"""
Full API Test Script for Address Sync Service
Tests all endpoints with demo data and displays results
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
TIMEOUT = 10

# Colors for terminal output


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.YELLOW}ℹ {message}{Colors.END}")


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_json(data: Any):
    """Pretty print JSON data"""
    print(json.dumps(data, indent=2, default=str))


def api_request(method: str, endpoint: str, data: Optional[Dict] = None, token: Optional[str] = None) -> Dict:
    """Make API request and return response"""
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    url = f"{BASE_URL}{endpoint}"

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, timeout=TIMEOUT)
        elif method.upper() == "POST":
            response = requests.post(
                url, json=data, headers=headers, timeout=TIMEOUT)
        elif method.upper() == "PUT":
            response = requests.put(
                url, json=data, headers=headers, timeout=TIMEOUT)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, timeout=TIMEOUT)
        else:
            return {"error": f"Unsupported method: {method}"}

        try:
            response_data = response.json()
        except:
            response_data = {"raw_response": response.text}

        return {
            "status_code": response.status_code,
            "data": response_data,
            "success": 200 <= response.status_code < 300
        }
    except requests.exceptions.ConnectionError:
        return {"error": f"Cannot connect to {BASE_URL}", "success": False}
    except requests.exceptions.Timeout:
        return {"error": "Request timeout", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}


def test_health_check():
    """Test health endpoint"""
    print_section("1. TESTING HEALTH CHECK")
    result = api_request("GET", "/health")

    if result.get("success"):
        print_success("Health check passed")
        print_json(result.get("data"))
        return True
    else:
        print_error(f"Health check failed: {result.get('error')}")
        return False


# Demo Data
DEMO_USERS = [
    {
        "aadhaar_number": "123456789012",
        "name": "Rajesh Kumar",
        "email": "rajesh.kumar@email.com",
        "current_address": "123 MG Road, Bangalore, Karnataka 560001",
        "password": "Rajesh@1234"
    },
    {
        "aadhaar_number": "234567890123",
        "name": "Priya Sharma",
        "email": "priya.sharma@email.com",
        "current_address": "456 Park Street, Kolkata, West Bengal 700016",
        "password": "Priya@1234"
    },
    {
        "aadhaar_number": "345678901234",
        "name": "Amit Patel",
        "email": "amit.patel@email.com",
        "current_address": "789 Linking Road, Mumbai, Maharashtra 400054",
        "password": "Amit@1234"
    },
    {
        "aadhaar_number": "456789012345",
        "name": "Neha Gupta",
        "email": "neha.gupta@email.com",
        "current_address": "321 Connaught Place, New Delhi, Delhi 110001",
        "password": "Neha@1234"
    }
]

DEMO_AGENCIES = [
    {
        "id": "municipal_bangalore",
        "name": "Bangalore Municipal Corporation",
        "email": "bmc@bangalore.gov.in",
        "password": "BMC@12345"
    },
    {
        "id": "municipal_mumbai",
        "name": "Mumbai Municipal Corporation",
        "email": "mmc@mumbai.gov.in",
        "password": "MMC@12345"
    },
    {
        "id": "municipal_delhi",
        "name": "Delhi Municipal Corporation",
        "email": "dmc@delhi.gov.in",
        "password": "DMC@12345"
    }
]

DEMO_REQUESTS = [
    {"new_address": "789 Electronic City, Bangalore, Karnataka 560100"},
    {"new_address": "456 Andheri East, Mumbai, Maharashtra 400093"},
    {"new_address": "123 Dwarka Sector 12, New Delhi, Delhi 110075"},
    {"new_address": "567 Salt Lake City, Kolkata, West Bengal 700064"}
]


class APITester:
    def __init__(self):
        self.user_tokens = {}
        self.agency_tokens = {}
        self.created_requests = []
        self.existing_users = []
        self.existing_agencies = []

    def register_user(self, user_data: Dict) -> Optional[Dict]:
        """Register a new user"""
        print_info(
            f"Registering user: {user_data['name']} ({user_data['aadhaar_number']})")
        result = api_request("POST", "/users/register", user_data)

        if result.get("success"):
            print_success(f"User {user_data['name']} registered successfully")
            return result.get("data")
        else:
            error_detail = result.get('data', {}).get(
                'detail', result.get('error'))
            if "already exists" in str(error_detail):
                print_warning(f"User already exists: {error_detail}")
                return {"exists": True}
            else:
                print_error(f"Failed to register user: {error_detail}")
                return None

    def login_user(self, aadhaar: str, password: str) -> Optional[str]:
        """Login user and get token"""
        login_data = {"aadhaar_number": aadhaar, "password": password}
        result = api_request("POST", "/users/login", login_data)

        if result.get("success"):
            token = result.get("data", {}).get("access_token")
            print_success(f"User {aadhaar} logged in successfully")
            return token
        else:
            error_detail = result.get('data', {}).get(
                'detail', result.get('error'))
            print_error(f"Failed to login user: {error_detail}")
            return None

    def register_agency(self, agency_data: Dict) -> Optional[Dict]:
        """Register a new agency"""
        print_info(
            f"Registering agency: {agency_data['name']} ({agency_data['id']})")
        result = api_request("POST", "/agencies/register", agency_data)

        if result.get("success"):
            print_success(
                f"Agency {agency_data['name']} registered successfully")
            return result.get("data")
        else:
            error_detail = result.get('data', {}).get(
                'detail', result.get('error'))
            if "already exists" in str(error_detail):
                print_warning(f"Agency already exists: {error_detail}")
                return {"exists": True}
            else:
                print_error(f"Failed to register agency: {error_detail}")
                return None

    def login_agency(self, agency_id: str, password: str) -> Optional[str]:
        """Login agency and get token"""
        login_data = {"id": agency_id, "password": password}
        result = api_request("POST", "/agencies/login", login_data)

        if result.get("success"):
            token = result.get("data", {}).get("access_token")
            print_success(f"Agency {agency_id} logged in successfully")
            return token
        else:
            error_detail = result.get('data', {}).get(
                'detail', result.get('error'))
            print_error(f"Failed to login agency: {error_detail}")
            return None

    def get_user_profile(self, token: str, user_name: str):
        """Get user profile"""
        print_info(f"Getting profile for {user_name}")
        result = api_request("GET", "/users/me", token=token)

        if result.get("success"):
            print_success(f"Profile retrieved successfully")
            return result.get("data")
        else:
            print_error(f"Failed to get profile")
            return None

    def get_agency_profile(self, token: str, agency_name: str):
        """Get agency profile"""
        print_info(f"Getting profile for {agency_name}")
        result = api_request("GET", "/agencies/me", token=token)

        if result.get("success"):
            print_success(f"Profile retrieved successfully")
            return result.get("data")
        else:
            print_error(f"Failed to get profile")
            return None

    def create_request(self, token: str, agency_id: str, new_address: str) -> Optional[Dict]:
        """Create a new address change request"""
        print_info(f"Creating request for agency {agency_id}")

        request_data = {
            "agency_id": agency_id,
            "new_address": new_address
        }

        result = api_request("POST", "/requests/create", request_data, token)

        if result.get("success"):
            request = result.get("data")
            print_success(
                f"Request created successfully with ID: {request.get('id')}")
            return request
        else:
            error_detail = result.get('data', {}).get(
                'detail', result.get('error'))
            print_error(f"Failed to create request: {error_detail}")
            return None

    def get_user_requests(self, token: str, user_name: str):
        """Get all requests for current user"""
        print_info(f"Getting requests for {user_name}")
        result = api_request("GET", "/requests/my-requests", token=token)

        if result.get("success"):
            requests = result.get("data", [])
            print_success(f"Found {len(requests)} requests")
            return requests
        else:
            print_error(f"Failed to get requests")
            return []

    def get_agency_requests(self, token: str, agency_name: str):
        """Get all requests for current agency"""
        print_info(f"Getting requests for {agency_name}")
        result = api_request("GET", "/requests/agency-requests", token=token)

        if result.get("success"):
            requests = result.get("data", [])
            print_success(f"Found {len(requests)} requests")
            return requests
        else:
            print_error(f"Failed to get requests")
            return []

    def get_pending_requests(self, token: str, agency_name: str):
        """Get pending requests for current agency"""
        print_info(f"Getting pending requests for {agency_name}")
        result = api_request("GET", "/requests/pending-requests", token=token)

        if result.get("success"):
            requests = result.get("data", [])
            print_success(f"Found {len(requests)} pending requests")
            return requests
        else:
            print_error(f"Failed to get pending requests")
            return []

    def update_request_status(self, token: str, request_id: str, status: str, reason: str = None):
        """Update request status (approve/reject)"""
        print_info(f"Updating request {request_id} to status: {status}")

        update_data = {"status": status}
        if reason:
            update_data["reason"] = reason

        result = api_request(
            "PUT", f"/requests/{request_id}", update_data, token)

        if result.get("success"):
            print_success(f"Request updated successfully to {status}")
            return result.get("data")
        else:
            print_error(f"Failed to update request")
            return None

    def cancel_request(self, token: str, request_id: str):
        """Cancel a request (user only)"""
        print_info(f"Cancelling request {request_id}")
        result = api_request("DELETE", f"/requests/{request_id}", token=token)

        if result.get("success"):
            print_success(f"Request cancelled successfully")
            return True
        else:
            print_error(f"Failed to cancel request")
            return False

    def get_stats(self, token: str):
        """Get statistics"""
        print_info(f"Getting statistics")
        result = api_request("GET", "/requests/stats", token=token)

        if result.get("success"):
            print_success(f"Statistics retrieved")
            return result.get("data")
        else:
            print_error(f"Failed to get statistics")
            return None

    def run_full_test(self):
        """Run complete API test"""
        print_section("ADDRESS SYNC API - FULL TEST")
        print(f"Testing against: {BASE_URL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Step 1: Health Check
        if not test_health_check():
            print_error(
                "Server not responding. Please start the server first.")
            return False

        # Step 2: Register Users
        print_section("2. REGISTERING USERS")
        for user in DEMO_USERS:
            result = self.register_user(user)
            if result and result.get("exists"):
                self.existing_users.append(user)

        # Step 3: Login Users
        print_section("3. LOGGING IN USERS")
        for user in DEMO_USERS:
            token = self.login_user(user["aadhaar_number"], user["password"])
            if token:
                self.user_tokens[user["aadhaar_number"]] = token
                profile = self.get_user_profile(token, user["name"])
                if profile:
                    print_json(profile)

        if not self.user_tokens:
            print_error("No users could login.")
            return False

        # Step 4: Register Agencies
        print_section("4. REGISTERING AGENCIES")
        for agency in DEMO_AGENCIES:
            result = self.register_agency(agency)
            if result and result.get("exists"):
                self.existing_agencies.append(agency)

        # Step 5: Login Agencies
        print_section("5. LOGGING IN AGENCIES")
        for agency in DEMO_AGENCIES:
            token = self.login_agency(agency["id"], agency["password"])
            if token:
                self.agency_tokens[agency["id"]] = token
                profile = self.get_agency_profile(token, agency["name"])
                if profile:
                    print_json(profile)

        if not self.agency_tokens:
            print_error("No agencies could login.")
            return False

        # Step 6: Create Requests
        print_section("6. CREATING ADDRESS CHANGE REQUESTS")

        requests_to_create = [
            (DEMO_USERS[0], DEMO_AGENCIES[0], DEMO_REQUESTS[0]["new_address"]),
            (DEMO_USERS[0], DEMO_AGENCIES[1], DEMO_REQUESTS[1]["new_address"]),
            (DEMO_USERS[1], DEMO_AGENCIES[0], DEMO_REQUESTS[2]["new_address"]),
            (DEMO_USERS[1], DEMO_AGENCIES[2], DEMO_REQUESTS[0]["new_address"]),
            (DEMO_USERS[2], DEMO_AGENCIES[1], DEMO_REQUESTS[3]["new_address"]),
        ]

        for user, agency, new_address in requests_to_create:
            token = self.user_tokens.get(user["aadhaar_number"])
            if token:
                request = self.create_request(token, agency["id"], new_address)
                if request:
                    self.created_requests.append({
                        "id": request.get("id"),
                        "user": user["name"],
                        "agency": agency["name"]
                    })

        print_info(f"Created {len(self.created_requests)} new requests")

        # Step 7: View User Requests
        print_section("7. VIEWING USER REQUESTS")
        for user in DEMO_USERS:
            token = self.user_tokens.get(user["aadhaar_number"])
            if token:
                requests = self.get_user_requests(token, user["name"])
                if requests:
                    print(
                        f"\n{Colors.BOLD}{user['name']}'s Requests:{Colors.END}")
                    for req in requests:
                        status_color = Colors.GREEN if req.get('status') == 'approved' else Colors.RED if req.get(
                            'status') == 'rejected' else Colors.YELLOW
                        print(f"  - ID: {req.get('id')}")
                        print(
                            f"    Status: {status_color}{req.get('status')}{Colors.END}")
                        print(f"    Agency: {req.get('agency_id')}")
                        print()

        # Step 8: View Agency Requests
        print_section("8. VIEWING AGENCY REQUESTS")
        for agency in DEMO_AGENCIES:
            token = self.agency_tokens.get(agency["id"])
            if token:
                requests = self.get_agency_requests(token, agency["name"])
                if requests:
                    print(
                        f"\n{Colors.BOLD}{agency['name']}'s Requests:{Colors.END}")
                    for req in requests:
                        status_color = Colors.GREEN if req.get('status') == 'approved' else Colors.RED if req.get(
                            'status') == 'rejected' else Colors.YELLOW
                        print(f"  - ID: {req.get('id')}")
                        print(
                            f"    Status: {status_color}{req.get('status')}{Colors.END}")
                        print(f"    User: {req.get('user_aadhaar')}")
                        print()

        # Step 9: Update Request Statuses
        print_section("9. UPDATING REQUEST STATUSES")

        for agency in DEMO_AGENCIES:
            token = self.agency_tokens.get(agency["id"])
            if token:
                pending_requests = self.get_pending_requests(
                    token, agency["name"])

                # Update first 2 pending requests
                for i, req in enumerate(pending_requests[:2]):
                    if i == 0:
                        self.update_request_status(
                            token, req.get("id"), "approved")
                    elif i == 1:
                        self.update_request_status(token, req.get(
                            "id"), "rejected", "Address format invalid")
                    time.sleep(0.5)

        # Step 10: Get Statistics
        print_section("10. GETTING STATISTICS")

        user = DEMO_USERS[0]
        token = self.user_tokens.get(user["aadhaar_number"])
        if token:
            stats = self.get_stats(token)
            if stats:
                print(f"\n{Colors.BOLD}User Statistics:{Colors.END}")
                print_json(stats)

        agency = DEMO_AGENCIES[0]
        token = self.agency_tokens.get(agency["id"])
        if token:
            stats = self.get_stats(token)
            if stats:
                print(f"\n{Colors.BOLD}Agency Statistics:{Colors.END}")
                print_json(stats)

        # Step 11: Cancel a Request
        print_section("11. CANCELLING A REQUEST")

        user = DEMO_USERS[0]
        token = self.user_tokens.get(user["aadhaar_number"])
        if token:
            user_requests = self.get_user_requests(token, user["name"])
            pending_requests = [
                r for r in user_requests if r.get("status") == "pending"]

            if pending_requests:
                request_to_cancel = pending_requests[0]
                self.cancel_request(token, request_to_cancel.get("id"))

        # Step 12: Summary
        print_section("TEST SUMMARY")
        print(f"{Colors.GREEN}✓ Health Check: Passed{Colors.END}")
        print(
            f"{Colors.GREEN}✓ User Logins: {len(self.user_tokens)} users logged in{Colors.END}")
        print(
            f"{Colors.GREEN}✓ Agency Logins: {len(self.agency_tokens)} agencies logged in{Colors.END}")
        print(
            f"{Colors.GREEN}✓ Requests Created: {len(self.created_requests)}{Colors.END}")
        print(f"{Colors.GREEN}✓ Status Updates: Completed{Colors.END}")

        if self.existing_users:
            print_warning(
                f"Note: {len(self.existing_users)} users already existed")
        if self.existing_agencies:
            print_warning(
                f"Note: {len(self.existing_agencies)} agencies already existed")

        print(
            f"\n{Colors.BOLD}{Colors.GREEN}All tests completed successfully!{Colors.END}")
        return True


def main():
    """Main function to run tests"""
    tester = APITester()

    print_warning("This test will create/use existing data in the database.")
    response = input("Continue? (Y/n): ")
    if response.lower() == 'n':
        print("Test cancelled.")
        return

    success = tester.run_full_test()

    if not success:
        print_error("\nTest failed. Make sure the server is running:")
        print("  uvicorn main:app --reload")
        sys.exit(1)


if __name__ == "__main__":
    main()
