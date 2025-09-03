import os
import json
import requests
import streamlit as st

API_BASE = os.getenv("API_BASE", "http://localhost:8001")

st.set_page_config(page_title="AI Data Platform", layout="wide")
st.title("AI Data Platform Dashboard")

with st.sidebar:
    st.header("Actions")
    if st.button("Run Ingestion"):
        payload = {"csv_file_path": "data/ads_spend.csv"}
        r = requests.post(f"{API_BASE}/ingest", json=payload, timeout=60)
        st.session_state["ingest_result"] = r.json()
    question = st.text_input("Ask a question")
    if st.button("Ask NLQ") and question:
        payload = {"question": question}
        r = requests.post(f"{API_BASE}/nlq", json=payload, timeout=60)
        st.session_state["nlq_result"] = r.json()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Metrics (June 2025)")
    r = requests.get(f"{API_BASE}/metrics", params={"start_date": "2025-06-01", "end_date": "2025-06-30"})
    st.json(r.json())
    st.subheader("Time Analysis (Last 30 vs Prior 30)")
    r = requests.get(f"{API_BASE}/time-analysis")
    st.json(r.json())

with col2:
    st.subheader("Platform Metrics (June 2025)")
    r = requests.get(f"{API_BASE}/platform-metrics", params={"start_date": "2025-06-01", "end_date": "2025-06-30"})
    st.json(r.json())
    if "ingest_result" in st.session_state:
        st.subheader("Latest Ingestion Result")
        st.json(st.session_state["ingest_result"])
    if "nlq_result" in st.session_state:
        st.subheader("NLQ Result")
        st.json(st.session_state["nlq_result"])


