import os
import json
import requests

# Simple workflow creation script using only basic nodes
WORKFLOW_JSON_FILE = 'simple-basic-workflow.json'
API_KEY = os.getenv('N8N_API_KEY', 'n8n_api_key_1a2b3c4d5e6f')
N8N_BASE_URL = 'http://n8n:5678'

def create_basic_workflow():
    with open(WORKFLOW_JSON_FILE, 'r') as f:
        workflow_data = json.load(f)
    
    headers = {
        'X-N8N-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"Creating basic workflow: {workflow_data['name']}")
    
    response = requests.post(
        f'{N8N_BASE_URL}/api/v1/workflows',
        headers=headers,
        json=workflow_data
    )
    
    if response.status_code in [200, 201]:
        workflow = response.json()
        workflow_id = workflow['id']
        print(f"✅ Basic workflow created successfully with ID: {workflow_id}")
        
        # Try to activate using different methods
        activation_methods = [
            ('PUT', f'/api/v1/workflows/{workflow_id}/activate'),
            ('POST', f'/api/v1/workflows/{workflow_id}/activate'),
            ('PUT', f'/api/v1/workflows/{workflow_id}', {'active': True}),
            ('PATCH', f'/api/v1/workflows/{workflow_id}', {'active': True})
        ]
        
        for method, endpoint, *payload in activation_methods:
            try:
                if payload:
                    if method == 'PUT':
                        activate_response = requests.put(
                            f'{N8N_BASE_URL}{endpoint}',
                            headers=headers,
                            json=payload[0]
                        )
                    elif method == 'PATCH':
                        activate_response = requests.patch(
                            f'{N8N_BASE_URL}{endpoint}',
                            headers=headers,
                            json=payload[0]
                        )
                else:
                    if method == 'PUT':
                        activate_response = requests.put(f'{N8N_BASE_URL}{endpoint}', headers=headers)
                    elif method == 'POST':
                        activate_response = requests.post(f'{N8N_BASE_URL}{endpoint}', headers=headers)
                
                print(f"Tried {method} {endpoint}: {activate_response.status_code}")
                
                if activate_response.status_code == 200:
                    print(f"✅ Workflow activated successfully using {method}!")
                    return workflow_id
                else:
                    print(f"Response: {activate_response.text[:200]}")
                    
            except Exception as e:
                print(f"Error with {method} {endpoint}: {e}")
        
        print(f"⚠️ Workflow created but activation failed. ID: {workflow_id}")
        return workflow_id
    else:
        print(f"❌ Failed to create workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    workflow_id = create_basic_workflow()
    print(f"Final workflow ID: {workflow_id}")
