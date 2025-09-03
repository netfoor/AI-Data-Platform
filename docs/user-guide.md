# AI Data Platform - User Guide

## 🚀 Getting Started

Welcome to the AI Data Platform! This guide will walk you through using all the platform's features, from data ingestion to natural language queries.

### What You'll Learn
- How to set up and access the platform
- How to ingest marketing data
- How to run automated workflows
- How to ask questions in plain English
- How to view and analyze results
- How to troubleshoot common issues

## 🏠 Platform Access

### Web Interface
- **Main Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8001/docs
- **n8n Workflows**: http://localhost:5678

### System Status Check
Before using the platform, verify all services are running:
```bash
# Check if services are running
docker ps

# Expected services:
# - ai-platform-api (port 8001)
# - ai-platform-ui (port 8501)  
# - n8n (port 5678)
```

## 📊 Data Ingestion Workflow

### Step 1: Prepare Your Data

Your CSV file should have this structure:
```csv
date,platform,account,campaign,country,device,spend,clicks,impressions,conversions
2025-06-01,Meta,CompanyA,SummerSale,US,Mobile,100.50,50,1000,5
2025-06-01,Google,CompanyA,SummerSale,US,Desktop,150.00,75,1500,8
```

**Important**: Use `Meta` (not Facebook) and `Google` as platform values.

### Step 2: Upload Data via Web Interface

1. **Open the Dashboard**: Navigate to http://localhost:8501
2. **Click "Data Ingestion"** in the sidebar
3. **Enter CSV Path**: Use `data/ads_spend.csv` (or your file path)
4. **Click "Ingest Data"**
5. **Monitor Progress**: Watch the real-time ingestion status

### Step 3: Verify Data Processing

Check the results:
- ✅ **Success**: Data processed and stored
- ⚠️ **Partial Success**: Some records failed (check logs)
- ❌ **Failed**: Processing failed (check error messages)

### Alternative: Direct API Call

```bash
curl -X POST "http://localhost:8001/ingest" \
  -H "Content-Type: application/json" \
  -d '{"csv_file_path": "data/ads_spend.csv"}'
```

## 🔄 Automated Workflow Execution

### Understanding n8n Workflows

The platform uses n8n for workflow automation. Here's how it works:

#### 1. **Data Ingestion Workflow**
- **Trigger**: Manual execution or scheduled runs
- **Process**: Reads CSV → Validates → Calls API → Notifies
- **Output**: Success/failure notification with details

#### 2. **NLQ Translation Workflow**
- **Trigger**: User submits natural language question
- **Process**: AI translation → Parameter extraction → API call → Results
- **Output**: Structured data response

### Running Workflows Manually

1. **Access n8n**: Go to http://localhost:5678
2. **Select Workflow**: Choose from available workflows
3. **Click "Execute"**: Run the workflow manually
4. **Monitor Execution**: Watch real-time progress
5. **Check Results**: View success/failure status

### Workflow Automation

#### Schedule Regular Data Ingestion
1. In n8n, set workflow to run daily at 9:00 AM
2. Configure to read from your data source
3. Set up email notifications for success/failure
4. Enable automatic retry on failure

#### Trigger on File Upload
1. Set up file watcher in n8n
2. Configure to monitor your data directory
3. Automatically trigger ingestion when new files arrive
4. Send Slack/email notifications

## 🗣️ Natural Language Queries

### How It Works

The platform translates your questions into SQL queries automatically:

1. **You Ask**: "Show me Facebook performance last month"
2. **AI Translates**: Converts to structured parameters
3. **System Executes**: Runs optimized SQL query
4. **Results Return**: Formatted data with insights

### Example Questions

#### Basic Queries
- "Show me daily metrics"
- "What's our total spend this month?"
- "How many conversions did we get?"

#### Advanced Queries
- "Compare CAC and ROAS last 30 days vs prior 30 days"
- "Show platform performance by country"
- "What's our best performing campaign?"

#### Date-Based Queries
- "Last week's performance"
- "This month vs last month"
- "Q2 vs Q1 comparison"

### Using the NLQ Interface

#### Web Interface
1. **Go to "Natural Language Queries"** in the sidebar
2. **Type your question** in the text box
3. **Add date parameters** if needed
4. **Click "Ask Question"**
5. **View results** in the response area

#### API Direct Access
```bash
curl -X POST "http://localhost:8001/nlq" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Show me Meta performance last month",
    "start_date": "2025-08-01",
    "end_date": "2025-08-31"
  }'
```

### Understanding Results

#### Success Response
```json
{
  "success": true,
  "query_name": "platform_performance",
  "data": [
    {
      "platform": "Meta",
      "total_spend": 1500.00,
      "total_conversions": 75,
      "cac": 20.00,
      "roas": 5.00
    }
  ],
  "row_count": 1,
  "execution_time": 0.045
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Unable to process question. Please rephrase.",
  "query_name": "unknown",
  "suggestions": [
    "Try: 'Show me daily metrics'",
    "Try: 'What's our total spend?'"
  ]
}
```

## 📈 Viewing Analytics & Results

### Dashboard Overview

The main dashboard provides:
- **Real-time Metrics**: Current KPI values
- **Performance Trends**: Visual charts and graphs
- **Quick Actions**: Common tasks and queries
- **System Status**: Service health and availability

### KPI Metrics

#### Key Performance Indicators
- **CAC (Customer Acquisition Cost)**: Cost per conversion
- **ROAS (Return on Ad Spend)**: Revenue per dollar spent
- **Revenue**: Total revenue generated
- **Conversion Rate**: Percentage of clicks that convert

#### Viewing Metrics
1. **Go to "KPI Dashboard"** in the sidebar
2. **Select date range** for analysis
3. **Choose dimensions** (platform, country, device)
4. **View results** in tables and charts

### Time Analysis

#### Period Comparisons
1. **Navigate to "Time Analysis"**
2. **Set current period** (e.g., last 30 days)
3. **Set comparison period** (e.g., prior 30 days)
4. **View changes** in spend, conversions, and KPIs

#### Trend Analysis
- **Daily Trends**: Performance over time
- **Weekly Patterns**: Day-of-week analysis
- **Monthly Growth**: Month-over-month comparison

### Platform Performance

#### Platform Comparison
1. **Go to "Platform Metrics"**
2. **Select date range**
3. **Compare Meta vs Google** performance
4. **Analyze** spend, conversions, and efficiency

#### Campaign Analysis
- **Campaign Performance**: Best and worst campaigns
- **Account Analysis**: Performance by account
- **Geographic Insights**: Country and device performance

## 🔧 Troubleshooting Common Issues

### Service Not Accessible

#### Problem: Can't access web interface
**Solution**:
```bash
# Check if services are running
docker ps

# Restart services if needed
docker compose restart

# Check logs for errors
docker compose logs ui
```

#### Problem: API endpoints not responding
**Solution**:
```bash
# Test API health
curl http://localhost:8001/health

# Check API logs
docker compose logs api

# Verify database connection
docker compose logs api | grep "database"
```

### Data Ingestion Issues

#### Problem: CSV validation errors
**Common Causes**:
- Wrong platform names (use `Meta`, not `Facebook`)
- Missing required columns
- Invalid data types (spend must be numeric)

**Solution**:
1. Check CSV format matches requirements
2. Validate platform names are correct
3. Ensure all required columns exist
4. Check data types are valid

#### Problem: Database connection errors
**Solution**:
```bash
# Check database service
docker compose logs api | grep "duckdb"

# Verify database file exists
ls -la data/ai_data_platform.duckdb

# Restart database service
docker compose restart api
```

### Workflow Execution Issues

#### Problem: n8n workflows not running
**Solution**:
1. Check n8n service status
2. Verify workflow configuration
3. Check webhook URLs are correct
4. Review workflow logs for errors

#### Problem: OpenAI translation failing
**Solution**:
1. Verify OpenAI API key is configured
2. Check API quota and limits
3. Ensure internet connectivity
4. Review error logs for specific issues

### Performance Issues

#### Problem: Slow query responses
**Solutions**:
1. **Check database size**: Large datasets may need optimization
2. **Verify indexes**: Ensure database indexes are created
3. **Monitor resources**: Check CPU and memory usage
4. **Optimize queries**: Use specific date ranges when possible

#### Problem: High memory usage
**Solutions**:
1. **Restart services**: Clear memory cache
2. **Check for memory leaks**: Review application logs
3. **Optimize data processing**: Process data in smaller batches
4. **Monitor resource usage**: Use `docker stats` to track

## 📱 Advanced Usage

### Batch Processing

#### Multiple File Ingestion
1. **Prepare multiple CSV files**
2. **Use batch processing workflow**
3. **Monitor progress** across all files
4. **Review results** for each batch

#### Automated Scheduling
1. **Set up cron jobs** in n8n
2. **Configure file watchers** for new data
3. **Set up notifications** for completion
4. **Enable error handling** and retries

### Data Export

#### Exporting Results
1. **Query data** using NLQ or direct API calls
2. **Download results** as CSV or JSON
3. **Use for reporting** in other tools
4. **Schedule regular exports** for stakeholders

#### Integration with Other Tools
- **Excel**: Import CSV exports for analysis
- **Tableau**: Connect via API for live dashboards
- **Slack**: Receive notifications and alerts
- **Email**: Automated reports and summaries

### Custom Workflows

#### Building New Workflows
1. **Identify automation opportunity**
2. **Design workflow** in n8n
3. **Test workflow** with sample data
4. **Deploy and monitor** execution

#### Workflow Examples
- **Data Quality Checks**: Validate incoming data
- **Performance Alerts**: Notify when KPIs drop
- **Report Generation**: Create automated reports
- **Data Synchronization**: Sync with external systems

## 📞 Getting Help

### Documentation Resources
- **This User Guide**: Complete usage instructions
- **API Reference**: Technical endpoint documentation
- **System Architecture**: Understanding how it works
- **Troubleshooting**: Common issues and solutions

### Support Channels
- **Logs**: Check service logs for detailed error information
- **Health Checks**: Use `/health` endpoint to verify system status
- **Documentation**: Review relevant documentation sections
- **Community**: Join our support community for help

### Reporting Issues
When reporting problems, include:
1. **Description**: What you were trying to do
2. **Steps**: Exact steps to reproduce
3. **Error Messages**: Copy of any error text
4. **System Info**: Service versions and configuration
5. **Logs**: Relevant log entries

---

*This user guide covers all the essential features of the AI Data Platform. For advanced usage or technical details, refer to the Developer Guide and API Reference.*
