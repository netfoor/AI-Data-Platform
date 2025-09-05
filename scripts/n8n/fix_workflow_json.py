#!/usr/bin/env python3
"""
Script para actualizar el workflow usando el archivo JSON corregido
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json

def update_workflow_from_file():
    """Actualizar workflow usando el archivo JSON corregido"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🔧 Updating workflow from corrected JSON file...")
    
    # Cargar el archivo JSON corregido
    try:
        with open('/app/workflows/consolidated-data-ingestion-workflow.json', 'r') as f:
            workflow_data = json.load(f)
        print("✅ Loaded corrected workflow JSON")
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return False
    
    # Obtener workflows existentes
    workflows = client.get_workflows()
    if not workflows:
        print("❌ No workflows found")
        return False
    
    workflow = workflows[0]
    workflow_id = workflow.get('id')
    workflow_name = workflow.get('name', 'Unknown')
    
    print(f"📋 Updating workflow: {workflow_name}")
    print(f"🆔 ID: {workflow_id}")
    
    # Actualizar el workflow
    print(f"💾 Updating workflow with corrected configuration...")
    success = client.update_workflow(workflow_id, workflow_data)
    
    if not success:
        print("❌ Failed to update workflow")
        return False
    
    print("✅ Workflow updated successfully!")
    
    # Intentar activar el workflow
    print(f"🔧 Attempting to activate workflow...")
    activation_success = client.activate_workflow(workflow_id)
    
    if activation_success:
        print("🎉 Workflow activated successfully!")
        
        # Verificar estado final
        workflows = client.get_workflows()
        if workflows:
            updated_workflow = workflows[0]
            status = "🟢 Active" if updated_workflow.get('active') else "🔴 Inactive"
            print(f"📊 Final status: {status}")
        
        # Probar ejecución manual
        print(f"🚀 Testing manual execution...")
        execution_id = client.execute_workflow(workflow_id)
        if execution_id:
            print(f"✅ Manual execution started: {execution_id}")
        else:
            print("⚠️ Manual execution failed")
        
        return True
    else:
        print("❌ Failed to activate workflow after update")
        print("💡 Check n8n interface for any remaining issues")
        return False

if __name__ == "__main__":
    success = update_workflow_from_file()
    if success:
        print("\n🎯 Workflow update completed successfully!")
        print("🚀 The n8n workflow is now properly configured and active")
        print("📝 URL corrected: localhost:8000 → api:8000")
        print("🔧 Node syntax fixed for proper n8n compatibility")
    else:
        print("\n❌ Workflow update failed")
        print("🔍 Check the error messages above for details")
