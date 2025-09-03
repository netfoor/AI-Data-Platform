# AI Data Platform - Testing Guide

## Overview

This document describes the comprehensive testing suite for the AI Data Platform, covering Task 10 requirements for testing all system components.

## Test Categories

### 1. Unit Tests (`test_kpi_calculations.py`)
**Purpose**: Test individual KPI calculation functions in isolation
**Coverage**:
- CAC calculation with edge cases (division by zero, negative values)
- ROAS calculation with edge cases
- Revenue calculation
- Complete KPI computation for single records
- Decimal precision and rounding

**Markers**: `@pytest.mark.unit`

### 2. Integration Tests (`test_database_integration.py`)
**Purpose**: Test database operations and data persistence
**Coverage**:
- Database schema creation and validation
- Data insertion and retrieval
- KPI metrics storage and retrieval
- Complete KPI computation and storage workflow
- Data integrity validation

**Markers**: `@pytest.mark.integration`

### 3. API Tests (`test_api_endpoints.py`)
**Purpose**: Test REST API endpoint functionality
**Coverage**:
- All API endpoints (`/`, `/health`, `/metrics`, `/time-analysis`, `/daily-trends`, `/platform-metrics`, `/ingest`, `/nlq`)
- Request validation and error handling
- Response formatting and status codes
- Edge cases and malformed requests

**Markers**: `@pytest.mark.api`

### 4. End-to-End Tests (`test_e2e_pipeline.py`)
**Purpose**: Test complete data flow from ingestion to analysis
**Coverage**:
- Complete ETL pipeline execution
- Data persistence after ETL
- KPI computation after data ingestion
- SQL query interface functionality
- Period comparison analysis
- Data quality validation
- Pipeline performance characteristics

**Markers**: `@pytest.mark.e2e`

## Running Tests

### Prerequisites

1. **Activate Virtual Environment**:
   ```bash
   .\venv\Scripts\activate
   ```

2. **Install Testing Dependencies**:
   ```bash
   pip install pytest pytest-cov httpx fastapi[testing]
   ```

### Test Runner Script

Use the comprehensive test runner for easy execution:

```bash
# Run all tests
python run_tests.py all

# Run specific test categories
python run_tests.py unit
python run_tests.py integration
python run_tests.py api
python run_tests.py e2e

# Verbose output
python run_tests.py all -v

# Install dependencies and run tests
python run_tests.py all --install-deps
```

### Direct Pytest Commands

```bash
# Run all tests
pytest

# Run specific test files
pytest tests/test_kpi_calculations.py
pytest tests/test_database_integration.py
pytest tests/test_api_endpoints.py
pytest tests/test_e2e_pipeline.py

# Run by markers
pytest -m unit
pytest -m integration
pytest -m api
pytest -m e2e

# Verbose output
pytest -v

# Generate coverage report
pytest --cov=ai_data_platform --cov-report=html
```

## Test Configuration

### pytest.ini
- Test discovery patterns
- Markers for test categorization
- Output formatting options
- Warning filters

### Test Environment
- **Temporary Databases**: Each test uses isolated DuckDB instances
- **Test Data**: Synthetic CSV files with known values
- **Cleanup**: Automatic cleanup of test artifacts
- **Isolation**: Tests don't interfere with each other

## Test Data

### Sample CSV Structure
```csv
date,platform,account,campaign,country,device,spend,clicks,impressions,conversions
2025-06-01,Facebook,TestAccount,TestCampaign,US,Mobile,100.00,50,1000,5
2025-06-01,Google,TestAccount,TestCampaign,US,Desktop,150.00,75,1500,8
```

### Test Scenarios
- **Valid Data**: Normal operation testing
- **Edge Cases**: Zero values, negative values, missing data
- **Performance**: Multiple pipeline executions
- **Error Handling**: Invalid inputs, file errors, database issues

## Expected Test Results

### Unit Tests
- ✅ CAC calculation accuracy
- ✅ ROAS calculation accuracy
- ✅ Edge case handling
- ✅ Decimal precision

### Integration Tests
- ✅ Database schema validation
- ✅ Data persistence
- ✅ KPI storage and retrieval
- ✅ Workflow integration

### API Tests
- ✅ Endpoint functionality
- ✅ Request validation
- ✅ Error handling
- ✅ Response formatting

### End-to-End Tests
- ✅ Complete pipeline execution
- ✅ Data flow validation
- ✅ KPI computation accuracy
- ✅ Performance characteristics

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure virtual environment is activated
   - Check that all dependencies are installed
   - Verify PYTHONPATH includes project root

2. **Database Connection Issues**:
   - Tests use temporary databases, no external dependencies
   - Check DuckDB installation
   - Verify file permissions for temporary files

3. **Test Failures**:
   - Check test output for specific error messages
   - Verify test data files exist
   - Check database schema initialization

### Debug Mode

Run tests with verbose output for detailed debugging:

```bash
python run_tests.py all -v
```

## Coverage Goals

- **Unit Tests**: 90%+ coverage of KPI calculation functions
- **Integration Tests**: 85%+ coverage of database operations
- **API Tests**: 95%+ coverage of endpoint functionality
- **End-to-End Tests**: 80%+ coverage of complete workflows

## Continuous Integration

### GitHub Actions (Recommended)
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: python run_tests.py all
```

### Local Development
```bash
# Pre-commit hook (optional)
pip install pre-commit
pre-commit install

# Run tests before committing
python run_tests.py all
```

## Performance Testing

### Pipeline Performance
- **ETL Pipeline**: Should complete in <60 seconds for 12 records
- **KPI Computation**: Should complete in <30 seconds for platform-level aggregation
- **API Response**: Should respond in <5 seconds for all endpoints

### Load Testing (Future)
- Multiple concurrent ETL pipelines
- High-volume data ingestion
- API endpoint stress testing

## Security Testing

### Input Validation
- SQL injection prevention
- File path validation
- Request payload validation

### Authentication (Future)
- API key validation
- Webhook secret verification
- Rate limiting

## Reporting

### Test Results
- Pass/Fail status for each test category
- Execution duration
- Detailed error messages
- Coverage reports

### Quality Metrics
- Test coverage percentage
- Pass rate
- Performance benchmarks
- Error frequency

## Next Steps

After completing Task 10 (Testing), proceed to:
- **Task 11**: Documentation and deployment artifacts
- **Task 12**: Final integration and validation

## Support

For testing issues or questions:
1. Check this guide first
2. Review test output and error messages
3. Verify test environment setup
4. Check test data and configuration files
