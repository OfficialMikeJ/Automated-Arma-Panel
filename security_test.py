#!/usr/bin/env python3
"""
Focused security testing for Tactical Server Control Panel
Tests the specific fixes mentioned in the review request
"""

import requests
import json
from datetime import datetime

class SecurityTester:
    def __init__(self, base_url="https://tacticalpanel.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.test_token = None
        self.test_username = None
        
    def log_result(self, test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        return success

    def test_authentication_returns_401(self):
        """Test that protected endpoints return 401 (not 403) when no auth provided"""
        print("\n🔒 Testing Authentication Enforcement (401 vs 403)")
        
        endpoints = [
            "system/resources",
            "servers", 
            "admin/sub-admins"
        ]
        
        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.api_url}/{endpoint}", timeout=10)
                if response.status_code == 401:
                    self.log_result(f"No Auth - {endpoint}", True, f"Correctly returned 401")
                else:
                    self.log_result(f"No Auth - {endpoint}", False, f"Expected 401, got {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_result(f"No Auth - {endpoint}", False, f"Error: {str(e)}")
                all_passed = False
                
        return all_passed

    def test_invalid_jwt_returns_401(self):
        """Test that invalid JWT tokens return 401 (not 520)"""
        print("\n🔑 Testing Invalid JWT Token Handling")
        
        invalid_tokens = [
            "invalid.jwt.token",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "Bearer invalid_token"
        ]
        
        all_passed = True
        for token in invalid_tokens:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get(f"{self.api_url}/system/resources", headers=headers, timeout=10)
                
                if response.status_code == 401:
                    self.log_result(f"Invalid JWT", True, f"Correctly returned 401 for invalid token")
                else:
                    self.log_result(f"Invalid JWT", False, f"Expected 401, got {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_result(f"Invalid JWT", False, f"Error: {str(e)}")
                all_passed = False
                
        return all_passed

    def test_password_reset_flow(self):
        """Test password reset functionality (should work after fixes)"""
        print("\n🔄 Testing Password Reset Flow")
        
        # First register a test user
        timestamp = datetime.now().strftime('%H%M%S')
        username = f"resettest_{timestamp}"
        
        register_data = {
            "username": username,
            "password": "TestPass123!",
            "security_questions": {
                "question1": "blue",
                "question2": "paris", 
                "question3": "fluffy",
                "question4": "smith"
            }
        }
        
        try:
            # Register user
            response = requests.post(f"{self.api_url}/auth/register", json=register_data, timeout=10)
            if response.status_code != 200:
                return self.log_result("Password Reset Setup", False, f"Failed to register test user: {response.status_code}")
            
            # Get security questions
            response = requests.get(f"{self.api_url}/auth/security-questions/{username}", timeout=10)
            if response.status_code != 200:
                return self.log_result("Get Security Questions", False, f"Failed to get security questions: {response.status_code}")
            
            # Test password reset
            reset_data = {
                "username": username,
                "answer1": "blue",
                "answer2": "paris", 
                "answer3": "fluffy",
                "answer4": "smith",
                "new_password": "NewTestPass123!"
            }
            
            response = requests.post(f"{self.api_url}/auth/reset-password", json=reset_data, timeout=10)
            
            if response.status_code == 200:
                return self.log_result("Password Reset", True, "Password reset successful")
            else:
                error_detail = ""
                try:
                    error_detail = response.json().get('detail', '')
                except:
                    pass
                return self.log_result("Password Reset", False, f"Expected 200, got {response.status_code} - {error_detail}")
                
        except Exception as e:
            return self.log_result("Password Reset", False, f"Error: {str(e)}")

    def test_www_authenticate_header(self):
        """Test that 401 responses include WWW-Authenticate header"""
        print("\n📋 Testing WWW-Authenticate Header")
        
        try:
            response = requests.get(f"{self.api_url}/system/resources", timeout=10)
            
            if response.status_code == 401:
                www_auth = response.headers.get('WWW-Authenticate', '')
                if 'Bearer' in www_auth:
                    return self.log_result("WWW-Authenticate Header", True, f"Header present: {www_auth}")
                else:
                    return self.log_result("WWW-Authenticate Header", False, f"Missing or incorrect WWW-Authenticate header: {www_auth}")
            else:
                return self.log_result("WWW-Authenticate Header", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            return self.log_result("WWW-Authenticate Header", False, f"Error: {str(e)}")

    def test_consistent_error_responses(self):
        """Test that error responses are consistent"""
        print("\n📝 Testing Consistent Error Response Format")
        
        try:
            response = requests.get(f"{self.api_url}/system/resources", timeout=10)
            
            if response.status_code == 401:
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        return self.log_result("Error Response Format", True, f"Consistent format with 'detail' field")
                    else:
                        return self.log_result("Error Response Format", False, f"Missing 'detail' field in error response")
                except:
                    return self.log_result("Error Response Format", False, "Error response is not valid JSON")
            else:
                return self.log_result("Error Response Format", False, f"Expected 401, got {response.status_code}")
                
        except Exception as e:
            return self.log_result("Error Response Format", False, f"Error: {str(e)}")

    def run_security_tests(self):
        """Run all security-focused tests"""
        print("🛡️  TACTICAL SERVER CONTROL PANEL - SECURITY TESTING")
        print("=" * 60)
        print("Testing fixes mentioned in review request:")
        print("✅ Authentication middleware returns proper 401 with WWW-Authenticate header")
        print("✅ JWT error handling improved to return 401 instead of 520")
        print("✅ Password reset logic improved")
        print("✅ Global exception handlers for consistent error responses")
        print("=" * 60)
        
        results = []
        
        # Test 1: Authentication enforcement (401 vs 403)
        results.append(self.test_authentication_returns_401())
        
        # Test 2: Invalid JWT handling (401 vs 520)
        results.append(self.test_invalid_jwt_returns_401())
        
        # Test 3: Password reset functionality
        results.append(self.test_password_reset_flow())
        
        # Test 4: WWW-Authenticate header
        results.append(self.test_www_authenticate_header())
        
        # Test 5: Consistent error responses
        results.append(self.test_consistent_error_responses())
        
        # Summary
        passed = sum(results)
        total = len(results)
        success_rate = (passed / total) * 100
        
        print("\n" + "=" * 60)
        print(f"🎯 SECURITY TEST RESULTS:")
        print(f"   Tests Passed: {passed}/{total}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if passed == total:
            print("🎉 ALL SECURITY FIXES VERIFIED!")
            print("✅ Authentication returns 401 (not 403)")
            print("✅ JWT errors return 401 (not 520)")
            print("✅ Password reset working")
            print("✅ WWW-Authenticate headers present")
            print("✅ Consistent error response format")
        else:
            print(f"⚠️  {total - passed} security issues still need attention")
            
        return passed == total

def main():
    tester = SecurityTester()
    success = tester.run_security_tests()
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())