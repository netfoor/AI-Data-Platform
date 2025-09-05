import requests

API_BASE = "http://localhost:8001"

print("🎯 Getting the actual results of the June 2025 query")

query = "SELECT platform, SUM(spend) as total_spend FROM raw_ads_spend WHERE date >= '2025-06-01' AND date <= '2025-06-30' GROUP BY platform ORDER BY total_spend DESC LIMIT 10"

try:
    response = requests.post(
        f"{API_BASE}/execute-sql",
        json={"query": query, "format": "json"},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Query successful!")
        print(f"Number of results: {len(result['data'])}")
        print(f"Results:")
        for row in result['data']:
            print(f"  Platform: {row['platform']}, Total Spend: ${row['total_spend']}")
    else:
        print(f"❌ Error: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n🗓️ Let's also check the date range:")
date_query = "SELECT MIN(date) as min_date, MAX(date) as max_date FROM raw_ads_spend"

try:
    response = requests.post(f"{API_BASE}/execute-sql", json={"query": date_query, "format": "json"})
    if response.status_code == 200:
        result = response.json()
        print(f"Date range: {result['data'][0]}")
except Exception as e:
    print(f"Date range error: {e}")
