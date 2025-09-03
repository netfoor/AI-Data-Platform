# AI Data Platform - System Architecture

## 🏗️ High-Level System Design

The AI Data Platform follows a **layered, microservices architecture** that separates concerns and enables independent scaling of components.

### Architecture Principles

1. **Loose Coupling**: Services communicate through well-defined APIs
2. **High Cohesion**: Each service has a single, well-defined responsibility
3. **Stateless Design**: Services don't maintain state between requests
4. **Event-Driven**: Asynchronous processing through webhooks and events
5. **Data-Centric**: All operations revolve around data transformation and insights

## 🧩 System Components

### 1. **Frontend Layer (Streamlit UI)**
- **Port**: 8501
- **Technology**: Streamlit, Python
- **Purpose**: User interface for data interaction and visualization
- **Responsibilities**:
  - Data ingestion forms
  - Query input interfaces
  - Results visualization
  - Dashboard displays

### 2. **API Layer (FastAPI)**
- **Port**: 8001
- **Technology**: FastAPI, Python, Pydantic
- **Purpose**: Business logic and data access layer
- **Responsibilities**:
  - Request/response handling
  - Data validation
  - Business logic execution
  - Database interactions
  - Error handling and logging

### 3. **Workflow Layer (n8n)**
- **Port**: 5678
- **Technology**: n8n, Node.js
- **Purpose**: Workflow automation and orchestration
- **Responsibilities**:
  - Data ingestion workflows
  - Natural language query processing
  - Scheduled tasks
  - Error handling and notifications

### 4. **Data Layer (DuckDB)**
- **Technology**: DuckDB, SQL
- **Purpose**: Data storage and retrieval
- **Responsibilities**:
  - Raw data storage
  - KPI metrics storage
  - Query execution
  - Data integrity

## 🔄 Component Interactions

### Data Flow Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   User     │────►│  Streamlit  │────►│   FastAPI   │
│  Input     │     │     UI      │     │     API     │
└─────────────┘     └─────────────┘     └─────────────┘
                            │                   │
                            │                   ▼
                            │            ┌─────────────┐
                            │            │   DuckDB    │
                            │            │  Database   │
                            │            └─────────────┘
                            │                   ▲
                            ▼                   │
                     ┌─────────────┐            │
                     │    n8n      │────────────┘
                     │ Workflows   │
                     └─────────────┘
```

### Request Flow

1. **User Input**: User enters data or query in Streamlit UI
2. **UI Processing**: Streamlit validates input and sends HTTP request to FastAPI
3. **API Processing**: FastAPI validates request, executes business logic
4. **Data Access**: API queries DuckDB for data or executes operations
5. **Response**: Results returned through API to UI for display
6. **Workflow Trigger**: n8n workflows can be triggered by API calls or scheduled events

## 📊 Data Flow Diagrams

### Data Ingestion Flow

```
CSV File → n8n Workflow → FastAPI /ingest → ETL Pipeline → DuckDB
    │           │              │              │           │
    │           │              │              │           ▼
    │           │              │              │    Raw Data Tables
    │           │              │              │           │
    │           │              │              │           ▼
    │           │              │              │    KPI Computation
    │           │              │              │           │
    │           │              │              │           ▼
    │           │              │              │    KPI Metrics Tables
    │           │              │              │           │
    │           │              │              │           ▼
    │           │              │              │    Success Notification
    │           │              │              │           │
    ▼           ▼              ▼              ▼           ▼
File Read   Workflow    API Endpoint    Data      Database    User
Complete    Execution   Processing     Transform  Storage    Notification
```

### Natural Language Query Flow

```
User Question → n8n Workflow → OpenAI Translation → FastAPI /nlq → SQL Query → DuckDB → Results
     │              │              │              │           │         │
     │              │              │              │           │         ▼
     │              │              │              │           │    Query Execution
     │              │              │              │           │         │
     │              │              │              │           │         ▼
     │              │              │              │           │    Data Retrieval
     │              │              │              │           │         │
     │              │              │              │           │         ▼
     │              │              │              │           │    Response Formatting
     │              │              │              │           │         │
     ▼              ▼              ▼              ▼           ▼         ▼
Natural      Workflow      Structured    API        SQL        Database   Formatted
Language     Trigger       Parameters   Processing  Execution  Results    Response
```

## 🗄️ Database Schema

### Core Tables

#### 1. **raw_ads_spend**
```sql
CREATE TABLE raw_ads_spend (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('Meta', 'Google')),
    account VARCHAR(100) NOT NULL,
    campaign VARCHAR(100) NOT NULL,
    country VARCHAR(50) NOT NULL,
    device VARCHAR(50) NOT NULL,
    spend DECIMAL(10,2) NOT NULL,
    clicks INTEGER NOT NULL,
    impressions INTEGER NOT NULL,
    conversions INTEGER NOT NULL,
    load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    source_file_name VARCHAR(255),
    batch_id VARCHAR(100)
);
```

#### 2. **kpi_metrics**
```sql
CREATE TABLE kpi_metrics (
    id INTEGER PRIMARY KEY,
    date DATE NOT NULL,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('Meta', 'Google', 'ALL')),
    account VARCHAR(100),
    campaign VARCHAR(100),
    country VARCHAR(50),
    device VARCHAR(50),
    total_spend DECIMAL(10,2) NOT NULL,
    total_conversions INTEGER NOT NULL,
    cac DECIMAL(10,4),
    roas DECIMAL(10,4),
    revenue DECIMAL(10,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Views

#### Performance Indexes
```sql
-- Date range queries
CREATE INDEX idx_raw_ads_spend_date ON raw_ads_spend(date);
CREATE INDEX idx_kpi_metrics_date ON kpi_metrics(date);

-- Platform filtering
CREATE INDEX idx_raw_ads_spend_platform ON raw_ads_spend(platform);
CREATE INDEX idx_kpi_metrics_platform ON kpi_metrics(platform);

-- Batch tracking
CREATE INDEX idx_raw_ads_spend_batch ON raw_ads_spend(batch_id);
```

#### Analytical Views
```sql
-- Platform performance summary
CREATE VIEW platform_performance AS
SELECT 
    platform,
    SUM(total_spend) as total_spend,
    SUM(total_conversions) as total_conversions,
    AVG(cac) as avg_cac,
    AVG(roas) as avg_roas
FROM kpi_metrics
GROUP BY platform;

-- Daily trends
CREATE VIEW daily_trends AS
SELECT 
    date,
    SUM(total_spend) as daily_spend,
    SUM(total_conversions) as daily_conversions,
    AVG(cac) as daily_avg_cac
FROM kpi_metrics
GROUP BY date
ORDER BY date;
```

## 🔌 API Architecture

### RESTful Endpoints

#### Core Endpoints
- `GET /` - API information and health
- `GET /health` - System health check
- `POST /ingest` - Data ingestion endpoint
- `GET /metrics` - KPI metrics retrieval
- `POST /nlq` - Natural language query processing

#### Query Endpoints
- `GET /time-analysis` - Period-over-period analysis
- `GET /daily-trends` - Daily performance trends
- `GET /platform-metrics` - Platform-specific metrics

### Request/Response Patterns

#### Standard Response Format
```json
{
    "success": true,
    "data": [...],
    "timestamp": "2025-09-03T10:00:00Z",
    "row_count": 10,
    "execution_time": 0.045
}
```

#### Error Response Format
```json
{
    "success": false,
    "error": "Error description",
    "error_code": "ERROR_CODE",
    "timestamp": "2025-09-03T10:00:00Z"
}
```

## 🔄 Workflow Architecture

### n8n Workflow Structure

#### 1. **Data Ingestion Workflow**
```
Webhook Trigger → Read CSV → Validate Data → Call API → Success/Failure Notification
```

#### 2. **NLQ Translation Workflow**
```
Webhook Trigger → OpenAI Translation → Parse Response → Call API → Format Results
```

### Workflow Triggers

- **Manual**: User-initiated workflow execution
- **Scheduled**: Time-based automatic execution
- **Webhook**: API-triggered execution
- **Event-based**: System event-triggered execution

## 🚀 Performance Characteristics

### Response Times
- **Simple Queries**: < 100ms
- **Complex Analytics**: < 500ms
- **Data Ingestion**: < 2 seconds per 1000 records
- **KPI Computation**: < 1 second for platform-level aggregation

### Scalability Metrics
- **Concurrent Users**: 100+ simultaneous users
- **Data Volume**: 1M+ records per batch
- **Query Complexity**: Support for complex multi-dimensional queries
- **System Resources**: Efficient memory and CPU utilization

## 🔒 Security & Access Control

### Current Security Features
- **Input Validation**: All inputs validated through Pydantic models
- **SQL Injection Prevention**: Parameterized queries only
- **Error Handling**: Secure error messages without system exposure
- **Rate Limiting**: Built-in request throttling

### Future Security Enhancements
- **Authentication**: JWT-based user authentication
- **Authorization**: Role-based access control (RBAC)
- **API Keys**: Secure API key management
- **Audit Logging**: Complete user action tracking

## 📈 Monitoring & Observability

### Health Checks
- **API Health**: `/health` endpoint with database connectivity
- **Service Status**: Individual service health monitoring
- **Performance Metrics**: Response time and throughput tracking

### Logging Strategy
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Context Information**: Request IDs, user context, performance metrics

### Metrics Collection
- **Request Counts**: API endpoint usage statistics
- **Response Times**: Performance monitoring
- **Error Rates**: System reliability tracking
- **Resource Usage**: CPU, memory, and database performance

---

*This architecture provides a solid foundation for intelligent data processing while maintaining flexibility for future enhancements and scaling.*
