import os
import json
import requests
import sys

# Setup script para crear workflow compatible
WORKFLOW_JSON_FILE = 'n8n-compatible-workflow.json'
API_KEY = os.getenv('N8N_API_KEY', 'n8n_api_key_1a2b3c4d5e6f')
N8N_BASE_URL = 'http://n8n:5678'

def load_workflow_json():
    with open(WORKFLOW_JSON_FILE, 'r') as f:
        return json.load(f)

def create_compatible_workflow():
    workflow_data = load_workflow_json()
    
    headers = {
        'X-N8N-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"Creating workflow: {workflow_data['name']}")
    
    response = requests.post(
        f'{N8N_BASE_URL}/api/v1/workflows',
        headers=headers,
        json=workflow_data
    )
    
    if response.status_code in [200, 201]:
        workflow = response.json()
        workflow_id = workflow['id']
        print(f"✅ Workflow created successfully with ID: {workflow_id}")
        
        # Try to activate it
        activate_response = requests.patch(
            f'{N8N_BASE_URL}/api/v1/workflows/{workflow_id}',
            headers=headers,
            json={'active': True}
        )
        
        if activate_response.status_code == 200:
            print(f"✅ Workflow activated successfully!")
            return workflow_id
        else:
            print(f"⚠️ Workflow created but activation failed: {activate_response.status_code}")
            print(f"Response: {activate_response.text}")
            return workflow_id
    else:
        print(f"❌ Failed to create workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    workflow_id = create_compatible_workflow()
    print(f"Workflow ID: {workflow_id}")
