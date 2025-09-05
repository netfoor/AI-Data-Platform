#!/usr/bin/env python3
"""
Script para analizar el workflow de n8n y encontrar problemas
"""
from ai_data_platform.api.n8n_api_client import N8nAPIClient
from ai_data_platform.config import settings
import os
import json

def main():
    api_key = os.getenv('N8N_API_KEY', 'your-n8n-api-key')
    client = N8nAPIClient(
        base_url=settings.n8n.base_url,
        api_key=api_key
    )
    
    print("🔍 Analyzing n8n workflow...")
    
    # Obtener workflows
    workflows = client.get_workflows()
    if not workflows:
        print("❌ No workflows found")
        return
    
    workflow = workflows[0]
    workflow_id = workflow.get('id')
    workflow_name = workflow.get('name', 'Unknown')
    
    print(f"📋 Workflow: {workflow_name}")
    print(f"🆔 ID: {workflow_id}")
    print(f"🔄 Active: {workflow.get('active', False)}")
    
    # Obtener detalles del workflow usando API directa
    try:
        import requests
        response = requests.get(
            f"{settings.n8n.base_url}/api/v1/workflows/{workflow_id}",
            headers={'X-N8N-API-KEY': api_key},
            timeout=10
        )
        if response.status_code == 200:
            details = response.json()
        else:
            print(f"❌ Could not get workflow details: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting workflow details: {e}")
        return
    
    # Analizar nodos
    nodes = details.get('nodes', [])
    print(f"\n📦 Nodes ({len(nodes)} total):")
    
    for i, node in enumerate(nodes, 1):
        name = node.get('name', 'unnamed')
        node_type = node.get('type', 'unknown')
        parameters = node.get('parameters', {})
        
        print(f"  {i}. {name} ({node_type})")
        
        # Verificar problemas comunes
        if not parameters and node_type != 'n8n-nodes-base.start':
            print(f"     ⚠️  Empty parameters")
        
        # Verificar configuración específica
        if 'http' in node_type.lower():
            url = parameters.get('url', '')
            if not url:
                print(f"     ⚠️  HTTP node without URL")
            else:
                print(f"     🌐 URL: {url}")
        
        if 'webhook' in node_type.lower():
            webhook_id = parameters.get('webhookId', '')
            path = parameters.get('path', '')
            print(f"     🔗 Webhook path: {path}")
    
    # Verificar conexiones
    connections = details.get('connections', {})
    print(f"\n🔗 Connections: {len(connections)} groups")
    
    # Buscar nodos desconectados
    connected_nodes = set()
    for source_node, outputs in connections.items():
        connected_nodes.add(source_node)
        for output_name, connections_list in outputs.items():
            for connection in connections_list:
                for target in connection:
                    connected_nodes.add(target.get('node'))
    
    all_node_names = {node.get('name') for node in nodes}
    unconnected = all_node_names - connected_nodes
    
    if unconnected:
        print(f"⚠️  Unconnected nodes: {list(unconnected)}")
    else:
        print("✅ All nodes are connected")
    
    # Intentar activar
    print(f"\n🔧 Attempting to activate workflow...")
    success = client.activate_workflow(workflow_id)
    
    if success:
        print("✅ Workflow activated successfully!")
    else:
        print("❌ Failed to activate workflow")
        print("💡 Check n8n interface for detailed error messages")

if __name__ == "__main__":
    main()
