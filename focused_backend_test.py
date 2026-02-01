#!/usr/bin/env python3
"""
Focused Backend Test for Tactical Reforger Control Panel
Testing the NEW FEATURES added in this session as requested in the review.
"""

import requests
import json
import sys
from datetime import datetime

class FocusedTacticalTester:
    def __init__(self):
        self.base_url = "https://reforgerctl.preview.emergentagent.com"
        self.api_url = f"{self.base_url}/api"
        self.admin_token = None
        self.sub_admin_token = None
        self.sub_admin_id = None
        self.server_id = None
        self.test_results = []
        
    def log_result(self, test_name, success, details=""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} | {test_name}")
        if details:
            print(f"      {details}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        return success
    
    def make_request(self, method, endpoint, data=None, token=None, expected_status=200):
        """Make API request"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=10)
            
            success = response.status_code == expected_status
            
            try:
                response_data = response.json()
            except:
                response_data = {}
            
            if not success:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                if response_data.get('detail'):
                    error_msg += f" - {response_data['detail']}"
                return False, error_msg, response_data
            
            return True, "Success", response_data
            
        except Exception as e:
            return False, f"Request error: {str(e)}", {}
    
    def setup_admin_credentials(self):
        """Setup admin credentials for testing"""
        print("🔐 Setting up admin credentials...")
        
        # Try to create admin via first-time setup if needed
        success, msg, response = self.make_request('GET', 'auth/check-first-run', expected_status=200)
        if not success:
            return self.log_result("Check First Run", False, msg)
        
        is_first_run = response.get('is_first_run', False)
        
        if is_first_run:
            # Create first admin
            admin_data = {
                "username": "testadmin",
                "password": "TestPass123!",
                "security_questions": {
                    "question1": "blue",
                    "question2": "paris",
                    "question3": "fluffy", 
                    "question4": "smith"
                }
            }
            
            success, msg, response = self.make_request('POST', 'auth/first-time-setup', admin_data, expected_status=200)
            if success and 'access_token' in response:
                self.admin_token = response['access_token']
                return self.log_result("First-Time Admin Setup", True, f"Created admin: testadmin")
            else:
                return self.log_result("First-Time Admin Setup", False, msg)
        else:
            # Try to register a new admin user first
            timestamp = datetime.now().strftime('%H%M%S')
            new_admin_data = {
                "username": f"testadmin_{timestamp}",
                "password": "TestPass123!",
                "security_questions": {
                    "question1": "blue",
                    "question2": "paris",
                    "question3": "fluffy", 
                    "question4": "smith"
                }
            }
            
            success, msg, response = self.make_request('POST', 'auth/register', new_admin_data, expected_status=200)
            if success and 'access_token' in response:
                self.admin_token = response['access_token']
                
                # Now we need to make this user an admin in the database
                # Since we can't do that via API, let's try existing admin credentials
                print(f"   Registered user: {new_admin_data['username']}, but need admin privileges...")
                
            # Try to login with existing admin credentials
            admin_credentials = [
                {"username": "testadmin", "password": "TestPass123!"},
                {"username": "admin", "password": "admin123"},
                {"username": "admin", "password": "TestPass123!"},
                {"username": "testadmin_backend", "password": "AdminPass123!"}
            ]
            
            for creds in admin_credentials:
                success, msg, response = self.make_request('POST', 'auth/login', creds, expected_status=200)
                if success and 'access_token' in response:
                    self.admin_token = response['access_token']
                    return self.log_result("Admin Login", True, f"Logged in as: {creds['username']}")
            
            # If we have a token from registration, use it but note it might not have admin privileges
            if self.admin_token:
                return self.log_result("User Login", True, f"Logged in as regular user: {new_admin_data['username']}")
            
            return self.log_result("Admin Login", False, "Could not login with any admin credentials")
    
    def test_authentication_flow(self):
        """Test 1: Authentication Flow"""
        print("\n📋 TEST 1: Authentication Flow")
        print("-" * 40)
        
        # Test JWT token is returned
        if not self.admin_token:
            return self.log_result("JWT Token Received", False, "No admin token available")
        
        # Test token works for protected endpoint
        success, msg, response = self.make_request('GET', 'system/resources', token=self.admin_token)
        if success:
            return self.log_result("JWT Token Valid", True, "Token works for protected endpoints")
        else:
            return self.log_result("JWT Token Valid", False, msg)
    
    def test_sub_admin_management(self):
        """Test 2: Sub-Admin Management (NEW FEATURE)"""
        print("\n👥 TEST 2: Sub-Admin Management (NEW FEATURE)")
        print("-" * 50)
        
        if not self.admin_token:
            return self.log_result("Sub-Admin Tests", False, "No admin token available")
        
        # Test creating sub-admin
        timestamp = datetime.now().strftime('%H%M%S')
        sub_admin_data = {
            "username": f"subadmin_{timestamp}",
            "password": "SubPass123!",
            "server_permissions": {
                "test_server": {
                    "view": True,
                    "edit": False,
                    "start": True,
                    "stop": True,
                    "restart": False
                }
            }
        }
        
        success, msg, response = self.make_request('POST', 'admin/sub-admins', sub_admin_data, token=self.admin_token)
        if success and 'id' in response:
            self.sub_admin_id = response['id']
            self.log_result("Create Sub-Admin", True, f"Created sub-admin: {sub_admin_data['username']}")
        else:
            return self.log_result("Create Sub-Admin", False, msg)
        
        # Test listing sub-admins
        success, msg, response = self.make_request('GET', 'admin/sub-admins', token=self.admin_token)
        if success and isinstance(response, list):
            self.log_result("List Sub-Admins", True, f"Found {len(response)} sub-admins")
        else:
            self.log_result("List Sub-Admins", False, msg)
        
        # Test getting specific sub-admin
        if self.sub_admin_id:
            success, msg, response = self.make_request('GET', f'admin/sub-admins/{self.sub_admin_id}', token=self.admin_token)
            if success and response.get('username') == sub_admin_data['username']:
                self.log_result("Get Specific Sub-Admin", True, "Retrieved sub-admin details")
            else:
                self.log_result("Get Specific Sub-Admin", False, msg)
        
        # Test updating sub-admin permissions
        if self.sub_admin_id:
            update_data = {
                "server_permissions": {
                    "test_server": {
                        "view": True,
                        "edit": True,
                        "start": True,
                        "stop": True,
                        "restart": True
                    }
                }
            }
            
            success, msg, response = self.make_request('PUT', f'admin/sub-admins/{self.sub_admin_id}', update_data, token=self.admin_token)
            if success:
                self.log_result("Update Sub-Admin Permissions", True, "Updated permissions successfully")
            else:
                self.log_result("Update Sub-Admin Permissions", False, msg)
        
        # Test sub-admin login
        sub_admin_login = {
            "username": sub_admin_data['username'],
            "password": sub_admin_data['password']
        }
        
        success, msg, response = self.make_request('POST', 'auth/login', sub_admin_login, expected_status=200)
        if success and 'access_token' in response:
            self.sub_admin_token = response['access_token']
            self.log_result("Sub-Admin Login", True, "Sub-admin can login successfully")
        else:
            self.log_result("Sub-Admin Login", False, msg)
        
        # Test permission enforcement - sub-admin should NOT access admin endpoints
        if self.sub_admin_token:
            success, msg, response = self.make_request('GET', 'admin/sub-admins', token=self.sub_admin_token, expected_status=403)
            if success:
                self.log_result("Sub-Admin Permission Enforcement", True, "Sub-admin correctly denied admin access")
            else:
                self.log_result("Sub-Admin Permission Enforcement", False, f"Expected 403, got different response: {msg}")
        
        # Test deleting sub-admin
        if self.sub_admin_id:
            success, msg, response = self.make_request('DELETE', f'admin/sub-admins/{self.sub_admin_id}', token=self.admin_token)
            if success:
                self.log_result("Delete Sub-Admin", True, "Sub-admin deleted successfully")
            else:
                self.log_result("Delete Sub-Admin", False, msg)
    
    def test_resource_management(self):
        """Test 3: Resource Management (NEW FEATURE)"""
        print("\n💾 TEST 3: Resource Management (NEW FEATURE)")
        print("-" * 50)
        
        if not self.admin_token:
            return self.log_result("Resource Management Tests", False, "No admin token available")
        
        # Test creating server with resource allocations
        server_data = {
            "name": "Test Tactical Server",
            "game_type": "arma_reforger",
            "port": 2302,
            "max_players": 64,
            "install_path": "/tmp/test_server",
            "cpu_cores": 4,
            "ram_gb": 8,
            "storage_gb": 100,
            "network_speed_mbps": 1000
        }
        
        success, msg, response = self.make_request('POST', 'servers', server_data, token=self.admin_token)
        if success and 'id' in response:
            self.server_id = response['id']
            
            # Verify resource fields are present
            resource_fields = ['cpu_cores', 'ram_gb', 'storage_gb', 'network_speed_mbps']
            missing_fields = [field for field in resource_fields if field not in response]
            
            if not missing_fields:
                self.log_result("Create Server with Resources", True, f"Server created with all resource fields")
            else:
                self.log_result("Create Server with Resources", False, f"Missing resource fields: {missing_fields}")
        else:
            return self.log_result("Create Server with Resources", False, msg)
        
        # Test updating server resources
        if self.server_id:
            resource_updates = {
                "cpu_cores": 6,
                "ram_gb": 16,
                "storage_gb": 200,
                "network_speed_mbps": 2000
            }
            
            success, msg, response = self.make_request('PATCH', f'servers/{self.server_id}', resource_updates, token=self.admin_token)
            if success:
                # Verify updated values
                all_updated = True
                for field, expected_value in resource_updates.items():
                    if response.get(field) != expected_value:
                        all_updated = False
                        break
                
                if all_updated:
                    self.log_result("Update Server Resources", True, "All resource fields updated correctly")
                else:
                    self.log_result("Update Server Resources", False, "Resource values not updated correctly")
            else:
                self.log_result("Update Server Resources", False, msg)
        
        # Test resource persistence - get server and verify resources
        if self.server_id:
            success, msg, response = self.make_request('GET', f'servers/{self.server_id}', token=self.admin_token)
            if success:
                resource_fields = ['cpu_cores', 'ram_gb', 'storage_gb', 'network_speed_mbps']
                has_resources = all(field in response for field in resource_fields)
                
                if has_resources:
                    self.log_result("Resource Persistence", True, "Resource fields persisted in database")
                else:
                    self.log_result("Resource Persistence", False, "Resource fields not persisted")
            else:
                self.log_result("Resource Persistence", False, msg)
    
    def test_server_management(self):
        """Test 4: Server Management"""
        print("\n🖥️  TEST 4: Server Management")
        print("-" * 40)
        
        if not self.admin_token:
            return self.log_result("Server Management Tests", False, "No admin token available")
        
        # Test listing servers
        success, msg, response = self.make_request('GET', 'servers', token=self.admin_token)
        if success and isinstance(response, list):
            self.log_result("List Servers", True, f"Retrieved {len(response)} servers")
        else:
            self.log_result("List Servers", False, msg)
        
        # Test getting single server
        if self.server_id:
            success, msg, response = self.make_request('GET', f'servers/{self.server_id}', token=self.admin_token)
            if success and response.get('id') == self.server_id:
                self.log_result("Get Single Server", True, "Retrieved server details")
            else:
                self.log_result("Get Single Server", False, msg)
        
        # Test updating server (non-resource fields)
        if self.server_id:
            update_data = {
                "name": "Updated Tactical Server",
                "max_players": 128
            }
            
            success, msg, response = self.make_request('PATCH', f'servers/{self.server_id}', update_data, token=self.admin_token)
            if success:
                self.log_result("Update Server", True, "Server updated successfully")
            else:
                self.log_result("Update Server", False, msg)
        
        # Test deleting server
        if self.server_id:
            success, msg, response = self.make_request('DELETE', f'servers/{self.server_id}', token=self.admin_token)
            if success:
                self.log_result("Delete Server", True, "Server deleted successfully")
            else:
                self.log_result("Delete Server", False, msg)
    
    def test_system_resources(self):
        """Test 5: System Resources"""
        print("\n⚙️  TEST 5: System Resources")
        print("-" * 40)
        
        if not self.admin_token:
            return self.log_result("System Resources Test", False, "No admin token available")
        
        success, msg, response = self.make_request('GET', 'system/resources', token=self.admin_token)
        if success:
            required_fields = ['cpu_percent', 'memory_percent', 'memory_used_gb', 'memory_total_gb', 
                             'disk_percent', 'disk_used_gb', 'disk_total_gb']
            missing_fields = [field for field in required_fields if field not in response]
            
            if not missing_fields:
                self.log_result("System Resources", True, "All required fields present")
            else:
                self.log_result("System Resources", False, f"Missing fields: {missing_fields}")
        else:
            self.log_result("System Resources", False, msg)
    
    def test_security_features(self):
        """Test 6: Security Features"""
        print("\n🔒 TEST 6: Security Features")
        print("-" * 40)
        
        # Test unauthorized access returns 401
        success, msg, response = self.make_request('GET', 'system/resources', expected_status=401)
        if success:
            self.log_result("Unauthorized Access Denied", True, "Returns 401 for unauthenticated requests")
        else:
            self.log_result("Unauthorized Access Denied", False, msg)
        
        # Test invalid token returns 401
        success, msg, response = self.make_request('GET', 'system/resources', token="invalid.jwt.token", expected_status=401)
        if success:
            self.log_result("Invalid Token Rejected", True, "Returns 401 for invalid tokens")
        else:
            self.log_result("Invalid Token Rejected", False, msg)
    
    def run_focused_tests(self):
        """Run focused tests on NEW FEATURES"""
        print("🎯 FOCUSED BACKEND TESTING - NEW FEATURES")
        print("=" * 60)
        print("Testing: Authentication, Sub-Admin Management, Resource Management")
        print("=" * 60)
        
        # Setup
        if not self.setup_admin_credentials():
            print("\n❌ Cannot proceed without admin credentials")
            return False
        
        # Run focused tests
        self.test_authentication_flow()
        self.test_sub_admin_management()
        self.test_resource_management()
        self.test_server_management()
        self.test_system_resources()
        self.test_security_features()
        
        # Results
        print("\n" + "=" * 60)
        print("📊 FOCUSED TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['success']])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ FAILED TESTS ({failed_tests}):")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['details']}")
        
        if passed_tests == total_tests:
            print("\n🎉 ALL NEW FEATURES WORKING PERFECTLY!")
            return True
        else:
            print(f"\n⚠️  {failed_tests} issues found in new features")
            return False

def main():
    tester = FocusedTacticalTester()
    success = tester.run_focused_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())