import duckdb
import pandas as pd
import sys

# Test script to check database content and SQL queries
print("🔍 Checking database content and SQL queries...")

try:
    # Connect to database
    conn = duckdb.connect('/app/data/ai_data_platform.duckdb')
    
    print("\n1. 📊 Checking available tables:")
    tables_result = conn.execute("SHOW TABLES").fetchall()
    print(f"Available tables: {tables_result}")
    
    print("\n2. 📋 Checking ads_spend table structure:")
    try:
        describe_result = conn.execute("DESCRIBE ads_spend").fetchall()
        print("Table structure:")
        for row in describe_result:
            print(f"  {row}")
    except Exception as e:
        print(f"Error describing ads_spend table: {e}")
    
    print("\n3. 📈 Checking row count:")
    try:
        count_result = conn.execute("SELECT COUNT(*) FROM ads_spend").fetchone()
        print(f"Total rows in ads_spend: {count_result[0]}")
    except Exception as e:
        print(f"Error counting rows: {e}")
    
    print("\n4. 📅 Checking date range:")
    try:
        date_range = conn.execute("SELECT MIN(date) as min_date, MAX(date) as max_date FROM ads_spend").fetchone()
        print(f"Date range: {date_range[0]} to {date_range[1]}")
    except Exception as e:
        print(f"Error checking date range: {e}")
    
    print("\n5. 🎯 Testing the problematic query:")
    query = """
    SELECT platform, SUM(spend) as total_spend 
    FROM ads_spend 
    WHERE date >= '2025-06-01' AND date <= '2025-06-30' 
    GROUP BY platform 
    ORDER BY total_spend DESC 
    LIMIT 10
    """
    try:
        result = conn.execute(query).fetchall()
        print(f"Query result: {result}")
        print(f"Number of results: {len(result)}")
    except Exception as e:
        print(f"Error executing query: {e}")
    
    print("\n6. 🔍 Checking sample data:")
    try:
        sample = conn.execute("SELECT * FROM ads_spend LIMIT 5").fetchall()
        print("Sample data:")
        for row in sample:
            print(f"  {row}")
    except Exception as e:
        print(f"Error getting sample data: {e}")
    
    print("\n7. 🗓️ Checking dates in 2025-06:")
    try:
        june_data = conn.execute("SELECT COUNT(*) FROM ads_spend WHERE date >= '2025-06-01' AND date <= '2025-06-30'").fetchone()
        print(f"Rows in June 2025: {june_data[0]}")
    except Exception as e:
        print(f"Error checking June data: {e}")
    
    print("\n8. 🔄 Alternative date formats:")
    try:
        # Try different date formats
        alt_query = conn.execute("SELECT date, platform, spend FROM ads_spend WHERE date LIKE '2025-06%' LIMIT 5").fetchall()
        print(f"Data with LIKE pattern: {alt_query}")
    except Exception as e:
        print(f"Error with alternative date format: {e}")
    
    conn.close()
    print("\n✅ Database check completed!")
    
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
