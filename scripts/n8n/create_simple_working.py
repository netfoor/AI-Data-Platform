#!/usr/bin/env python3
"""
Script para crear un workflow simple que definitivamente funciona
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json
import time

def create_simple_working_workflow():
    """Crear un workflow simple que garantiza funcionar"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🔧 Creating simple working workflow...")
    
    # Define simple workflow that definitely works
    timestamp = int(time.time())
    simple_workflow = {
        "name": f"AI Data Platform - Simple Working {timestamp}",
        "nodes": [
            {
                "parameters": {},
                "id": "start-trigger",
                "name": "Start",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [200, 300]
            },
            {
                "parameters": {
                    "method": "POST",
                    "url": "http://api:8000/ingest",
                    "sendHeaders": True,
                    "headerParameters": [
                        { "name": "Content-Type", "value": "application/json" }
                    ],
                    "sendBody": True,
                    "contentType": "json",
                    "jsonData": '{\n  "csv_file_path": "ads_spend.csv"\n}'
                },
                "id": "trigger-etl",
                "name": "Trigger ETL",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [420, 300]
            }
        ],
        "connections": {
            "Start": { "main": [[{ "node": "Trigger ETL", "type": "main", "index": 0 }]] }
        },
        "settings": { "executionOrder": "v1" }
    }
    
    print(f"📋 Creating: {simple_workflow['name']}")
    
    # Create workflow
    workflow_id = client.create_workflow(simple_workflow)
    
    if workflow_id:
        print(f"✅ Simple workflow created with ID: {workflow_id}")
        print(f"📋 Workflow name: {simple_workflow['name']}")
        
        # Verify it appears in the list
        print("🔍 Verifying workflow was created...")
        workflows = client.get_workflows()
        found = False
        for w in workflows:
            if w.get('id') == workflow_id:
                print(f"📋 Found in list: {w.get('name')}")
                print(f"📊 Status: {'🟢 Active' if w.get('active') else '🔴 Inactive'}")
                found = True
                break
        
        if not found:
            print("⚠️ Workflow created but not visible in list")
        
        return workflow_id
    else:
        print("❌ Failed to create simple workflow")
        return None

if __name__ == "__main__":
    print("🚀 Creating a guaranteed working n8n workflow...")
    workflow_id = create_simple_working_workflow()
    
    if workflow_id:
        print(f"\n🎯 SUCCESS!")
        print(f"🆔 Workflow ID: {workflow_id}")
        print(f"🌐 Next steps:")
        print(f"  1. Go to http://localhost:5678")
        print(f"  2. Find the workflow 'AI Data Platform - Simple Working XXXXX'")
        print(f"  3. Toggle it to ACTIVE")
        print(f"  4. Test execution directly in n8n interface")
        print(f"  5. If it works, use: docker compose exec api python -m ai_data_platform.cli n8n ingest")
    else:
        print(f"\n❌ FAILED to create workflow")
        print(f"🔍 There may be a deeper issue with n8n setup")
