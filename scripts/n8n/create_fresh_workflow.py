#!/usr/bin/env python3
"""
Script para crear un workflow completamente nuevo con timestamp único
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json
import time
from pathlib import Path

def create_fresh_workflow_standalone():
    """Crear un workflow completamente nuevo"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🆕 Creating fresh data ingestion workflow...")
    
    # Load the corrected workflow JSON
    workflow_path = Path("/app/workflows/consolidated-data-ingestion-workflow.json")
    if not workflow_path.exists():
        print(f"❌ Workflow template not found at: {workflow_path}")
        return None

    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return None

    # Generate unique name with timestamp
    timestamp = int(time.time())
    unique_name = f"AI Data Platform - Fresh Ingestion {timestamp}"
    workflow_data['name'] = unique_name
    
    print(f"🏷️ Creating workflow: {unique_name}")

    # Update CSV file path in parameters
    csv_file_path = "ads_spend.csv"
    for node in workflow_data.get('nodes', []):
        if node.get('name') == 'Read CSV File':
            if 'parameters' in node and 'filePath' in node['parameters']:
                node['parameters']['filePath'] = csv_file_path
                print(f"📝 Updated CSV file path: {csv_file_path}")

    # Create workflow
    print("🔧 Creating workflow...")
    workflow_id = client.create_workflow(workflow_data)
    
    if workflow_id:
        print(f"✅ Fresh workflow created with ID: {workflow_id}")
        print(f"📋 Workflow name: {unique_name}")
        print(f"🌐 Go to http://localhost:5678 to find and activate it")
        
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
        print("❌ Failed to create fresh workflow")
        return None

if __name__ == "__main__":
    workflow_id = create_fresh_workflow_standalone()
    if workflow_id:
        print(f"\n🎯 SUCCESS!")
        print(f"🆔 Workflow ID: {workflow_id}")
        print(f"🌐 Next steps:")
        print(f"  1. Go to http://localhost:5678")
        print(f"  2. Find the workflow 'AI Data Platform - Fresh Ingestion XXXXX'")
        print(f"  3. Toggle it to ACTIVE")
        print(f"  4. Test with: docker compose exec api python -m ai_data_platform.cli n8n ingest")
    else:
        print(f"\n❌ FAILED to create workflow")
        print(f"🔍 Check the error messages above")
