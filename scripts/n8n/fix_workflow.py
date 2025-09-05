#!/usr/bin/env python3
"""
Script para corregir la URL del workflow de n8n
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import requests

def fix_workflow_url():
    """Corregir la URL del workflow para usar comunicación entre contenedores"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🔧 Fixing workflow URL configuration...")
    
    # Obtener workflows
    workflows = client.get_workflows()
    if not workflows:
        print("❌ No workflows found")
        return False
    
    workflow = workflows[0]
    workflow_id = workflow.get('id')
    workflow_name = workflow.get('name', 'Unknown')
    
    print(f"📋 Workflow: {workflow_name}")
    print(f"🆔 ID: {workflow_id}")
    
    # Obtener detalles del workflow
    try:
        response = requests.get(
            f"{settings.n8n.base_url}/api/v1/workflows/{workflow_id}",
            headers={'X-N8N-API-KEY': api_key},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ Could not get workflow details: {response.status_code}")
            return False
            
        workflow_data = response.json()
        
    except Exception as e:
        print(f"❌ Error getting workflow details: {e}")
        return False
    
    # Buscar y corregir nodos con URL localhost
    nodes = workflow_data.get('nodes', [])
    modified = False
    
    print(f"🔍 Checking {len(nodes)} nodes for localhost URLs...")
    
    for node in nodes:
        node_name = node.get('name', 'unnamed')
        node_type = node.get('type', 'unknown')
        parameters = node.get('parameters', {})
        
        # Verificar nodos HTTP con localhost
        if 'http' in node_type.lower():
            url = parameters.get('url', '')
            if 'localhost:8000' in url:
                old_url = url
                new_url = url.replace('localhost:8000', 'api:8000')
                parameters['url'] = new_url
                modified = True
                print(f"🔄 Fixed {node_name}:")
                print(f"  Old: {old_url}")
                print(f"  New: {new_url}")
    
    if not modified:
        print("ℹ️  No localhost URLs found to fix")
        return True
    
    # Crear payload mínimo para la actualización (sin campos read-only)
    update_payload = {
        'name': workflow_data.get('name'),
        'nodes': workflow_data.get('nodes'),
        'connections': workflow_data.get('connections'),
        'settings': workflow_data.get('settings', {}),
        'staticData': workflow_data.get('staticData', {})
    }
    
    # Actualizar el workflow
    print(f"💾 Updating workflow...")
    success = client.update_workflow(workflow_id, update_payload)
    
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
        
        return True
    else:
        print("❌ Failed to activate workflow after URL fix")
        print("💡 Check n8n interface for any remaining issues")
        return False

if __name__ == "__main__":
    success = fix_workflow_url()
    if success:
        print("\n🎯 Workflow fix completed successfully!")
        print("🚀 You can now use the n8n workflow for data ingestion")
    else:
        print("\n❌ Workflow fix failed")
        print("🔍 Check the error messages above for details")
