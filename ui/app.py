import os
import json
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def safe_dataframe(data):
    """Safely create a DataFrame from various data structures."""
    try:
        if isinstance(data, list):
            if not data:
                return pd.DataFrame()
            # If list of dicts, use directly
            if all(isinstance(item, dict) for item in data):
                return pd.DataFrame(data)
            # If list of simple values, create single column
            else:
                return pd.DataFrame(data, columns=['value'])
        elif isinstance(data, dict):
            # If dict has values that are lists of same length, use as columns
            if all(isinstance(v, list) for v in data.values()) and len(set(len(v) for v in data.values())) <= 1:
                return pd.DataFrame(data)
            # Otherwise, single row
            else:
                return pd.DataFrame([data])
        else:
            # Single value
            return pd.DataFrame([{'value': data}])
    except Exception as e:
        st.error(f"Error creating DataFrame: {e}")
        return pd.DataFrame()

def get_api_base():
    # Si se define API_BASE en el entorno, úsalo
    env_base = os.getenv("API_BASE")
    if env_base:
        return env_base
    # Si está corriendo en Docker, usa el nombre del servicio
    if os.path.exists("/.dockerenv"):
        return "http://api:8000"
    # Si está local, usa el puerto publicado
    return "http://localhost:8001"

API_BASE = get_api_base()

st.set_page_config(page_title="AI Data Platform", layout="wide")
st.title("AI Data Platform Dashboard")

# Health Check
st.subheader("System Status")
col1, col2, col3 = st.columns(3)

with col1:
    try:
        response = requests.get(f"{API_BASE}/platform-info")
        if response.status_code == 200:
            st.success("✅ API Service: Online")
            info = response.json()
            st.text(f"Version: {info.get('version', 'Unknown')}")
        else:
            st.error("❌ API Service: Offline")
    except:
        st.error("❌ API Service: Connection Failed")

with col2:
    try:
        response = requests.post(f"{API_BASE}/n8n/test", json={})
        if response.status_code == 200:
            st.success("✅ n8n Integration: Connected")
        else:
            st.error("❌ n8n Integration: Failed")
    except:
        st.error("❌ n8n Integration: Connection Failed")

with col3:
    try:
        response = requests.post(f"{API_BASE}/sql-query", 
                              json={"query": "SELECT COUNT(*) as count FROM ads_spend", "query_name": "count_check"})
        if response.status_code == 200:
            result = response.json()
            count = result.get('data', [{}])[0].get('count', 0) if result.get('data') else 0
            st.success(f"✅ Database: {count} records")
        else:
            st.error("❌ Database: Query Failed")
    except:
        st.error("❌ Database: Connection Failed")

st.divider()

# Data Ingestion
st.subheader("Data Ingestion")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Ingest CSV Data"):
        try:
            response = requests.post(f"{API_BASE}/ingest", 
                                   json={"csv_file_path": "/app/data/ads_spend.csv"})
            if response.status_code == 200:
                st.success("CSV data ingested successfully!")
                st.session_state["ingest_result"] = response.json()
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("Setup n8n Workflow"):
        try:
            response = requests.post(f"{API_BASE}/n8n/setup", 
                                   json={"csv_file_path": "/app/data/ads_spend.csv"})
            if response.status_code == 200:
                st.success("n8n workflow setup successfully!")
                st.session_state["n8n_result"] = response.json()
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

with col3:
    if st.button("Ingest via n8n"):
        try:
            response = requests.post(f"{API_BASE}/n8n/ingest", 
                                   json={"file_path": "/app/data/ads_spend.csv"})
            if response.status_code == 200:
                st.success("Data ingested via n8n successfully!")
                st.session_state["n8n_ingest"] = response.json()
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

# Add a new row for webhook ingestion
col1_webhook, col2_webhook, col3_webhook = st.columns(3)

with col1_webhook:
    st.empty()  # Spacing

with col2_webhook:
    if st.button("🎣 Trigger Webhook Ingestion", key="webhook_ingest"):
        try:
            response = requests.post(f"{API_BASE}/n8n/webhook-ingest", 
                                   json={"csv_file_path": "ads_spend.csv"})
            if response.status_code == 200:
                st.success("🚀 Webhook ingestion triggered successfully!")
                result = response.json()
                st.json(result)
                st.session_state["webhook_result"] = result
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")

with col3_webhook:
    st.empty()  # Spacing

st.divider()

# Analytics
st.subheader("Analytics Dashboard")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Metrics (June 2025)")
    try:
        r = requests.get(f"{API_BASE}/metrics", params={"start_date": "2025-06-01", "end_date": "2025-06-30"})
        if r.status_code == 200:
            metrics_data = r.json()
            
            if isinstance(metrics_data, dict) and "metrics" in metrics_data:
                # Convert single metrics dict to a DataFrame
                metrics_dict = metrics_data["metrics"]
                df_metrics = safe_dataframe(metrics_dict)
            elif isinstance(metrics_data, dict) and "data" in metrics_data:
                df_metrics = safe_dataframe(metrics_data["data"])
            elif isinstance(metrics_data, list):
                df_metrics = safe_dataframe(metrics_data)
            else:
                # Handle unexpected format - show raw data and create empty DataFrame
                st.warning("Unexpected data format received from API")
                st.json(metrics_data)
                df_metrics = pd.DataFrame()
                
            if not df_metrics.empty:
                st.dataframe(df_metrics)
            else:
                st.info("No metrics data available.")
        else:
            st.error(f"Failed to fetch metrics: {r.status_code}")
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")

    st.subheader("Time Analysis (Last 30 vs Prior 30)")
    try:
        r = requests.get(f"{API_BASE}/time-analysis")
        if r.status_code == 200:
            ta_data = r.json()
            if isinstance(ta_data, dict) and "current" in ta_data and "previous" in ta_data:
                st.metric("Current Period", ta_data["current"])
                st.metric("Previous Period", ta_data["previous"])
                if "change" in ta_data:
                    st.metric("Change", ta_data["change"])
            elif isinstance(ta_data, dict):
                st.dataframe(safe_dataframe(ta_data))
            else:
                st.json(ta_data)
        else:
            st.error(f"Failed to fetch time analysis: {r.status_code}")
    except Exception as e:
        st.error(f"Error fetching time analysis: {e}")

with col2:
    st.subheader("Platform Metrics (June 2025)")
    try:
        r = requests.get(f"{API_BASE}/platform-metrics", params={"start_date": "2025-06-01", "end_date": "2025-06-30"})
        if r.status_code == 200:
            plat_data = r.json()
            
            if isinstance(plat_data, dict) and "platform_metrics" in plat_data:
                df_plat = safe_dataframe(plat_data["platform_metrics"])
            elif isinstance(plat_data, dict) and "data" in plat_data:
                df_plat = safe_dataframe(plat_data["data"])
            elif isinstance(plat_data, list):
                df_plat = safe_dataframe(plat_data)
            else:
                # Handle unexpected format - show raw data and create empty DataFrame
                st.warning("Unexpected data format received from API")
                st.json(plat_data)
                df_plat = pd.DataFrame()
                
            if not df_plat.empty:
                st.dataframe(df_plat)
                # Graficar si hay columnas numéricas
                num_cols = df_plat.select_dtypes(include="number").columns
                if len(num_cols) > 0:
                    fig = px.bar(df_plat, x=df_plat.columns[0], y=num_cols[0], title=f"{num_cols[0]} by {df_plat.columns[0]}")
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No platform metrics available.")
        else:
            st.error(f"Failed to fetch platform metrics: {r.status_code}")
    except Exception as e:
        st.error(f"Error fetching platform metrics: {e}")

st.divider()

# Results Display
def show_result(title, result):
    if isinstance(result, dict) and ("data" in result or "result" in result):
        key = "data" if "data" in result else "result"
        df = safe_dataframe(result[key])
        st.subheader(title)
        st.dataframe(df)
        # Graficar si es posible
        if not df.empty and len(df.columns) >= 2:
            fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=f"{title} - {df.columns[1]} by {df.columns[0]}")
            st.plotly_chart(fig, use_container_width=True)
    elif isinstance(result, list):
        st.subheader(title)
        st.dataframe(safe_dataframe(result))
    elif isinstance(result, dict):
        st.subheader(title)
        st.dataframe(safe_dataframe(result))
    else:
        st.subheader(title)
        st.write(result)

# Display results from session state
if "ingest_result" in st.session_state:
    show_result("CSV Ingestion Result", st.session_state["ingest_result"])

if "n8n_result" in st.session_state:
    show_result("n8n Workflow Result", st.session_state["n8n_result"])

if "n8n_ingest" in st.session_state:
    show_result("n8n Ingestion Result", st.session_state["n8n_ingest"])

st.divider()

# SQL Query Interface
st.subheader("SQL Query Interface")
query = st.text_area("Enter SQL Query:", value="SELECT platform, SUM(spend) as total_spend FROM raw_ads_spend WHERE date >= '2025-06-01' AND date <= '2025-06-30' GROUP BY platform ORDER BY total_spend DESC LIMIT 10")

if st.button("Execute Query"):
    try:
        response = requests.post(f"{API_BASE}/execute-sql", json={"query": query, "format": "json"})
        if response.status_code == 200:
            result = response.json()
            show_result("Query Result", result)
        else:
            st.error(f"Query failed: {response.text}")
    except Exception as e:
        st.error(f"Error executing query: {e}")

st.divider()

# Natural Language Query
st.subheader("Natural Language Query")
nlq = st.text_input("Ask a question about your data:", value="What were the total conversions by platform in June 2025?")

if st.button("Ask"):
    try:
        nlq_payload = {
            "question": nlq,
            "start_date": "2025-06-01",
            "end_date": "2025-06-30"
        }
        response = requests.post(f"{API_BASE}/nlq", json=nlq_payload)
        if response.status_code == 200:
            result = response.json()
            st.write("**SQL Query Generated:**")
            st.code(result.get("sql", "No SQL generated"))
            if "data" in result:
                show_result("Query Result", result)
        else:
            st.error(f"NLQ failed: {response.text}")
    except Exception as e:
        st.error(f"Error with natural language query: {e}")
