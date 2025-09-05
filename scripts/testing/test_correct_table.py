import requests

API_BASE = "http://localhost:8001"

print("🎯 Testing with correct table name: raw_ads_spend")

# Test queries with correct table name
queries = [
    "SHOW TABLES",
    "SELECT COUNT(*) FROM raw_ads_spend",
    "DESCRIBE raw_ads_spend", 
    "SELECT MIN(date) as min_date, MAX(date) as max_date FROM raw_ads_spend",
    "SELECT * FROM raw_ads_spend LIMIT 3",
    "SELECT date, platform, spend FROM raw_ads_spend WHERE date LIKE '2025-06%' LIMIT 5",
    "SELECT platform, SUM(spend) as total_spend FROM raw_ads_spend WHERE date >= '2025-06-01' AND date <= '2025-06-30' GROUP BY platform ORDER BY total_spend DESC LIMIT 10"
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
            if "data" in result and result["data"]:
                print(f"✅ Success: Found {len(result['data'])} results")
                if i <= 3:  # Show data for first few queries
                    print(f"Data: {result['data']}")
            else:
                print(f"✅ Success but no data: {result}")
        else:
            print(f"❌ Error {response.status_code}: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
