import requests
import json

# Test API SQL endpoint directly
API_BASE = "http://localhost:8001"

print("🔍 Testing SQL queries via API...")

# Test queries
queries = [
    "SHOW TABLES",
    "SELECT COUNT(*) FROM ads_spend",
    "DESCRIBE ads_spend",
    "SELECT MIN(date) as min_date, MAX(date) as max_date FROM ads_spend",
    "SELECT * FROM ads_spend LIMIT 3",
    "SELECT date, platform, spend FROM ads_spend WHERE date LIKE '2025-06%' LIMIT 5",
    "SELECT platform, SUM(spend) as total_spend FROM ads_spend WHERE date >= '2025-06-01' AND date <= '2025-06-30' GROUP BY platform ORDER BY total_spend DESC LIMIT 10"
]

for i, query in enumerate(queries, 1):
    print(f"\n{i}. 🔍 Query: {query}")
    try:
        response = requests.post(
            f"{API_BASE}/execute-sql",
            json={"query": query, "format": "json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n🔄 Testing ingestion to refresh data...")
try:
    response = requests.post(f"{API_BASE}/ingest", json={"csv_file_path": "ads_spend.csv"})
    print(f"Ingestion result: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Ingestion error: {e}")
