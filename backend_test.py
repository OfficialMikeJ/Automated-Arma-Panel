import requests
import sys
import json
from datetime import datetime
import time

class TacticalServerControlPanelTester:
    def __init__(self, base_url="https://reforgerctl.preview.emergentagent.com"):
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

    def run_test(self, name, method, endpoint, expected_status, data=None, auth_required=True, is_critical=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if auth_required and self.admin_token:
            headers['Authorization'] = f'Bearer {self.admin_token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
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
            
            if success:
                self.log_test(name, True, is_critical=is_critical)
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
                self.log_test(name, False, error_msg, is_critical=is_critical)
                return False, {}

        except requests.exceptions.RequestException as e:
            self.log_test(name, False, f"Request error: {str(e)}", is_critical=is_critical)
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Unexpected error: {str(e)}", is_critical=is_critical)
            return False, {}

    def run_test_with_token(self, name, method, endpoint, expected_status, data=None, token=None, is_critical=False):
        """Run a test with specific token"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
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
            
            if success:
                self.log_test(name, True, is_critical=is_critical)
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
                self.log_test(name, False, error_msg, is_critical=is_critical)
                return False, {}

        except requests.exceptions.RequestException as e:
            self.log_test(name, False, f"Request error: {str(e)}", is_critical=is_critical)
            return False, {}
        except Exception as e:
            self.log_test(name, False, f"Unexpected error: {str(e)}", is_critical=is_critical)
            return False, {}

    # ========== AUTHENTICATION & USER MANAGEMENT TESTS ==========
    
    def test_check_first_run(self):
        """Test first run check"""
        success, response = self.run_test(
            "Check First Run",
            "GET",
            "auth/check-first-run",
            200,
            auth_required=False,
            is_critical=True
        )
        return success and isinstance(response.get('is_first_run'), bool)

    def test_password_config(self):
        """Test password configuration endpoint"""
        success, response = self.run_test(
            "Password Configuration",
            "GET",
            "auth/password-config",
            200,
            auth_required=False,
            is_critical=True
        )
        
        if success:
            required_fields = ['min_length', 'require_uppercase', 'require_lowercase', 'require_numbers', 'require_special']
            for field in required_fields:
                if field not in response:
                    self.log_test(f"Password Config - {field} field", False, f"Missing {field}", is_critical=True)
                    return False
            return True
        return False

    def test_first_time_setup(self):
        """Test first-time admin setup or skip if admin exists"""
        # First check if this is actually first run
        success, response = self.run_test(
            "Check First Run Status",
            "GET",
            "auth/check-first-run",
            200,
            auth_required=False,
            is_critical=True
        )
        
        if not success:
            return False
            
        is_first_run = response.get('is_first_run', False)
        
        if not is_first_run:
            # Admin already exists, skip first-time setup
            print("   ℹ️  Admin user already exists, skipping first-time setup")
            # Try common admin credentials
            self.admin_username = "admin"  # Try common username
            return True
        
        timestamp = datetime.now().strftime('%H%M%S')
        self.admin_username = f"admin_{timestamp}"
        
        setup_data = {
            "username": self.admin_username,
            "password": "AdminPass123!",
            "security_questions": {
                "question1": "What is your favorite color?",
                "question2": "What city were you born in?", 
                "question3": "What is your pet's name?",
                "question4": "What is your mother's maiden name?"
            }
        }
        
        success, response = self.run_test(
            "First Time Setup",
            "POST",
            "auth/first-time-setup",
            200,
            data=setup_data,
            auth_required=False,
            is_critical=True
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            return True
        return False

    def test_admin_login(self):
        """Test admin login"""
        # First try to register a test admin user
        timestamp = datetime.now().strftime('%H%M%S')
        test_username = f"testadmin_{timestamp}"
        
        register_data = {
            "username": test_username,
            "password": "AdminPass123!",
            "security_questions": {
                "question1": "blue",
                "question2": "paris", 
                "question3": "fluffy",
                "question4": "smith"
            }
        }
        
        success, response = self.run_test(
            "Register Test Admin",
            "POST",
            "auth/register",
            200,
            data=register_data,
            auth_required=False,
            is_critical=False
        )
        
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            self.admin_username = test_username
            print(f"   ✅ Successfully registered and logged in as {test_username}")
            return True
        
        # If registration failed, try existing credentials
        admin_credentials = [
            {"username": "admin", "password": "admin123"},
            {"username": "admin", "password": "AdminPass123!"},
            {"username": "testadmin_backend", "password": "AdminPass123!"}
        ]
        
        for creds in admin_credentials:
            success, response = self.run_test(
                f"Admin Login ({creds['username']})",
                "POST",
                "auth/login",
                200,
                data=creds,
                auth_required=False,
                is_critical=False
            )
            
            if success and 'access_token' in response:
                self.admin_token = response['access_token']
                self.admin_username = creds['username']
                print(f"   ✅ Successfully logged in as {creds['username']}")
                return True
        
        # If all failed, mark as critical failure
        self.log_test("Admin Login", False, "Could not login with any admin credentials", is_critical=True)
        return False

    def test_totp_setup_flow(self):
        """Test TOTP setup and verification flow"""
        # Setup TOTP
        success, response = self.run_test(
            "TOTP Setup",
            "POST",
            "auth/totp/setup",
            200,
            is_critical=False
        )
        
        if not success:
            return False
            
        # Check TOTP status
        success, status_response = self.run_test(
            "TOTP Status Check",
            "GET",
            "auth/totp/status",
            200,
            is_critical=False
        )
        
        return success

    def test_password_reset_flow(self):
        """Test password reset with security questions"""
        # First get security questions
        success, response = self.run_test(
            "Get Security Questions",
            "GET",
            f"auth/security-questions/{self.admin_username}",
            200,
            auth_required=False,
            is_critical=False
        )
        
        if not success:
            return False
            
        # Test password reset
        reset_data = {
            "username": self.admin_username,
            "answer1": "blue",
            "answer2": "paris", 
            "answer3": "fluffy",
            "answer4": "smith",
            "new_password": "NewAdminPass123!"
        }
        
        success, response = self.run_test(
            "Password Reset",
            "POST",
            "auth/reset-password",
            200,
            data=reset_data,
            auth_required=False,
            is_critical=False
        )
        
        return success

    # ========== SUB-ADMIN USER SYSTEM TESTS ==========
    
    def test_create_sub_admin(self):
        """Test creating a sub-admin user"""
        timestamp = datetime.now().strftime('%H%M%S')
        self.sub_admin_username = f"subadmin_{timestamp}"
        
        sub_admin_data = {
            "username": self.sub_admin_username,
            "password": "SubAdminPass123!",
            "server_permissions": {
                "server_1": {
                    "view": True,
                    "edit": False,
                    "start": True,
                    "stop": True,
                    "restart": False
                }
            }
        }
        
        success, response = self.run_test(
            "Create Sub-Admin",
            "POST",
            "admin/sub-admins",
            200,
            data=sub_admin_data,
            is_critical=True
        )
        
        if success and 'id' in response:
            self.sub_admin_id = response['id']
            return True
        return False

    def test_list_sub_admins(self):
        """Test listing sub-admins"""
        success, response = self.run_test(
            "List Sub-Admins",
            "GET",
            "admin/sub-admins",
            200,
            is_critical=True
        )
        
        return success and isinstance(response, list)

    def test_get_sub_admin(self):
        """Test getting specific sub-admin"""
        if not self.sub_admin_id:
            return False
            
        success, response = self.run_test(
            "Get Specific Sub-Admin",
            "GET",
            f"admin/sub-admins/{self.sub_admin_id}",
            200,
            is_critical=True
        )
        
        return success and response.get('username') == self.sub_admin_username

    def test_update_sub_admin(self):
        """Test updating sub-admin permissions"""
        if not self.sub_admin_id:
            return False
            
        update_data = {
            "server_permissions": {
                "server_1": {
                    "view": True,
                    "edit": True,
                    "start": True,
                    "stop": True,
                    "restart": True
                }
            }
        }
        
        success, response = self.run_test(
            "Update Sub-Admin Permissions",
            "PUT",
            f"admin/sub-admins/{self.sub_admin_id}",
            200,
            data=update_data,
            is_critical=True
        )
        
        return success

    def test_sub_admin_login(self):
        """Test sub-admin login"""
        if not self.sub_admin_username:
            return False
            
        success, response = self.run_test(
            "Sub-Admin Login",
            "POST",
            "auth/login",
            200,
            data={"username": self.sub_admin_username, "password": "SubAdminPass123!"},
            auth_required=False,
            is_critical=True
        )
        
        if success and 'access_token' in response:
            self.sub_admin_token = response['access_token']
            return True
        return False

    # ========== SERVER MANAGEMENT TESTS ==========
    
    def test_create_server_with_resources(self):
        """Test creating server with resource allocations"""
        server_data = {
            "name": "Tactical Arma Server",
            "game_type": "arma_reforger",
            "port": 2302,
            "max_players": 64,
            "install_path": "/home/steamcmd/servers/tactical",
            "cpu_cores": 4,
            "ram_gb": 8,
            "storage_gb": 100,
            "network_speed_mbps": 1000
        }
        
        success, response = self.run_test(
            "Create Server with Resources",
            "POST",
            "servers",
            200,
            data=server_data,
            is_critical=True
        )
        
        if success and 'id' in response:
            self.server_id = response['id']
            # Verify resource fields are present
            resource_fields = ['cpu_cores', 'ram_gb', 'storage_gb', 'network_speed_mbps']
            for field in resource_fields:
                if field not in response:
                    self.log_test(f"Server Creation - {field} field", False, f"Missing {field}", is_critical=True)
                    return False
            return True
        return False

    def test_list_servers(self):
        """Test listing servers"""
        success, response = self.run_test(
            "List Servers",
            "GET",
            "servers",
            200,
            is_critical=True
        )
        
        return success and isinstance(response, list)

    def test_get_server(self):
        """Test getting specific server"""
        if not self.server_id:
            return False
            
        success, response = self.run_test(
            "Get Specific Server",
            "GET",
            f"servers/{self.server_id}",
            200,
            is_critical=True
        )
        
        return success and response.get('id') == self.server_id

    def test_update_server_resources(self):
        """Test updating server resources"""
        if not self.server_id:
            return False
            
        update_data = {
            "cpu_cores": 6,
            "ram_gb": 16,
            "storage_gb": 200,
            "network_speed_mbps": 2000
        }
        
        success, response = self.run_test(
            "Update Server Resources",
            "PATCH",
            f"servers/{self.server_id}",
            200,
            data=update_data,
            is_critical=True
        )
        
        if success:
            # Verify updated values
            for field, expected_value in update_data.items():
                if response.get(field) != expected_value:
                    self.log_test(f"Resource Update - {field}", False, f"Expected {expected_value}, got {response.get(field)}", is_critical=True)
                    return False
            return True
        return False

    def test_server_control_operations(self):
        """Test server start/stop/restart operations"""
        if not self.server_id:
            return False
            
        operations = ["start", "stop", "restart"]
        for operation in operations:
            success, response = self.run_test(
                f"Server {operation.title()}",
                "POST",
                f"servers/{self.server_id}/{operation}",
                200,
                is_critical=True
            )
            if not success:
                return False
            
            # Small delay between operations
            time.sleep(1)
        
        return True

    def test_server_config_management(self):
        """Test server configuration management"""
        if not self.server_id:
            return False
            
        # Get server config
        success, response = self.run_test(
            "Get Server Config",
            "GET",
            f"servers/{self.server_id}/config",
            200,
            is_critical=False
        )
        
        if not success:
            return False
            
        # Update server config
        config_data = {
            "content": "// Updated server configuration\nhostname = \"Updated Tactical Server\";"
        }
        
        success, response = self.run_test(
            "Update Server Config",
            "PUT",
            f"servers/{self.server_id}/config",
            200,
            data=config_data,
            is_critical=False
        )
        
        return success

    def test_server_mod_management(self):
        """Test server mod management"""
        if not self.server_id:
            return False
            
        # Add mod
        mod_data = {
            "workshop_id": "2582780947",
            "name": "Enhanced Movement",
            "enabled": True
        }
        
        success, response = self.run_test(
            "Add Server Mod",
            "POST",
            f"servers/{self.server_id}/mods",
            200,
            data=mod_data,
            is_critical=False
        )
        
        if not success:
            return False
            
        mod_id = response.get('id')
        if not mod_id:
            return False
            
        # List mods
        success, response = self.run_test(
            "List Server Mods",
            "GET",
            f"servers/{self.server_id}/mods",
            200,
            is_critical=False
        )
        
        if not success:
            return False
            
        # Toggle mod
        success, response = self.run_test(
            "Toggle Server Mod",
            "PATCH",
            f"servers/{self.server_id}/mods/{mod_id}/toggle",
            200,
            is_critical=False
        )
        
        if not success:
            return False
            
        # Delete mod
        success, response = self.run_test(
            "Delete Server Mod",
            "DELETE",
            f"servers/{self.server_id}/mods/{mod_id}",
            200,
            is_critical=False
        )
        
        return success

    def test_server_logs(self):
        """Test server log viewing"""
        if not self.server_id:
            return False
            
        success, response = self.run_test(
            "Get Server Logs",
            "GET",
            f"servers/{self.server_id}/logs?lines=50",
            200,
            is_critical=False
        )
        
        return success and 'logs' in response

    # ========== SYSTEM RESOURCES TESTS ==========
    
    def test_system_resources(self):
        """Test system resources endpoint"""
        success, response = self.run_test(
            "System Resources",
            "GET",
            "system/resources",
            200,
            is_critical=True
        )
        
        if success:
            required_fields = ['cpu_percent', 'memory_percent', 'memory_used_gb', 'memory_total_gb', 
                             'disk_percent', 'disk_used_gb', 'disk_total_gb']
            for field in required_fields:
                if field not in response:
                    self.log_test(f"System Resources - {field} field", False, f"Missing {field}", is_critical=True)
                    return False
            return True
        return False

    # ========== CHANGELOG/UPDATES API TESTS ==========
    
    def test_changelog_endpoint(self):
        """Test changelog endpoint"""
        success, response = self.run_test(
            "Changelog Endpoint",
            "GET",
            "changelog",
            200,
            auth_required=False,
            is_critical=True
        )
        
        if success:
            if 'content' not in response:
                self.log_test("Changelog - content field", False, "Missing content field", is_critical=True)
                return False
            
            # Verify content is not empty
            content = response.get('content', '')
            if not content or len(content.strip()) == 0:
                self.log_test("Changelog - content empty", False, "Changelog content is empty", is_critical=True)
                return False
                
            return True
        return False

    # ========== STEAMCMD TESTS ==========
    
    def test_steamcmd_status(self):
        """Test SteamCMD status endpoint"""
        success, response = self.run_test(
            "SteamCMD Status",
            "GET",
            "steamcmd/status",
            200,
            is_critical=False
        )
        
        if success:
            if 'installed' not in response:
                self.log_test("SteamCMD Status - installed field", False, "Missing installed field", is_critical=False)
                return False
            return True
        return False

    def test_steamcmd_install(self):
        """Test SteamCMD installation"""
        success, response = self.run_test(
            "SteamCMD Install",
            "POST",
            "steamcmd/install",
            200,
            is_critical=False
        )
        return success

    # ========== SECURITY TESTS ==========
    
    def test_authentication_required(self):
        """Test that protected endpoints require authentication"""
        protected_endpoints = [
            ("GET", "system/resources"),
            ("GET", "servers"),
            ("POST", "servers"),
            ("GET", "admin/sub-admins")
        ]
        
        all_passed = True
        for method, endpoint in protected_endpoints:
            # Test without token
            url = f"{self.api_url}/{endpoint}"
            headers = {'Content-Type': 'application/json'}
            
            try:
                if method == 'GET':
                    response = requests.get(url, headers=headers, timeout=10)
                elif method == 'POST':
                    response = requests.post(url, json={}, headers=headers, timeout=10)
                
                if response.status_code != 401:
                    self.log_test(f"Auth Required - {endpoint}", False, f"Expected 401, got {response.status_code}", is_critical=True)
                    all_passed = False
                else:
                    self.log_test(f"Auth Required - {endpoint}", True, is_critical=True)
                    
            except Exception as e:
                self.log_test(f"Auth Required - {endpoint}", False, f"Error: {str(e)}", is_critical=True)
                all_passed = False
        
        return all_passed

    def test_sub_admin_permissions(self):
        """Test sub-admin permission enforcement"""
        if not self.sub_admin_token or not self.server_id:
            return False
            
        # Test sub-admin can view servers (should work if they have permission)
        success, response = self.run_test_with_token(
            "Sub-Admin Server Access",
            "GET",
            "servers",
            200,
            token=self.sub_admin_token,
            is_critical=True
        )
        
        # Test sub-admin cannot access admin endpoints
        success_admin, response_admin = self.run_test_with_token(
            "Sub-Admin Admin Access Denied",
            "GET",
            "admin/sub-admins",
            403,  # Should be forbidden
            token=self.sub_admin_token,
            is_critical=True
        )
        
        return success and success_admin

    def test_jwt_token_validation(self):
        """Test JWT token validation"""
        # Test with invalid token
        invalid_token = "invalid.jwt.token"
        
        url = f"{self.api_url}/system/resources"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {invalid_token}'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 401:
                self.log_test("JWT Token Validation", True, is_critical=True)
                return True
            else:
                self.log_test("JWT Token Validation", False, f"Expected 401, got {response.status_code}", is_critical=True)
                return False
        except Exception as e:
            self.log_test("JWT Token Validation", False, f"Error: {str(e)}", is_critical=True)
            return False

    # ========== CLEANUP TESTS ==========
    
    def test_cleanup(self):
        """Clean up test data"""
        cleanup_success = True
        
        # Delete test server
        if self.server_id:
            success, _ = self.run_test(
                "Cleanup - Delete Server",
                "DELETE",
                f"servers/{self.server_id}",
                200,
                is_critical=False
            )
            if not success:
                cleanup_success = False
        
        # Delete sub-admin
        if self.sub_admin_id:
            success, _ = self.run_test(
                "Cleanup - Delete Sub-Admin",
                "DELETE",
                f"admin/sub-admins/{self.sub_admin_id}",
                200,
                is_critical=False
            )
            if not success:
                cleanup_success = False
        
        return cleanup_success

    def run_all_tests(self):
        """Run comprehensive backend tests for Tactical Server Control Panel"""
        print("🚀 Starting Tactical Server Control Panel Backend Tests")
        print(f"   Base URL: {self.base_url}")
        print("=" * 80)

        # Phase 1: Basic Authentication & Setup Tests
        print("\n📋 PHASE 1: Authentication & User Management")
        print("-" * 50)
        
        if not self.test_check_first_run():
            print("❌ First run check failed, stopping tests")
            return False
            
        if not self.test_password_config():
            print("❌ Password config failed, stopping tests")
            return False

        if not self.test_first_time_setup():
            print("❌ First-time setup failed, stopping tests")
            return False

        if not self.test_admin_login():
            print("❌ Admin login failed, stopping tests")
            return False

        # TOTP and password reset (non-critical)
        self.test_totp_setup_flow()
        self.test_password_reset_flow()

        # Phase 2: Sub-Admin System Tests
        print("\n👥 PHASE 2: Sub-Admin User System")
        print("-" * 50)
        
        if not self.test_create_sub_admin():
            print("❌ Sub-admin creation failed")
            
        if not self.test_list_sub_admins():
            print("❌ Sub-admin listing failed")
            
        if not self.test_get_sub_admin():
            print("❌ Sub-admin retrieval failed")
            
        if not self.test_update_sub_admin():
            print("❌ Sub-admin update failed")
            
        if not self.test_sub_admin_login():
            print("❌ Sub-admin login failed")

        # Phase 3: Server Management Tests
        print("\n🖥️  PHASE 3: Server Management & Resources")
        print("-" * 50)
        
        if not self.test_create_server_with_resources():
            print("❌ Server creation with resources failed")
            
        if not self.test_list_servers():
            print("❌ Server listing failed")
            
        if not self.test_get_server():
            print("❌ Server retrieval failed")
            
        if not self.test_update_server_resources():
            print("❌ Server resource update failed")
            
        if not self.test_server_control_operations():
            print("❌ Server control operations failed")

        # Server management features (non-critical)
        self.test_server_config_management()
        self.test_server_mod_management()
        self.test_server_logs()

        # Phase 4: System & API Tests
        print("\n⚙️  PHASE 4: System Resources & APIs")
        print("-" * 50)
        
        if not self.test_system_resources():
            print("❌ System resources failed")
            
        if not self.test_changelog_endpoint():
            print("❌ Changelog endpoint failed")

        # SteamCMD tests (non-critical)
        self.test_steamcmd_status()
        self.test_steamcmd_install()

        # Phase 5: Security Tests
        print("\n🔒 PHASE 5: Security & Permissions")
        print("-" * 50)
        
        if not self.test_authentication_required():
            print("❌ Authentication enforcement failed")
            
        if not self.test_sub_admin_permissions():
            print("❌ Sub-admin permission enforcement failed")
            
        if not self.test_jwt_token_validation():
            print("❌ JWT token validation failed")

        # Phase 6: Cleanup
        print("\n🧹 PHASE 6: Cleanup")
        print("-" * 50)
        self.test_cleanup()

        # Print comprehensive results
        print("\n" + "=" * 80)
        print(f"📊 COMPREHENSIVE TEST RESULTS:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES ({len(self.critical_failures)}):")
            for failure in self.critical_failures:
                print(f"   ❌ {failure}")
        
        # Categorize results
        critical_tests = [r for r in self.test_results if r.get('critical', False)]
        critical_passed = len([r for r in critical_tests if r['success']])
        critical_total = len(critical_tests)
        
        non_critical_tests = [r for r in self.test_results if not r.get('critical', False)]
        non_critical_passed = len([r for r in non_critical_tests if r['success']])
        non_critical_total = len(non_critical_tests)
        
        print(f"\n📈 DETAILED BREAKDOWN:")
        print(f"   Critical Tests: {critical_passed}/{critical_total} passed ({(critical_passed/critical_total*100):.1f}%)")
        print(f"   Non-Critical Tests: {non_critical_passed}/{non_critical_total} passed ({(non_critical_passed/non_critical_total*100):.1f}%)")
        
        if critical_passed == critical_total:
            print("\n🎉 All critical backend functionality is working!")
            if self.tests_passed == self.tests_run:
                print("🌟 Perfect score - All tests passed!")
            else:
                print(f"⚠️  Some non-critical features need attention ({self.tests_run - self.tests_passed} minor issues)")
            return True
        else:
            print(f"\n💥 CRITICAL ISSUES DETECTED - {critical_total - critical_passed} critical tests failed")
            return False

def main():
    tester = TacticalServerControlPanelTester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())