import requests

API_BASE = "http://localhost:8001"

print("🔍 Testing the fixed analytics endpoints...")

# Test the endpoints that were failing
endpoints = [
    "/metrics?start_date=2025-06-01&end_date=2025-06-30",
    "/platform-metrics?start_date=2025-06-01&end_date=2025-06-30", 
    "/time-analysis"
]

for endpoint in endpoints:
    print(f"\n🔍 Testing: {endpoint}")
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            
            # Show a summary of the data
            if isinstance(result, dict):
                print(f"  Keys: {list(result.keys())}")
                if 'metrics' in result:
                    print(f"  Metrics: {result['metrics']}")
                elif 'data' in result:
                    print(f"  Data length: {len(result['data']) if isinstance(result['data'], list) else 'not a list'}")
            else:
                print(f"  Result type: {type(result)}")
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

print("\n🎯 Testing specific SQL query that should work now:")
sql_endpoint = "/execute-sql"
query = "SELECT platform, SUM(spend) as total_spend FROM raw_ads_spend WHERE date >= '2025-06-01' AND date <= '2025-06-30' GROUP BY platform ORDER BY total_spend DESC"

try:
    response = requests.post(f"{API_BASE}{sql_endpoint}", json={"query": query})
    if response.status_code == 200:
        result = response.json()
        print(f"✅ SQL Query works: {result['data']}")
    else:
        print(f"❌ SQL Error: {response.text}")
except Exception as e:
    print(f"❌ SQL Exception: {e}")
