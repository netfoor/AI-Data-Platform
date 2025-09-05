import requests
import json

# Test the webhook workflow
N8N_BASE_URL = 'http://n8n:5678'
webhook_url = f"{N8N_BASE_URL}/webhook/trigger-ingestion"

print(f"Testing webhook: {webhook_url}")

# Test payload
payload = {
    "csv_file_path": "ads_spend.csv",
    "batch_id": "test_webhook_batch_123"
}

try:
    response = requests.post(webhook_url, json=payload, timeout=30)
    print(f"Webhook response status: {response.status_code}")
    print(f"Webhook response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Webhook triggered successfully!")
    else:
        print("❌ Webhook failed")
        
except Exception as e:
    print(f"Error testing webhook: {e}")

# Also test with empty payload (should use defaults)
print("\nTesting with empty payload...")
try:
    response = requests.post(webhook_url, json={}, timeout=30)
    print(f"Empty payload response status: {response.status_code}")
    print(f"Empty payload response: {response.text}")
except Exception as e:
    print(f"Error testing empty payload: {e}")
