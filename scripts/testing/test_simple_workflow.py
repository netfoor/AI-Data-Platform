#!/usr/bin/env python3
"""
Script para crear y probar un workflow mínimo
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json

def create_simple_workflow():
    """Crear un workflow muy simple para probar"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🔧 Creating simple test workflow...")
    
    # Definir workflow mínimo
    simple_workflow = {
        "name": "AI Data Platform - Simple Test",
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
                    "jsonData": '{"csv_file_path": "ads_spend.csv"}'
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
    
    # Crear el workflow
    print(f"💾 Creating simple workflow...")
    workflow_id = client.create_workflow(simple_workflow)
    
    if not workflow_id:
        print("❌ Failed to create workflow")
        return False
    
    print(f"✅ Simple workflow created! ID: {workflow_id}")
    
    # Intentar activar
    print(f"🔧 Attempting to activate simple workflow...")
    activation_success = client.activate_workflow(workflow_id)
    
    if activation_success:
        print("🎉 Simple workflow activated successfully!")
        
        # Probar ejecución
        print(f"🚀 Testing execution...")
        execution_id = client.execute_workflow(workflow_id)
        if execution_id:
            print(f"✅ Execution started: {execution_id}")
            
            # Esperar y verificar resultado
            import time
            time.sleep(3)
            
            status = client.get_execution_status(execution_id)
            if status:
                print(f"📊 Execution status: {status.get('finished', False)}")
                print(f"🎯 Success: {status.get('success', False)}")
        
        return True
    else:
        print("❌ Failed to activate simple workflow")
        return False

if __name__ == "__main__":
    success = create_simple_workflow()
    if success:
        print("\n🎯 Simple workflow test completed successfully!")
        print("🔧 This confirms the basic n8n integration works")
        print("🚀 Now you can build more complex workflows")
    else:
        print("\n❌ Simple workflow test failed")
        print("🔍 There may be a fundamental issue with n8n setup")
