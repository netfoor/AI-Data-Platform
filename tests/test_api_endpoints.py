"""
API endpoint tests
Tests all REST API endpoints for proper functionality and error handling
"""
import pytest
import json
from datetime import date
from fastapi.testclient import TestClient

from ai_data_platform.api.rest_api import app


class TestAPIEndpoints:
    """Test all API endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    @pytest.mark.api
    def test_root_endpoint(self):
        """Test root endpoint returns API information"""
        response = self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["message"] == "AI Data Platform API"
        assert data["version"] == "1.0.0"
        assert data["status"] == "running"
        assert "metrics" in data["endpoints"]
        assert "ingest" in data["endpoints"]
        assert "nlq" in data["endpoints"]
    
    @pytest.mark.api
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert "timestamp" in data
    
    @pytest.mark.api
    def test_metrics_endpoint_basic(self):
        """Test metrics endpoint without parameters"""
        response = self.client.get("/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period" in data
        assert "metrics" in data
        assert "timestamp" in data
        
        metrics = data["metrics"]
        assert "total_spend" in metrics
        assert "total_conversions" in metrics
        assert "cac" in metrics
        assert "roas" in metrics
    
    @pytest.mark.api
    def test_metrics_endpoint_with_dates(self):
        """Test metrics endpoint with date parameters"""
        params = {
            "start_date": "2025-06-01",
            "end_date": "2025-06-30"
        }
        
        response = self.client.get("/metrics", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        period = data["period"]
        assert period["start_date"] == "2025-06-01"
        assert period["end_date"] == "2025-06-30"
    
    @pytest.mark.api
    def test_metrics_endpoint_invalid_dates(self):
        """Test metrics endpoint with invalid date range"""
        params = {
            "start_date": "2025-06-30",
            "end_date": "2025-06-01"  # Start after end
        }
        
        response = self.client.get("/metrics", params=params)
        
        assert response.status_code == 400
        data = response.json()
        assert "Start date must be before or equal to end date" in data["detail"]
    
    @pytest.mark.api
    def test_time_analysis_endpoint(self):
        """Test time analysis endpoint"""
        response = self.client.get("/time-analysis")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "analysis" in data
        assert "timestamp" in data
        
        analysis = data["analysis"]
        assert "current_period" in analysis
        assert "previous_period" in analysis
        assert "summary" in analysis
        assert "comparison" in analysis
    
    @pytest.mark.api
    def test_daily_trends_endpoint(self):
        """Test daily trends endpoint"""
        response = self.client.get("/daily-trends")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "trends" in data
        assert "timestamp" in data
        
        trends = data["trends"]
        assert "days_analyzed" in trends
        assert "daily_metrics" in trends
    
    @pytest.mark.api
    def test_daily_trends_with_custom_days(self):
        """Test daily trends endpoint with custom days parameter"""
        params = {"days": 7}
        
        response = self.client.get("/daily-trends", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        trends = data["trends"]
        assert trends["days_analyzed"] == 7
    
    @pytest.mark.api
    def test_daily_trends_invalid_days(self):
        """Test daily trends endpoint with invalid days parameter"""
        params = {"days": 0}  # Invalid: must be >= 1
        
        response = self.client.get("/daily-trends", params=params)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_platform_metrics_endpoint(self):
        """Test platform metrics endpoint"""
        response = self.client.get("/platform-metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "period" in data
        assert "platform_metrics" in data
        assert "timestamp" in data
    
    @pytest.mark.api
    def test_platform_metrics_with_dates(self):
        """Test platform metrics endpoint with date parameters"""
        params = {
            "start_date": "2025-06-01",
            "end_date": "2025-06-30"
        }
        
        response = self.client.get("/platform-metrics", params=params)
        
        assert response.status_code == 200
        data = response.json()
        
        period = data["period"]
        assert period["start_date"] == "2025-06-01"
        assert period["end_date"] == "2025-06-30"
    
    @pytest.mark.api
    def test_ingest_endpoint_basic(self):
        """Test ingest endpoint with basic payload"""
        payload = {"csv_file_path": "data/ads_spend.csv"}
        
        response = self.client.post("/ingest", json=payload)
        
        assert response.status_code in [200, 207]  # Success or partial success
        data = response.json()
        
        assert "status" in data
        assert "summary" in data
        
        summary = data["summary"]
        assert "batch_id" in summary
        assert "source_file" in summary
        assert "success" in summary
    
    @pytest.mark.api
    def test_ingest_endpoint_with_batch_id(self):
        """Test ingest endpoint with custom batch ID"""
        payload = {
            "csv_file_path": "data/ads_spend.csv",
            "batch_id": "test_batch_123"
        }
        
        response = self.client.post("/ingest", json=payload)
        
        assert response.status_code in [200, 207]
        data = response.json()
        
        summary = data["summary"]
        assert summary["batch_id"] == "test_batch_123"
    
    @pytest.mark.api
    def test_ingest_endpoint_invalid_file(self):
        """Test ingest endpoint with invalid file path"""
        payload = {"csv_file_path": "nonexistent_file.csv"}
        
        response = self.client.post("/ingest", json=payload)
        
        # Should fail but return structured error
        assert response.status_code in [400, 500]
    
    @pytest.mark.api
    def test_nlq_endpoint_basic(self):
        """Test NLQ endpoint with basic question"""
        payload = {"question": "Show me daily metrics"}
        
        response = self.client.post("/nlq", json=payload)
        
        assert response.status_code in [200, 400]  # Success or error
        data = response.json()
        
        assert "query_name" in data
        assert "parameters" in data
        assert "success" in data
    
    @pytest.mark.api
    def test_nlq_endpoint_with_dates(self):
        """Test NLQ endpoint with date parameters"""
        payload = {
            "question": "Compare CAC and ROAS last 30 days vs prior 30 days",
            "start_date": "2025-06-01",
            "end_date": "2025-06-30",
            "previous_start_date": "2025-05-01",
            "previous_end_date": "2025-05-31"
        }
        
        response = self.client.post("/nlq", json=payload)
        
        assert response.status_code in [200, 400]
        data = response.json()
        
        assert "query_name" in data
        assert "parameters" in data
    
    @pytest.mark.api
    def test_nlq_endpoint_empty_question(self):
        """Test NLQ endpoint with empty question"""
        payload = {"question": ""}
        
        response = self.client.post("/nlq", json=payload)
        
        assert response.status_code in [200, 400]
        data = response.json()
        
        assert "query_name" in data
        assert data["query_name"] == "daily_metrics"  # Default fallback


class TestAPIErrorHandling:
    """Test API error handling and edge cases"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = TestClient(app)
    
    @pytest.mark.api
    def test_metrics_endpoint_malformed_date(self):
        """Test metrics endpoint with malformed date"""
        params = {"start_date": "invalid-date"}
        
        response = self.client.get("/metrics", params=params)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_ingest_endpoint_missing_payload(self):
        """Test ingest endpoint with missing payload"""
        response = self.client.post("/ingest")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_nlq_endpoint_missing_payload(self):
        """Test NLQ endpoint with missing payload"""
        response = self.client.post("/nlq")
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.api
    def test_nonexistent_endpoint(self):
        """Test 404 for nonexistent endpoint"""
        response = self.client.get("/nonexistent")
        
        assert response.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])
