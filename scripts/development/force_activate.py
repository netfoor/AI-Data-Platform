#!/usr/bin/env python3
"""
Script para forzar la activación de workflows usando todos los métodos disponibles
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json
import requests

def force_activate_workflow():
    """Forzar activación usando todos los métodos posibles"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🔧 Force activating workflows using all available methods...")
    
    # Get all workflows
    workflows = client.get_workflows()
    if not workflows:
        print("❌ No workflows found")
        return False
    
    # Try to activate each one
    for workflow in workflows:
        workflow_id = workflow.get('id')
        workflow_name = workflow.get('name', 'Unknown')
        is_active = workflow.get('active', False)
        
        print(f"\n📋 Processing: {workflow_name}")
        print(f"🆔 ID: {workflow_id}")
        print(f"📊 Current status: {'🟢 Active' if is_active else '🔴 Inactive'}")
        
        if is_active:
            print("✅ Already active, skipping")
            continue
        
        # Method 1: Standard activation
        print("🔧 Method 1: Standard API activation...")
        success1 = client.activate_workflow(workflow_id)
        
        if success1:
            print("✅ Method 1 succeeded!")
            continue
        
        # Method 2: Direct HTTP requests with different endpoints
        print("🔧 Method 2: Direct HTTP activation...")
        endpoints_to_try = [
            f"/api/v1/workflows/{workflow_id}/activate",
            f"/api/workflows/{workflow_id}/activate", 
            f"/workflows/{workflow_id}/activate"
        ]
        
        method2_success = False
        for endpoint in endpoints_to_try:
            try:
                response = requests.post(
                    f"{settings.n8n.base_url}{endpoint}",
                    headers={'X-N8N-API-KEY': api_key},
                    timeout=10
                )
                if response.status_code == 200:
                    print(f"✅ Method 2 succeeded with {endpoint}!")
                    method2_success = True
                    break
                else:
                    print(f"⚠️ {endpoint}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ {endpoint}: {e}")
        
        if method2_success:
            continue
        
        # Method 3: Update workflow with active=true
        print("🔧 Method 3: Update workflow with active=true...")
        try:
            # Get current workflow
            get_response = requests.get(
                f"{settings.n8n.base_url}/api/v1/workflows/{workflow_id}",
                headers={'X-N8N-API-KEY': api_key},
                timeout=10
            )
            
            if get_response.status_code == 200:
                workflow_data = get_response.json()
                
                # Try minimal update
                minimal_update = {
                    "name": workflow_data.get("name"),
                    "active": True
                }
                
                update_response = requests.put(
                    f"{settings.n8n.base_url}/api/v1/workflows/{workflow_id}",
                    headers={'X-N8N-API-KEY': api_key},
                    json=minimal_update,
                    timeout=10
                )
                
                if update_response.status_code == 200:
                    print("✅ Method 3 succeeded!")
                    continue
                else:
                    print(f"⚠️ Method 3 failed: {update_response.status_code}")
                    print(f"Response: {update_response.text[:100]}")
            
        except Exception as e:
            print(f"⚠️ Method 3 error: {e}")
        
        print(f"❌ All activation methods failed for {workflow_name}")
        print("💡 Manual activation required in n8n web interface")
    
    # Final verification
    print("\n🔍 Final status check...")
    updated_workflows = client.get_workflows()
    active_count = sum(1 for w in updated_workflows if w.get('active', False))
    
    print(f"📊 Results: {active_count}/{len(updated_workflows)} workflows active")
    
    if active_count > 0:
        print("🎉 At least one workflow was activated!")
        
        # Test execution of active workflows
        for w in updated_workflows:
            if w.get('active'):
                print(f"🚀 Testing execution of active workflow: {w.get('name')}")
                execution_id = client.execute_workflow(w.get('id'))
                if execution_id:
                    print(f"✅ Execution started: {execution_id}")
                else:
                    print("⚠️ Execution failed")
        
        return True
    else:
        print("❌ No workflows could be activated automatically")
        print("🌐 Please activate manually at http://localhost:5678")
        return False

if __name__ == "__main__":
    force_activate_workflow()
