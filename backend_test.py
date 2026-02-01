import requests
import sys
import json
from datetime import datetime
import time

class TacticalServerControlPanelTester:
    def __init__(self, base_url="https://tacticalpanel.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.sub_admin_token = None
        self.admin_username = None
        self.sub_admin_username = None
        self.sub_admin_id = None
        self.server_id = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.critical_failures = []

    def log_test(self, name, success, details="", is_critical=False):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
            if is_critical:
                self.critical_failures.append(f"{name}: {details}")
        
        self.test_results.append({
            "test": name,
            "success": success,
            "details": details,
            "critical": is_critical
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=True):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)

            success = response.status_code == expected_status
            
            if success:
                self.log_test(name, True)
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_detail = response.json().get('detail', '')
                    if error_detail:
                        error_msg += f" - {error_detail}"
                except:
                    pass
                self.log_test(name, False, error_msg)
                return False, {}

        except requests.exceptions.RequestException as e:
            self.log_test(name, False, f"Request error: {str(e)}")
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Unexpected error: {str(e)}")
            return False, {}

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        self.username = f"test_user_{timestamp}"
        password = "TestPass123!"
        
        success, response = self.run_test(
            "User Registration",
            "POST",
            "auth/register",
            200,
            data={"username": self.username, "password": password},
            auth_required=False
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_user_login(self):
        """Test user login with existing credentials"""
        if not self.username:
            return False
            
        success, response = self.run_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"username": self.username, "password": "TestPass123!"},
            auth_required=False
        )
        
        if success and 'access_token' in response:
            self.token = response['access_token']
            return True
        return False

    def test_system_resources(self):
        """Test system resources endpoint"""
        success, response = self.run_test(
            "System Resources",
            "GET",
            "system/resources",
            200
        )
        
        if success:
            required_fields = ['cpu_percent', 'memory_percent', 'disk_percent']
            for field in required_fields:
                if field not in response:
                    self.log_test(f"System Resources - {field} field", False, f"Missing {field}")
                    return False
            return True
        return False

    def test_steamcmd_status(self):
        """Test SteamCMD status endpoint"""
        success, response = self.run_test(
            "SteamCMD Status",
            "GET",
            "steamcmd/status",
            200
        )
        
        if success:
            if 'installed' not in response:
                self.log_test("SteamCMD Status - installed field", False, "Missing installed field")
                return False
            return True
        return False

    def test_server_crud_operations(self):
        """Test server CRUD operations"""
        # Test create server
        server_data = {
            "name": "Test Arma Server",
            "game_type": "arma_reforger",
            "port": 2001,
            "max_players": 64,
            "install_path": "/home/steamcmd/servers/test"
        }
        
        success, response = self.run_test(
            "Create Server Instance",
            "POST",
            "servers",
            200,
            data=server_data
        )
        
        if not success:
            return False
            
        server_id = response.get('id')
        if not server_id:
            self.log_test("Create Server - ID field", False, "Missing server ID in response")
            return False

        # Test get servers
        success, servers = self.run_test(
            "Get Server Instances",
            "GET",
            "servers",
            200
        )
        
        if not success or not isinstance(servers, list):
            return False

        # Test get specific server
        success, server = self.run_test(
            "Get Specific Server",
            "GET",
            f"servers/{server_id}",
            200
        )
        
        if not success:
            return False

        # Test update server
        update_data = {"current_players": 5}
        success, updated_server = self.run_test(
            "Update Server Instance",
            "PATCH",
            f"servers/{server_id}",
            200,
            data=update_data
        )
        
        if not success:
            return False

        # Test server control operations
        for action in ["start", "stop", "restart"]:
            success, _ = self.run_test(
                f"Server {action.title()}",
                "POST",
                f"servers/{server_id}/{action}",
                200
            )
            if not success:
                return False

        # Test delete server
        success, _ = self.run_test(
            "Delete Server Instance",
            "DELETE",
            f"servers/{server_id}",
            200
        )
        
        return success

    def test_steamcmd_install(self):
        """Test SteamCMD installation"""
        success, response = self.run_test(
            "SteamCMD Install",
            "POST",
            "steamcmd/install",
            200
        )
        return success

    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Arma Server Panel Backend Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 60)

        # Authentication tests
        if not self.test_user_registration():
            print("❌ Registration failed, stopping tests")
            return False

        if not self.test_user_login():
            print("❌ Login failed, stopping tests")
            return False

        # System tests
        self.test_system_resources()
        self.test_steamcmd_status()
        
        # Server management tests
        self.test_server_crud_operations()
        
        # SteamCMD install test
        self.test_steamcmd_install()

        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Backend Tests Summary:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All backend tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

def main():
    tester = ArmaServerPanelTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())