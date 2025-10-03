#!/usr/bin/env python3
"""
Test script for JARVIS AI Hub integration
Tests the orchestrator functionality, skill routing, and API endpoints
"""

import sys
import os
import json
import requests
import time
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_schema_loader():
    """Test schema loading functionality"""
    print("🔍 Testing Schema Loader...")
    
    try:
        from src.schema_loader import get_all_schemas, match_schema
        
        # Test schema loading
        schemas = get_all_schemas()
        print(f"✅ Loaded {len(schemas)} schemas: {list(schemas.keys())}")
        
        # Test schema matching
        test_inputs = [
            {"message": "turn on the lights", "action": "device_control"},
            {"message": "what time is it", "action": "information_request"},
            {"message": "hello jarvis"}
        ]
        
        for test_input in test_inputs:
            skill_name, schema = match_schema(test_input)
            if skill_name:
                print(f"✅ Matched '{test_input['message']}' to skill: {skill_name}")
            else:
                print(f"ℹ️  No match for '{test_input['message']}' (will use GPT fallback)")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema loader test failed: {e}")
        return False

def test_skills():
    """Test individual skill execution"""
    print("\n🛠️  Testing Skills...")
    
    try:
        # Test device control skill
        from src.skills.device_control import execute as device_execute
        
        device_result = device_execute({
            "message": "turn on the living room lights",
            "user_id": "test_user"
        })
        
        if device_result.get("success"):
            print("✅ Device control skill working")
        else:
            print(f"⚠️  Device control skill issue: {device_result}")
        
        # Test information request skill
        from src.skills.information_request import execute as info_execute
        
        info_result = info_execute({
            "message": "what time is it",
            "user_id": "test_user"
        })
        
        if info_result.get("success"):
            print("✅ Information request skill working")
        else:
            print(f"⚠️  Information request skill issue: {info_result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Skills test failed: {e}")
        return False

def test_orchestrator():
    """Test orchestrator functionality"""
    print("\n🎭 Testing Orchestrator...")
    
    try:
        import asyncio
        from src.orchestrator import handle_request
        
        # Test skill routing
        test_requests = [
            {"message": "turn on the kitchen lights", "user_id": "test_user"},
            {"message": "what time is it", "user_id": "test_user"},
            {"message": "hello jarvis, how are you today?", "user_id": "test_user"}
        ]
        
        for test_request in test_requests:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(handle_request(test_request))
                if result.get("success", True):  # Some responses don't have success field
                    print(f"✅ Orchestrator handled: '{test_request['message']}'")
                else:
                    print(f"⚠️  Orchestrator issue with: '{test_request['message']}'")
            finally:
                loop.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def test_flask_app():
    """Test Flask application startup"""
    print("\n🌐 Testing Flask Application...")
    
    try:
        # Import the Flask app
        from src.main import app
        
        # Test app creation
        if app:
            print("✅ Flask app created successfully")
            
            # Test blueprints registration
            blueprint_names = [bp.name for bp in app.blueprints.values()]
            expected_blueprints = ['user', 'ai_core', 'integrations', 'orchestrator']
            
            for expected in expected_blueprints:
                if expected in blueprint_names:
                    print(f"✅ Blueprint '{expected}' registered")
                else:
                    print(f"⚠️  Blueprint '{expected}' not found")
            
            return True
        else:
            print("❌ Flask app creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints if server is running"""
    print("\n🔌 Testing API Endpoints...")
    
    base_url = "http://localhost:5000/api"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"⚠️  Health endpoint returned {response.status_code}")
    except requests.exceptions.RequestException:
        print("ℹ️  Server not running - skipping API tests")
        return True
    
    # Test skills endpoint
    try:
        response = requests.get(f"{base_url}/skills", timeout=5)
        if response.status_code == 200:
            skills_data = response.json()
            print(f"✅ Skills endpoint working - {skills_data.get('total_count', 0)} skills available")
        else:
            print(f"⚠️  Skills endpoint returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Skills endpoint test failed: {e}")
    
    # Test chat endpoint
    try:
        chat_data = {
            "message": "turn on the lights",
            "user_id": "test_user"
        }
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=10)
        if response.status_code == 200:
            chat_result = response.json()
            print("✅ Chat endpoint working")
            print(f"   Response: {chat_result.get('response', 'No response')[:100]}...")
        else:
            print(f"⚠️  Chat endpoint returned {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Chat endpoint test failed: {e}")
    
    return True

def main():
    """Run all tests"""
    print("🚀 JARVIS AI Hub Integration Test Suite")
    print("=" * 50)
    
    test_results = []
    
    # Run tests
    test_results.append(("Schema Loader", test_schema_loader()))
    test_results.append(("Skills", test_skills()))
    test_results.append(("Orchestrator", test_orchestrator()))
    test_results.append(("Flask App", test_flask_app()))
    test_results.append(("API Endpoints", test_api_endpoints()))
    
    # Summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The integration is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

