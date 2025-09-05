#!/usr/bin/env python3
"""
Script para crear un nuevo workflow usando el JSON actualizado
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json

def create_new_workflow():
    """Crear un nuevo workflow usando el JSON corregido"""
    
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🆕 Creating new workflow from corrected JSON...")
    
    # Cargar el archivo JSON corregido
    try:
        with open('/app/workflows/consolidated-data-ingestion-workflow.json', 'r') as f:
            workflow_data = json.load(f)
        print("✅ Loaded corrected workflow JSON")
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return False
    
    # Cambiar el nombre para crear uno nuevo
    workflow_data['name'] = 'AI Data Platform - Fixed Data Ingestion'
    
    # Crear el nuevo workflow
    print(f"💾 Creating new workflow...")
    workflow_id = client.create_workflow(workflow_data)
    
    if not workflow_id:
        print("❌ Failed to create new workflow")
        return False
    
    print(f"✅ New workflow created! ID: {workflow_id}")
    
    # Intentar activar el nuevo workflow
    print(f"🔧 Attempting to activate new workflow...")
    activation_success = client.activate_workflow(workflow_id)
    
    if activation_success:
        print("🎉 New workflow activated successfully!")
        
        # Verificar estado final
        workflows = client.get_workflows()
        new_workflow = None
        for w in workflows:
            if w.get('id') == workflow_id:
                new_workflow = w
                break
        
        if new_workflow:
            status = "🟢 Active" if new_workflow.get('active') else "🔴 Inactive"
            print(f"📊 Final status: {status}")
        
        # Probar ejecución manual
        print(f"🚀 Testing manual execution...")
        execution_id = client.execute_workflow(workflow_id)
        if execution_id:
            print(f"✅ Manual execution started: {execution_id}")
            
            # Esperar un poco y verificar resultado
            import time
            time.sleep(5)
            
            status = client.get_execution_status(execution_id)
            if status:
                finished = status.get('finished', False)
                success = status.get('success', False)
                print(f"📊 Execution finished: {finished}, success: {success}")
        else:
            print("⚠️ Manual execution failed to start")
        
        return True
    else:
        print("❌ Failed to activate new workflow")
        print("💡 Let's try activating it manually in the n8n interface")
        return False

if __name__ == "__main__":
    success = create_new_workflow()
    if success:
        print("\n🎯 New workflow created and activated successfully!")
        print("🚀 The workflow is ready for data ingestion")
    else:
        print("\n⚠️ Workflow created but needs manual activation")
        print("🌐 Go to http://localhost:5678 to activate it manually")
