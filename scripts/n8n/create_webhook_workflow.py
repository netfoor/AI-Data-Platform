import os
import json
import requests

# Webhook workflow creation script
WORKFLOW_JSON_FILE = 'webhook-workflow.json'
API_KEY = os.getenv('N8N_API_KEY', 'n8n_api_key_1a2b3c4d5e6f')
N8N_BASE_URL = 'http://n8n:5678'

def create_webhook_workflow():
    with open(WORKFLOW_JSON_FILE, 'r') as f:
        workflow_data = json.load(f)
    
    headers = {
        'X-N8N-API-KEY': API_KEY,
        'Content-Type': 'application/json'
    }
    
    print(f"Creating webhook workflow: {workflow_data['name']}")
    
    response = requests.post(
        f'{N8N_BASE_URL}/api/v1/workflows',
        headers=headers,
        json=workflow_data
    )
    
    if response.status_code in [200, 201]:
        workflow = response.json()
        workflow_id = workflow['id']
        print(f"✅ Webhook workflow created successfully with ID: {workflow_id}")
        
        # Try to activate the webhook workflow
        try:
            activate_response = requests.post(
                f'{N8N_BASE_URL}/api/v1/workflows/{workflow_id}/activate',
                headers=headers
            )
            
            print(f"Activation attempt: {activate_response.status_code}")
            
            if activate_response.status_code == 200:
                print(f"✅ Webhook workflow activated successfully!")
                
                # Get the webhook URL
                status_response = requests.get(f'{N8N_BASE_URL}/api/v1/workflows/{workflow_id}', headers=headers)
                if status_response.status_code == 200:
                    workflow_details = status_response.json()
                    print(f"✅ Workflow is active: {workflow_details.get('active', False)}")
                    
                    # The webhook URL will be: http://localhost:5678/webhook/trigger-ingestion
                    webhook_url = f"{N8N_BASE_URL}/webhook/trigger-ingestion"
                    print(f"🎣 Webhook URL: {webhook_url}")
                    print(f"📋 You can trigger the workflow by sending a POST request to this URL")
                
                return workflow_id
            else:
                print(f"❌ Activation failed: {activate_response.text}")
                return workflow_id
                
        except Exception as e:
            print(f"Error activating workflow: {e}")
            return workflow_id
        
    else:
        print(f"❌ Failed to create webhook workflow: {response.status_code}")
        print(f"Response: {response.text}")
        return None

if __name__ == "__main__":
    workflow_id = create_webhook_workflow()
    print(f"Final workflow ID: {workflow_id}")
