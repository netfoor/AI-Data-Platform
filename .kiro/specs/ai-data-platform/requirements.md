# Requirements Document

## Introduction

This feature implements a comprehensive AI Data Engineer Platform that demonstrates best practices for data ingestion, modeling, and metrics accessibility. The platform will orchestrate data ingestion using n8n, store data in DuckDB, compute marketing KPIs (CAC and ROAS), and provide analyst access through APIs or parameterized queries. The system emphasizes data provenance, automation, and natural language query capabilities.

## Requirements

### Requirement 1

**User Story:** As a data engineer, I want to set up automated data ingestion infrastructure, so that I can reliably ingest advertising spend data with proper metadata tracking.

#### Acceptance Criteria

1. WHEN the system is initialized THEN it SHALL create an n8n MCP server configuration
2. WHEN the system is initialized THEN it SHALL create a DuckDB database instance
3. WHEN the system is initialized THEN it SHALL create n8n documentation MCP server
4. WHEN data ingestion runs THEN the system SHALL include load_date metadata for provenance
5. WHEN data ingestion runs THEN the system SHALL include source_file_name metadata for tracking
6. WHEN the database is refreshed THEN the ingested data SHALL persist

### Requirement 2

**User Story:** As a data engineer, I want to orchestrate data ingestion using n8n workflows, so that I can automate the ETL process for advertising spend data.

#### Acceptance Criteria

1. WHEN n8n workflow executes THEN it SHALL read ads_spend.csv with columns: date, platform, account, campaign, country, device, spend, clicks, impressions, conversions
2. WHEN n8n workflow processes data THEN it SHALL transform data into warehouse-ready format
3. WHEN n8n workflow loads data THEN it SHALL insert records into DuckDB warehouse table
4. WHEN n8n workflow completes THEN it SHALL log successful ingestion with metadata
5. WHEN n8n workflow fails THEN it SHALL provide clear error messages and retry logic

### Requirement 3

**User Story:** As a data analyst, I want computed marketing KPIs available as SQL models, so that I can analyze campaign performance metrics.

#### Acceptance Criteria

1. WHEN KPI computation runs THEN it SHALL calculate CAC as spend / conversions
2. WHEN KPI computation runs THEN it SHALL calculate ROAS as (revenue / spend) where revenue = conversions × 100
3. WHEN KPI models execute THEN they SHALL handle division by zero cases gracefully
4. WHEN KPI models execute THEN they SHALL aggregate data by relevant dimensions (platform, campaign, country, device)
5. WHEN KPI models execute THEN they SHALL store results in accessible format

### Requirement 4

**User Story:** As a data analyst, I want to compare performance metrics across time periods, so that I can identify trends and performance changes.

#### Acceptance Criteria

1. WHEN analysis query runs THEN it SHALL compare last 30 days vs prior 30 days
2. WHEN analysis query runs THEN it SHALL show absolute values for both periods
3. WHEN analysis query runs THEN it SHALL calculate percentage change deltas
4. WHEN analysis query runs THEN it SHALL present results in compact table format
5. WHEN analysis query runs THEN it SHALL handle cases where prior period has no data

### Requirement 5

**User Story:** As a business user, I want accessible metrics through APIs or parameterized queries, so that I can retrieve performance data programmatically.

#### Acceptance Criteria

1. WHEN metrics access is requested THEN the system SHALL provide either SQL script with date range parameters OR API endpoint
2. IF API endpoint is implemented THEN it SHALL accept start and end date parameters
3. IF API endpoint is implemented THEN it SHALL return metrics in JSON format
4. WHEN parameterized query is used THEN it SHALL accept date range inputs
5. WHEN metrics are retrieved THEN they SHALL include CAC and ROAS for specified periods

### Requirement 6

**User Story:** As a business user, I want natural language query capabilities, so that I can ask questions about data without writing SQL.

#### Acceptance Criteria

1. WHEN natural language question is asked THEN the system SHALL map it to appropriate SQL query
2. WHEN question like "Compare CAC and ROAS for last 30 days vs prior 30 days" is asked THEN it SHALL execute comparison analysis
3. WHEN natural language processing occurs THEN it SHALL provide clear answer format
4. WHEN natural language query fails THEN it SHALL provide helpful error messages
5. WHEN natural language results are returned THEN they SHALL be in human-readable format

### Requirement 7

**User Story:** As a developer, I want comprehensive documentation and setup instructions, so that I can deploy and maintain the system.

#### Acceptance Criteria

1. WHEN documentation is created THEN it SHALL include n8n workflow export JSON
2. WHEN documentation is created THEN it SHALL include GitHub repository with public access
3. WHEN documentation is created THEN it SHALL include README with setup instructions
4. WHEN documentation is created THEN it SHALL include results documentation with best practices
5. WHEN documentation is created THEN it SHALL include n8n access details (URL + credentials or workflow JSON)