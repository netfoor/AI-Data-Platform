# AI Data Platform - Developer Guide

## 👨‍💻 Developer Overview

Welcome to the AI Data Platform development team! This guide provides everything you need to understand the codebase, contribute to the project, and maintain high code quality.

### What You'll Learn
- **Code Architecture**: Understanding the system structure
- **Development Workflow**: How to contribute effectively
- **Testing Strategy**: Comprehensive testing approach
- **Code Standards**: Quality and style guidelines
- **Deployment Process**: From development to production

---

## 🏗️ Code Architecture

### Project Structure
```
Figure-Agency/
├── ai_data_platform/          # Core platform code
│   ├── __init__.py
│   ├── analytics/             # Analytics and KPI engine
│   │   ├── kpi_engine.py     # KPI calculations
│   │   ├── sql_queries.py    # SQL query interface
│   │   ├── time_analysis.py  # Time-based analysis
│   │   └── nlq.py            # Natural language processing
│   ├── api/                   # FastAPI application
│   │   ├── rest_api.py       # Main API endpoints
│   │   ├── server.py         # Server configuration
│   │   └── n8n_client.py     # n8n integration
│   ├── database/              # Data persistence layer
│   │   ├── connection.py     # Database connection
│   │   ├── schema.py         # Database schema
│   │   └── init_db.py        # Database initialization
│   ├── ingestion/             # Data ingestion pipeline
│   │   ├── etl_pipeline.py   # ETL orchestration
│   │   ├── csv_reader.py     # CSV processing
│   │   └── transformations.py # Data transformations
│   ├── models/                # Data models and validation
│   │   ├── ads_spend.py      # Marketing data models
│   │   └── validation.py     # Data validation rules
│   └── utils/                 # Utility functions
│       └── logging.py        # Logging configuration
├── ui/                        # Streamlit user interface
│   └── app.py                # Main UI application
├── workflows/                 # n8n workflow definitions
├── tests/                     # Comprehensive test suite
├── docs/                      # Documentation
├── docker-compose.yml         # Service orchestration
├── Dockerfile.api            # API service container
├── Dockerfile.ui             # UI service container
└── requirements.txt           # Python dependencies
```

### Core Components

#### 1. **Analytics Layer** (`ai_data_platform/analytics/`)
- **KPI Engine**: Calculates marketing metrics (CAC, ROAS, Revenue)
- **SQL Interface**: Parameterized query execution
- **Time Analysis**: Period-over-period comparisons
- **NLQ Processor**: Natural language query translation

#### 2. **API Layer** (`ai_data_platform/api/`)
- **FastAPI Application**: RESTful API endpoints
- **Request Validation**: Pydantic models for data validation
- **Error Handling**: Comprehensive error management
- **n8n Integration**: Workflow automation client

#### 3. **Database Layer** (`ai_data_platform/database/`)
- **Connection Management**: DuckDB connection handling
- **Schema Management**: Table creation and maintenance
- **Data Migration**: Schema versioning and updates

#### 4. **Ingestion Layer** (`ai_data_platform/ingestion/`)
- **ETL Pipeline**: End-to-end data processing
- **Data Validation**: Quality checks and error handling
- **Batch Processing**: Efficient data loading

#### 5. **Models Layer** (`ai_data_platform/models/`)
- **Data Models**: Pydantic models for data validation
- **Business Logic**: Domain-specific validation rules
- **Type Safety**: Strong typing for data integrity

---

## 🔄 Development Workflow

### 1. **Environment Setup**

#### Prerequisites
```bash
# Python 3.11+
python --version

# Docker and Docker Compose
docker --version
docker compose version

# Git
git --version
```

#### Local Development Setup
```bash
# Clone repository
git clone <repository-url>
cd Figure-Agency

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-core.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

#### IDE Configuration
- **VS Code**: Install Python, Docker, and Git extensions
- **PyCharm**: Configure virtual environment and Docker
- **Vim/Emacs**: Configure Python language server

### 2. **Development Process**

#### Feature Development
1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Implement Feature**
   - Write code following coding standards
   - Add comprehensive tests
   - Update documentation

3. **Test Locally**
   ```bash
   # Run tests
   python run_tests.py all
   
   # Run specific test categories
   python -m pytest tests/test_kpi_calculations.py -v
   
   # Check code quality
   black --check .
   flake8 .
   mypy .
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and Create PR**
   ```bash
   git push origin feature/new-feature-name
   # Create Pull Request on GitHub/GitLab
   ```

#### Bug Fixes
1. **Create Bug Fix Branch**
   ```bash
   git checkout -b fix/bug-description
   ```

2. **Fix and Test**
   - Reproduce the bug
   - Implement fix
   - Add regression test
   - Verify fix works

3. **Commit and Push**
   ```bash
   git commit -m "fix: resolve bug description"
   git push origin fix/bug-description
   ```

### 3. **Code Review Process**

#### Pull Request Checklist
- [ ] **Code Quality**: Follows coding standards
- [ ] **Tests**: All tests pass, new tests added
- [ ] **Documentation**: Updated relevant docs
- [ ] **Performance**: No performance regressions
- [ ] **Security**: No security vulnerabilities
- [ ] **Testing**: Manually tested functionality

#### Review Guidelines
- **Be Constructive**: Provide helpful feedback
- **Focus on Code**: Review the code, not the person
- **Ask Questions**: Clarify unclear implementations
- **Suggest Improvements**: Offer better alternatives
- **Approve Promptly**: Don't block on minor issues

---

## 🧪 Testing Strategy

### Test Categories

#### 1. **Unit Tests** (`tests/test_kpi_calculations.py`)
- **Purpose**: Test individual functions and methods
- **Coverage**: Business logic, edge cases, error handling
- **Execution**: Fast, isolated, no external dependencies

```python
def test_cac_calculation_basic(self):
    """Test basic CAC calculation"""
    spend = Decimal('100.00')
    conversions = 5
    
    cac = self.kpi_engine.calculate_cac(spend, conversions)
    expected = Decimal('20.00')
    
    assert cac == expected
    assert isinstance(cac, Decimal)
```

#### 2. **Integration Tests** (`tests/test_database_integration.py`)
- **Purpose**: Test component interactions
- **Coverage**: Database operations, API integrations
- **Execution**: Medium speed, requires test database

```python
def test_data_insertion_and_retrieval(self):
    """Test data insertion and retrieval"""
    # Insert test data
    test_data = [
        ('2025-06-01', 'Meta', 'TestAccount', 'TestCampaign', 'US', 'Mobile', 100.00, 50, 1000, 5)
    ]
    
    # Verify insertion
    count_query = "SELECT COUNT(*) FROM raw_ads_spend"
    result = self.db.execute_query(count_query)
    count = result.fetchone()[0]
    assert count == 1
```

#### 3. **API Tests** (`tests/test_api_endpoints.py`)
- **Purpose**: Test HTTP endpoints and responses
- **Coverage**: Request/response handling, error cases
- **Execution**: Fast, uses FastAPI TestClient

```python
def test_metrics_endpoint_with_dates(self):
    """Test metrics endpoint with date parameters"""
    response = self.client.get("/metrics?start_date=2025-06-01&end_date=2025-06-30")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
```

#### 4. **End-to-End Tests** (`tests/test_e2e_pipeline.py`)
- **Purpose**: Test complete data flow
- **Coverage**: Full pipeline from CSV to insights
- **Execution**: Slower, requires full system setup

```python
def test_complete_etl_pipeline(self):
    """Test complete ETL pipeline execution"""
    result = run_etl_pipeline(
        csv_file_path=str(self.test_csv),
        batch_id="test_e2e_batch"
    )
    
    assert result.success is True
    assert result.total_records_read == 12
    assert result.records_inserted == 12
```

### Running Tests

#### Test Runner Script
```bash
# Run all tests
python run_tests.py all

# Run specific test categories
python run_tests.py unit
python run_tests.py integration
python run_tests.py api
python run_tests.py e2e

# Run with verbose output
python run_tests.py all -v
```

#### Direct Pytest Commands
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_kpi_calculations.py

# Run specific test method
python -m pytest tests/test_kpi_calculations.py::TestKPICalculations::test_cac_calculation_basic

# Run with coverage
python -m pytest --cov=ai_data_platform --cov-report=html

# Run with markers
python -m pytest -m "unit"
python -m pytest -m "integration"
python -m pytest -m "api"
python -m pytest -m "e2e"
```

### Test Configuration

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --color=yes
markers =
    unit: Unit tests
    integration: Integration tests
    api: API endpoint tests
    e2e: End-to-end pipeline tests
    slow: Slow running tests
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
```

---

## 📝 Coding Standards

### Python Style Guide

#### Code Formatting
- **Black**: Automatic code formatting
- **Line Length**: 88 characters (Black default)
- **Indentation**: 4 spaces (no tabs)

```python
# Good formatting
def calculate_kpi_metrics(
    start_date: date,
    end_date: date,
    platform: Optional[str] = None,
    dimensions: List[str] = None,
) -> List[Dict[str, Any]]:
    """Calculate KPI metrics for specified parameters."""
    if dimensions is None:
        dimensions = ["platform"]
    
    # Implementation here
    pass
```

#### Type Hints
- **Use Type Hints**: All function parameters and return values
- **Import Types**: Use proper type imports
- **Generic Types**: Use for collections and complex types

```python
from typing import List, Dict, Any, Optional, Union
from datetime import date, datetime
from decimal import Decimal

def process_marketing_data(
    data: List[Dict[str, Any]],
    date_range: tuple[date, date],
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Union[int, float, str]]:
    """Process marketing data with type safety."""
    pass
```

#### Documentation
- **Docstrings**: Use Google-style docstrings
- **Inline Comments**: Explain complex logic
- **README Files**: Keep documentation updated

```python
def calculate_cac(spend: Decimal, conversions: int) -> Optional[Decimal]:
    """
    Calculate Customer Acquisition Cost (CAC).
    
    Args:
        spend: Total advertising spend amount
        conversions: Number of conversions achieved
        
    Returns:
        CAC value (spend per conversion) or None if invalid
        
    Raises:
        ValueError: If spend or conversions are negative
        
    Example:
        >>> calculate_cac(Decimal('100.00'), 5)
        Decimal('20.00')
    """
    if spend < 0 or conversions < 0:
        raise ValueError("Spend and conversions must be non-negative")
    
    if conversions == 0:
        return None
    
    return spend / conversions
```

### Error Handling

#### Exception Types
- **Custom Exceptions**: Create domain-specific exceptions
- **Proper Hierarchy**: Inherit from appropriate base classes
- **Meaningful Messages**: Provide helpful error information

```python
class DataValidationError(Exception):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: str, value: Any):
        self.message = message
        self.field = field
        self.value = value
        super().__init__(f"{message}: {field}={value}")


class DatabaseConnectionError(Exception):
    """Raised when database connection fails."""
    pass


class WorkflowExecutionError(Exception):
    """Raised when workflow execution fails."""
    pass
```

#### Error Handling Patterns
```python
def process_data_file(file_path: str) -> ProcessingResult:
    """Process data file with comprehensive error handling."""
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Read and validate data
        data = read_csv_file(file_path)
        validated_data = validate_data(data)
        
        # Process data
        result = process_validated_data(validated_data)
        return ProcessingResult(success=True, data=result)
        
    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        return ProcessingResult(success=False, error=str(e))
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return ProcessingResult(success=False, error=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ProcessingResult(success=False, error="Internal processing error")
```

### Logging

#### Logging Configuration
```python
import logging
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[Path] = None,
) -> None:
    """Configure logging for the application."""
    # Set log level
    level = getattr(logging, log_level.upper())
    
    # Configure format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # File handler (if specified)
    handlers = [console_handler]
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        handlers=handlers,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
```

#### Logging Usage
```python
import logging

logger = logging.getLogger(__name__)

def process_batch(batch_id: str, data: List[Dict]) -> bool:
    """Process a batch of data with detailed logging."""
    logger.info(f"Starting batch processing: {batch_id}")
    logger.debug(f"Batch contains {len(data)} records")
    
    try:
        # Process data
        processed_count = 0
        for record in data:
            if process_record(record):
                processed_count += 1
            else:
                logger.warning(f"Failed to process record: {record.get('id')}")
        
        logger.info(f"Batch {batch_id} completed: {processed_count}/{len(data)} records processed")
        return True
        
    except Exception as e:
        logger.error(f"Batch {batch_id} failed: {e}", exc_info=True)
        return False
```

---

## 🚀 Performance Optimization

### Database Optimization

#### Indexing Strategy
```python
def create_performance_indexes(self) -> None:
    """Create indexes for optimal query performance."""
    indexes = [
        "CREATE INDEX idx_raw_ads_spend_date ON raw_ads_spend(date)",
        "CREATE INDEX idx_raw_ads_spend_platform ON raw_ads_spend(platform)",
        "CREATE INDEX idx_raw_ads_spend_batch ON raw_ads_spend(batch_id)",
        "CREATE INDEX idx_kpi_metrics_date ON kpi_metrics(date)",
        "CREATE INDEX idx_kpi_metrics_platform ON kpi_metrics(platform)",
    ]
    
    for index_sql in indexes:
        try:
            self.db.execute_query(index_sql)
            logger.info(f"Created index: {index_sql}")
        except Exception as e:
            logger.warning(f"Failed to create index: {e}")
```

#### Query Optimization
```python
def get_platform_performance(
    self,
    start_date: date,
    end_date: date,
    platform: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get platform performance with optimized query."""
    # Build efficient query with proper filtering
    query = """
    SELECT 
        platform,
        SUM(total_spend) as total_spend,
        SUM(total_conversions) as total_conversions,
        AVG(cac) as avg_cac,
        AVG(roas) as avg_roas
    FROM kpi_metrics
    WHERE date BETWEEN ? AND ?
    """
    
    params = [start_date, end_date]
    
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    
    query += " GROUP BY platform ORDER BY total_spend DESC"
    
    return self.db.execute_query(query, params).fetchall()
```

### Memory Management

#### Efficient Data Processing
```python
def process_large_dataset(file_path: str, batch_size: int = 1000) -> None:
    """Process large datasets in memory-efficient batches."""
    with open(file_path, 'r') as file:
        # Skip header
        next(file)
        
        batch = []
        for line in file:
            batch.append(parse_line(line))
            
            if len(batch) >= batch_size:
                process_batch(batch)
                batch = []
        
        # Process remaining records
        if batch:
            process_batch(batch)
```

#### Generator Functions
```python
def read_csv_generator(file_path: str):
    """Read CSV file as generator to save memory."""
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            yield row
```

---

## 🔒 Security Considerations

### Input Validation

#### Data Sanitization
```python
from pydantic import BaseModel, validator
import re

class DataIngestionRequest(BaseModel):
    csv_file_path: str
    batch_id: Optional[str] = None
    
    @validator('csv_file_path')
    def validate_file_path(cls, v):
        """Validate file path for security."""
        # Prevent path traversal attacks
        if '..' in v or v.startswith('/'):
            raise ValueError("Invalid file path")
        
        # Only allow CSV files
        if not v.endswith('.csv'):
            raise ValueError("Only CSV files are allowed")
        
        return v
    
    @validator('batch_id')
    def validate_batch_id(cls, v):
        """Validate batch ID format."""
        if v and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError("Batch ID contains invalid characters")
        return v
```

#### SQL Injection Prevention
```python
def execute_safe_query(self, query: str, params: List[Any]) -> Any:
    """Execute query with parameterized statements."""
    try:
        # Always use parameterized queries
        result = self.db.execute_query(query, params)
        return result
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise DatabaseError(f"Query failed: {e}")
```

### API Security

#### Rate Limiting
```python
from fastapi import FastAPI, Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/ingest")
@limiter.limit("10/minute")
async def ingest_data(request: Request):
    """Rate-limited data ingestion endpoint."""
    # Implementation here
    pass
```

#### CORS Configuration
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",  # Streamlit UI
        "http://localhost:5678",  # n8n workflows
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

---

## 📦 Deployment Process

### Development Deployment

#### Local Docker Setup
```bash
# Build and start services
docker compose up -d --build

# Check service status
docker compose ps

# View logs
docker compose logs -f api
```

#### Development Mode
```bash
# Run API in development mode
cd ai_data_platform
uvicorn api.rest_api:app --reload --host 0.0.0.0 --port 8000

# Run UI in development mode
cd ui
streamlit run app.py --server.port 8501
```

### Production Deployment

#### Environment Configuration
```bash
# Production environment variables
export ENVIRONMENT=production
export LOG_LEVEL=WARNING
export DATABASE_PATH=/data/ai_data_platform.duckdb
export API_HOST=0.0.0.0
export API_PORT=8000
```

#### Production Docker Compose
```yaml
version: '3.8'
services:
  api:
    build: .
    dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

#### Monitoring and Logging
```python
# Production logging configuration
import logging
from logging.handlers import RotatingFileHandler

def setup_production_logging():
    """Configure production logging with rotation."""
    handler = RotatingFileHandler(
        'logs/ai_data_platform.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.WARNING)
```

---

## 🤝 Contributing Guidelines

### Contribution Process

#### 1. **Fork and Clone**
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/yourusername/Figure-Agency.git
cd Figure-Agency

# Add upstream remote
git remote add upstream https://github.com/original/Figure-Agency.git
```

#### 2. **Create Feature Branch**
```bash
git checkout -b feature/your-feature-name
```

#### 3. **Make Changes**
- Follow coding standards
- Write comprehensive tests
- Update documentation
- Keep commits atomic and meaningful

#### 4. **Test Your Changes**
```bash
# Run all tests
python run_tests.py all

# Check code quality
black --check .
flake8 .
mypy .
```

#### 5. **Commit and Push**
```bash
git add .
git commit -m "feat: add your feature description"
git push origin feature/your-feature-name
```

#### 6. **Create Pull Request**
- Provide clear description of changes
- Include test results
- Reference related issues
- Request review from maintainers

### Code Review Guidelines

#### For Contributors
- **Respond Promptly**: Address review comments quickly
- **Be Open to Feedback**: Consider suggestions constructively
- **Test Thoroughly**: Ensure all tests pass
- **Document Changes**: Update relevant documentation

#### For Reviewers
- **Be Constructive**: Provide helpful, specific feedback
- **Focus on Code**: Review the implementation, not the person
- **Ask Questions**: Clarify unclear implementations
- **Approve Promptly**: Don't block on minor issues

### Issue Reporting

#### Bug Reports
- **Clear Description**: Explain what happened vs. expected
- **Reproduction Steps**: Provide step-by-step instructions
- **Environment Details**: Include system and version information
- **Error Messages**: Copy complete error text and logs

#### Feature Requests
- **Problem Statement**: Explain the problem you're solving
- **Proposed Solution**: Describe your suggested approach
- **Use Cases**: Provide examples of how it would be used
- **Priority**: Indicate importance and urgency

---

## 📚 Additional Resources

### Documentation
- **API Reference**: [docs/api-reference.md](api-reference.md)
- **User Guide**: [docs/user-guide.md](user-guide.md)
- **System Architecture**: [docs/system-architecture.md](system-architecture.md)

### External Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Streamlit Documentation**: https://docs.streamlit.io/
- **n8n Documentation**: https://docs.n8n.io/
- **DuckDB Documentation**: https://duckdb.org/docs/

### Community
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share ideas
- **Contributions**: Submit pull requests and improvements

---

*This developer guide provides comprehensive information for contributing to the AI Data Platform. For questions or clarifications, please open an issue or start a discussion on GitHub.*
