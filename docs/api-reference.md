# AI Data Platform - API Reference

## 🔌 API Overview

The AI Data Platform provides a RESTful API for data ingestion, analytics, and natural language queries. All endpoints return JSON responses and support standard HTTP methods.

### Base URL
```
http://localhost:8001
```

### API Documentation
- **Interactive Docs**: http://localhost:8001/docs (Swagger UI)
- **OpenAPI Schema**: http://localhost:8001/openapi.json
- **ReDoc**: http://localhost:8001/redoc

### Authentication
Currently, the API operates without authentication. For production use, implement JWT-based authentication.

### Rate Limiting
- **Default**: 100 requests per minute per IP
- **Burst**: 200 requests per minute per IP
- **Headers**: Rate limit information included in response headers

---

## 📊 Core Endpoints

### 1. **Root Endpoint**
**GET** `/`

Returns basic API information and available endpoints.

#### Request
```bash
curl http://localhost:8001/
```

#### Response
```json
{
  "message": "AI Data Platform API",
  "version": "1.0.0",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "ingest": "/ingest",
    "metrics": "/metrics",
    "nlq": "/nlq",
    "time_analysis": "/time-analysis",
    "daily_trends": "/daily-trends",
    "platform_metrics": "/platform-metrics"
  },
  "timestamp": "2025-09-03T10:00:00Z"
}
```

### 2. **Health Check**
**GET** `/health`

Returns system health status and database connectivity.

#### Request
```bash
curl http://localhost:8001/health
```

#### Response
```json
{
  "status": "healthy",
  "timestamp": "2025-09-03T10:00:00Z",
  "services": {
    "api": "running",
    "database": "connected",
    "version": "1.0.0"
  },
  "uptime": "2h 15m 30s"
}
```

---

## 📥 Data Ingestion

### 3. **Data Ingestion**
**POST** `/ingest`

Processes CSV files and ingests data into the platform.

#### Request
```bash
curl -X POST "http://localhost:8001/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "csv_file_path": "data/ads_spend.csv",
    "batch_id": "batch_001"
  }'
```

#### Request Body
```json
{
  "csv_file_path": "string (required)",
  "batch_id": "string (optional)"
}
```

#### Response
```json
{
  "status": "success",
  "summary": {
    "total_records_read": 1000,
    "valid_records": 995,
    "records_inserted": 995,
    "records_failed": 5,
    "validation_success_rate": 99.5,
    "insertion_success_rate": 100.0,
    "batch_id": "batch_001",
    "source_file": "data/ads_spend.csv",
    "duration_seconds": 2.45,
    "validation_errors": [
      {
        "row": 45,
        "error": "Invalid platform value: Facebook (use Meta)",
        "data": "2025-06-01,Facebook,Account1,Campaign1,US,Mobile,100.00,50,1000,5"
      }
    ],
    "insertion_errors": []
  }
}
```

#### Error Response
```json
{
  "status": "failed",
  "error": "File not found: data/ads_spend.csv",
  "timestamp": "2025-09-03T10:00:00Z"
}
```

---

## 📈 Analytics & Metrics

### 4. **KPI Metrics**
**GET** `/metrics`

Retrieves KPI metrics for specified date range and dimensions.

#### Request
```bash
curl "http://localhost:8001/metrics?start_date=2025-06-01&end_date=2025-06-30&platform=Meta&country=US"
```

#### Query Parameters
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `platform` (optional): Filter by platform (Meta, Google)
- `account` (optional): Filter by account name
- `campaign` (optional): Filter by campaign name
- `country` (optional): Filter by country
- `device` (optional): Filter by device type

#### Response
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-06-01",
      "platform": "Meta",
      "account": "CompanyA",
      "campaign": "SummerSale",
      "country": "US",
      "device": "Mobile",
      "total_spend": 1500.00,
      "total_conversions": 75,
      "cac": 20.00,
      "roas": 5.00,
      "revenue": 7500.00
    }
  ],
  "row_count": 1,
  "execution_time": 0.045,
  "summary": {
    "total_spend": 1500.00,
    "total_conversions": 75,
    "avg_cac": 20.00,
    "avg_roas": 5.00,
    "total_revenue": 7500.00
  }
}
```

### 5. **Time Analysis**
**GET** `/time-analysis`

Performs period-over-period analysis for marketing metrics.

#### Request
```bash
curl "http://localhost:8001/time-analysis?start_date=2025-06-01&end_date=2025-06-30&previous_start_date=2025-05-01&previous_end_date=2025-05-31"
```

#### Query Parameters
- `start_date` (required): Current period start date
- `end_date` (required): Current period end date
- `previous_start_date` (required): Previous period start date
- `previous_end_date` (required): Previous period end date
- `platform` (optional): Filter by platform
- `dimensions` (optional): Comma-separated list of dimensions

#### Response
```json
{
  "success": true,
  "data": [
    {
      "metric": "total_spend",
      "current_value": 15000.00,
      "previous_value": 12000.00,
      "change_amount": 3000.00,
      "change_percent": 25.0,
      "trend": "increasing"
    },
    {
      "metric": "total_conversions",
      "current_value": 750,
      "previous_value": 600,
      "change_amount": 150,
      "change_percent": 25.0,
      "trend": "increasing"
    },
    {
      "metric": "cac",
      "current_value": 20.00,
      "previous_value": 20.00,
      "change_amount": 0.00,
      "change_percent": 0.0,
      "trend": "stable"
    }
  ],
  "row_count": 3,
  "execution_time": 0.078,
  "summary": {
    "current_period": "2025-06-01 to 2025-06-30",
    "previous_period": "2025-05-01 to 2025-05-31",
    "overall_trend": "positive"
  }
}
```

### 6. **Daily Trends**
**GET** `/daily-trends`

Retrieves daily performance trends for specified date range.

#### Request
```bash
curl "http://localhost:8001/daily-trends?start_date=2025-06-01&end_date=2025-06-30&platform=Meta"
```

#### Query Parameters
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `platform` (optional): Filter by platform
- `metric` (optional): Metric to analyze (spend, conversions, cac, roas)

#### Response
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-06-01",
      "total_spend": 500.00,
      "total_conversions": 25,
      "avg_cac": 20.00,
      "avg_roas": 5.00,
      "total_revenue": 2500.00
    },
    {
      "date": "2025-06-02",
      "total_spend": 550.00,
      "total_conversions": 28,
      "avg_cac": 19.64,
      "avg_roas": 5.09,
      "total_revenue": 2800.00
    }
  ],
  "row_count": 2,
  "execution_time": 0.034,
  "trends": {
    "spend_trend": "increasing",
    "conversions_trend": "increasing",
    "cac_trend": "decreasing",
    "roas_trend": "increasing"
  }
}
```

### 7. **Platform Metrics**
**GET** `/platform-metrics`

Compares performance metrics across different platforms.

#### Request
```bash
curl "http://localhost:8001/platform-metrics?start_date=2025-06-01&end_date=2025-06-30"
```

#### Query Parameters
- `start_date` (required): Start date in YYYY-MM-DD format
- `end_date` (required): End date in YYYY-MM-DD format
- `dimensions` (optional): Additional dimensions (country, device, campaign)

#### Response
```json
{
  "success": true,
  "data": [
    {
      "platform": "Meta",
      "total_spend": 8000.00,
      "total_conversions": 400,
      "avg_cac": 20.00,
      "avg_roas": 5.00,
      "total_revenue": 40000.00,
      "conversion_rate": 0.05,
      "spend_efficiency": 5.0
    },
    {
      "platform": "Google",
      "total_spend": 7000.00,
      "total_conversions": 350,
      "avg_cac": 20.00,
      "avg_roas": 5.00,
      "total_revenue": 35000.00,
      "conversion_rate": 0.05,
      "spend_efficiency": 5.0
    }
  ],
  "row_count": 2,
  "execution_time": 0.056,
  "summary": {
    "total_spend": 15000.00,
    "total_conversions": 750,
    "overall_cac": 20.00,
    "overall_roas": 5.00,
    "best_performing_platform": "Meta"
  }
}
```

---

## 🗣️ Natural Language Queries

### 8. **Natural Language Query**
**POST** `/nlq`

Processes natural language questions and returns structured data.

#### Request
```bash
curl -X POST "http://localhost:8001/nlq" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me Meta performance last month",
    "start_date": "2025-08-01",
    "end_date": "2025-08-31"
  }'
```

#### Request Body
```json
{
  "question": "string (required)",
  "start_date": "date (optional)",
  "end_date": "date (optional)",
  "previous_start_date": "date (optional)",
  "previous_end_date": "date (optional)"
}
```

#### Response
```json
{
  "success": true,
  "query_name": "platform_performance",
  "parameters": {
    "platform": "Meta",
    "start_date": "2025-08-01",
    "end_date": "2025-08-31"
  },
  "data": [
    {
      "platform": "Meta",
      "total_spend": 12000.00,
      "total_conversions": 600,
      "avg_cac": 20.00,
      "avg_roas": 5.00,
      "total_revenue": 60000.00
    }
  ],
  "row_count": 1,
  "execution_time": 0.123,
  "summary": "Retrieved Meta platform performance for August 2025"
}
```

#### Error Response
```json
{
  "success": false,
  "query_name": "unknown",
  "parameters": {},
  "error": "Unable to process question. Please rephrase.",
  "suggestions": [
    "Try: 'Show me daily metrics'",
    "Try: 'What is our total spend?'",
    "Try: 'Compare platform performance'"
  ],
  "execution_time": 0.045
}
```

---

## 🔍 SQL Query Interface

### 9. **Predefined Queries**
**POST** `/sql/predefined`

Executes predefined SQL queries with parameters.

#### Request
```bash
curl -X POST "http://localhost:8001/sql/predefined" \
  -H "Content-Type: application/json" \
  -d '{
    "query_name": "platform_performance",
    "parameters": {
      "start_date": "2025-06-01",
      "end_date": "2025-06-30"
    }
  }'
```

#### Available Query Types
- `daily_metrics`: Daily performance metrics
- `platform_performance`: Platform comparison
- `period_comparison`: Period-over-period analysis
- `campaign_analysis`: Campaign performance
- `geographic_insights`: Country and device analysis

#### Response
```json
{
  "success": true,
  "query_name": "platform_performance",
  "parameters": {
    "start_date": "2025-06-01",
    "end_date": "2025-06-30"
  },
  "data": [...],
  "row_count": 2,
  "execution_time": 0.067,
  "sql_query": "SELECT platform, SUM(total_spend) as total_spend...",
  "summary": "Platform performance comparison for June 2025"
}
```

### 10. **Custom SQL Queries**
**POST** `/sql/custom`

Executes custom SQL queries with parameter validation.

#### Request
```bash
curl -X POST "http://localhost:8001/sql/custom" \
  -H "Content-Type: application/json" \
  -d '{
    "sql_query": "SELECT platform, SUM(spend) FROM raw_ads_spend WHERE date BETWEEN ? AND ? GROUP BY platform",
    "parameters": ["2025-06-01", "2025-06-30"]
  }'
```

#### Request Body
```json
{
  "sql_query": "string (required)",
  "parameters": "array (optional)"
}
```

#### Response
```json
{
  "success": true,
  "data": [
    {
      "platform": "Meta",
      "total_spend": 8000.00
    },
    {
      "platform": "Google",
      "total_spend": 7000.00
    }
  ],
  "row_count": 2,
  "execution_time": 0.034,
  "sql_query": "SELECT platform, SUM(spend) FROM raw_ads_spend...",
  "warnings": []
}
```

---

## 🚨 Error Handling

### Standard Error Response Format
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-09-03T10:00:00Z",
  "details": {
    "field": "Additional error details",
    "suggestion": "How to fix the error"
  }
}
```

### Common Error Codes

#### HTTP 400 - Bad Request
- `INVALID_DATE_FORMAT`: Date parameter format is incorrect
- `MISSING_REQUIRED_PARAMETER`: Required parameter is missing
- `INVALID_PLATFORM_VALUE`: Platform value is not supported
- `INVALID_DATE_RANGE`: End date is before start date

#### HTTP 404 - Not Found
- `FILE_NOT_FOUND`: CSV file not found
- `QUERY_NOT_FOUND`: Predefined query doesn't exist
- `ENDPOINT_NOT_FOUND`: API endpoint not found

#### HTTP 422 - Validation Error
- `VALIDATION_ERROR`: Request data validation failed
- `INVALID_CSV_FORMAT`: CSV file format is incorrect
- `DATA_TYPE_MISMATCH`: Data type validation failed

#### HTTP 500 - Internal Server Error
- `DATABASE_ERROR`: Database operation failed
- `PROCESSING_ERROR`: Data processing failed
- `SYSTEM_ERROR`: Unexpected system error

### Error Response Examples

#### Invalid Date Format
```json
{
  "success": false,
  "error": "Invalid date format. Use YYYY-MM-DD format.",
  "error_code": "INVALID_DATE_FORMAT",
  "timestamp": "2025-09-03T10:00:00Z",
  "details": {
    "parameter": "start_date",
    "value": "06-01-2025",
    "expected_format": "YYYY-MM-DD"
  }
}
```

#### Missing Required Parameter
```json
{
  "success": false,
  "error": "Missing required parameter: start_date",
  "error_code": "MISSING_REQUIRED_PARAMETER",
  "timestamp": "2025-09-03T10:00:00Z",
  "details": {
    "missing_parameter": "start_date",
    "required_parameters": ["start_date", "end_date"]
  }
}
```

#### File Not Found
```json
{
  "success": false,
  "error": "File not found: data/ads_spend.csv",
  "error_code": "FILE_NOT_FOUND",
  "timestamp": "2025-09-03T10:00:00Z",
  "details": {
    "file_path": "data/ads_spend.csv",
    "suggestion": "Check file path and ensure file exists"
  }
}
```

---

## 📊 Response Headers

### Standard Headers
```
Content-Type: application/json
X-Request-ID: req_1234567890
X-Execution-Time: 0.045
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1640995200
```

### Rate Limiting Headers
```
X-Rate-Limit-Limit: 100
X-Rate-Limit-Remaining: 95
X-Rate-Limit-Reset: 1640995200
X-Rate-Limit-Reset-Time: 2025-09-03T11:00:00Z
```

---

## 🔧 API Configuration

### Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true
API_WORKERS=4

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200

# Database Configuration
DATABASE_PATH=data/ai_data_platform.duckdb
DATABASE_TIMEOUT=30

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/ai_data_platform.log
```

### CORS Configuration
```python
# CORS middleware configuration
CORS_ORIGINS = [
    "http://localhost:8501",  # Streamlit UI
    "http://localhost:5678",  # n8n workflows
    "http://127.0.0.1:8501",
    "http://127.0.0.1:5678"
]

CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
CORS_HEADERS = ["*"]
```

---

## 📈 Performance & Monitoring

### Response Time Benchmarks
- **Simple Queries**: < 100ms
- **Complex Analytics**: < 500ms
- **Data Ingestion**: < 2 seconds per 1000 records
- **Natural Language Processing**: < 1 second

### Monitoring Endpoints
- **Health Check**: `/health` - System status
- **Metrics**: `/metrics` - Performance metrics
- **Logs**: Check container logs for detailed information

### Performance Tips
1. **Use Date Ranges**: Limit data with specific date parameters
2. **Filter Early**: Apply platform/country filters in requests
3. **Batch Operations**: Use batch IDs for multiple data loads
4. **Cache Results**: Implement client-side caching for repeated queries

---

*This API reference provides comprehensive documentation for all endpoints. For interactive testing, use the Swagger UI at http://localhost:8001/docs.*
