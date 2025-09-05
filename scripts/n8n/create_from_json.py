#!/usr/bin/env python3
"""
Script para crear workflow desde archivo JSON simple
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json
import time
from pathlib import Path

def create_workflow_from_simple_json():
    """Crear workflow desde el archivo JSON simple"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🔧 Creating workflow from simple JSON file...")
    
    # Load the simple working workflow JSON
    workflow_path = Path("/app/workflows/simple-working-workflow.json")
    
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
        print(f"✅ Loaded simple workflow JSON")
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return None

    # Add timestamp to make it unique
    timestamp = int(time.time())
    original_name = workflow_data.get('name', 'Unknown')
    workflow_data['name'] = f"{original_name} {timestamp}"
    
    print(f"📋 Creating: {workflow_data['name']}")
    print(f"🔍 Nodes: {len(workflow_data.get('nodes', []))}")
    print(f"🔗 Connections: {len(workflow_data.get('connections', {}))}")

    # Create workflow
    workflow_id = client.create_workflow(workflow_data)
    
    if workflow_id:
        print(f"✅ Workflow created with ID: {workflow_id}")
        
        # Verify it appears and is accessible
        print("🔍 Verifying workflow accessibility...")
        workflows = client.get_workflows()
        found = False
        
        for w in workflows:
            if w.get('id') == workflow_id:
                name = w.get('name')
                active = w.get('active', False)
                print(f"📋 Found: {name}")
                print(f"📊 Status: {'🟢 Active' if active else '🔴 Inactive'}")
                
                # Try to get the specific workflow details
                try:
                    import requests
                    response = requests.get(
                        f"{settings.n8n.base_url}/api/v1/workflows/{workflow_id}",
                        headers={'X-N8N-API-KEY': api_key},
                        timeout=10
                    )
                    if response.status_code == 200:
                        print("✅ Workflow is accessible and valid")
                    else:
                        print(f"⚠️ Workflow not accessible: {response.status_code}")
                except Exception as e:
                    print(f"⚠️ Error accessing workflow: {e}")
                
                found = True
                break
        
        if not found:
            print("⚠️ Workflow created but not visible in list")
        
        return workflow_id
    else:
        print("❌ Failed to create workflow from simple JSON")
        return None

if __name__ == "__main__":
    print("🚀 Creating workflow from simple JSON file...")
    workflow_id = create_workflow_from_simple_json()
    
    if workflow_id:
        print(f"\n🎯 SUCCESS!")
        print(f"🆔 Workflow ID: {workflow_id}")
        print(f"🌐 Next steps:")
        print(f"  1. Go to http://localhost:5678")
        print(f"  2. Find the new workflow")
        print(f"  3. Toggle it to ACTIVE")
        print(f"  4. Test execution")
        
        # Also test basic connectivity
        print(f"\n🔍 Testing basic API connectivity...")
        from ai_data_platform.api.n8n_api_client import N8nAPIClient
        api_key = os.getenv('N8N_API_KEY')
        client = N8nAPIClient(settings.n8n.base_url, api_key)
        
        if client.test_connection():
            print("✅ n8n API connection working")
        else:
            print("❌ n8n API connection failed")
            
    else:
        print(f"\n❌ FAILED to create workflow")
        print(f"🔍 Check n8n logs: docker compose logs n8n --tail 20")
