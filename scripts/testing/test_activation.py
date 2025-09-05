import os
import sys
sys.path.append('/app')

from ai_data_platform.api.n8n_api_client import N8nAPIClient

# Setup API client
API_KEY = os.getenv('N8N_API_KEY', 'n8n_api_key_1a2b3c4d5e6f')
N8N_BASE_URL = 'http://n8n:5678'

client = N8nAPIClient(N8N_BASE_URL, API_KEY)

# Try to activate the workflow we already created
workflow_id = "8niYK2ZMrGgLcgSh"  # From previous creation

print(f"Testing connection...")
if client.test_connection():
    print("✅ Connected to n8n")
    
    print(f"Getting workflow status...")
    status = client.get_workflow_status(workflow_id)
    print(f"Current status: {status}")
    
    if not status.get('active', False):
        print(f"Attempting to activate workflow {workflow_id}...")
        success = client.activate_workflow_by_id(workflow_id)
        if success:
            print("✅ Workflow activated!")
            
            # Check status again
            status = client.get_workflow_status(workflow_id)
            print(f"New status: {status}")
        else:
            print("❌ Failed to activate workflow")
    else:
        print("✅ Workflow is already active")
else:
    print("❌ Cannot connect to n8n")
