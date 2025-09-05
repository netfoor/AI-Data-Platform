#!/usr/bin/env python3
"""
Test script for n8n Docker connection and workflow functionality
"""
import requests
import json
import time
from pathlib import Path

def test_n8n_connection():
    """Test basic connection to n8n Docker instance"""
    print("🔍 Testing n8n Docker connection...")
    
    try:
        # Test basic connection
        response = requests.get("http://localhost:5678", timeout=10)
        if response.status_code == 200:
            print("✅ n8n is accessible at http://localhost:5678")
            return True
        else:
            print(f"❌ n8n responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to n8n. Is the Docker container running?")
        print("💡 Try: docker-compose up -d n8n")
        return False
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def test_webhook_endpoint():
    """Test the webhook endpoint for workflow triggering"""
    print("\n🔗 Testing webhook endpoint...")
    
    try:
        # Test webhook endpoint
        webhook_url = "http://localhost:5678/webhook/start-webhook"
        test_data = {
            "test": "data",
            "timestamp": time.time(),
            "source": "test_script"
        }
        
        response = requests.post(
            webhook_url,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print("✅ Webhook endpoint is working!")
            print(f"📊 Response: {response.text}")
            return True
        else:
            print(f"❌ Webhook failed with status: {response.status_code}")
            print(f"📝 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")
        return False

def check_workflow_file():
    """Check if the workflow JSON file exists"""
    print("\n📁 Checking workflow file...")
    
    workflow_path = Path("workflows/data-ingestion-workflow.json")
    if workflow_path.exists():
        print("✅ Workflow file found!")
        
        # Validate JSON
        try:
            with open(workflow_path, 'r') as f:
                workflow_data = json.load(f)
            print(f"✅ Valid JSON workflow: {workflow_data.get('name', 'Unknown')}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in workflow file: {e}")
            return False
    else:
        print("❌ Workflow file not found!")
        print(f"💡 Expected path: {workflow_path.absolute()}")
        return False

def main():
    """Main test function"""
    print("🚀 n8n Docker Connection Test")
    print("=" * 40)
    
    # Test 1: Basic connection
    connection_ok = test_n8n_connection()
    
    # Test 2: Workflow file
    workflow_ok = check_workflow_file()
    
    # Test 3: Webhook (only if connection is ok)
    webhook_ok = False
    if connection_ok:
        webhook_ok = test_webhook_endpoint()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results Summary:")
    print(f"🔌 Connection: {'✅ OK' if connection_ok else '❌ FAILED'}")
    print(f"📁 Workflow File: {'✅ OK' if workflow_ok else '❌ FAILED'}")
    print(f"🔗 Webhook: {'✅ OK' if webhook_ok else '❌ FAILED'}")
    
    if connection_ok and workflow_ok:
        print("\n🎉 Ready to import workflow!")
        print("📖 Follow DOCKER_SETUP_GUIDE.md for next steps")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")
        
        if not connection_ok:
            print("\n💡 Troubleshooting:")
            print("1. Ensure Docker is running")
            print("2. Start n8n: docker-compose up -d n8n")
            print("3. Check container status: docker-compose ps")

if __name__ == "__main__":
    main()

