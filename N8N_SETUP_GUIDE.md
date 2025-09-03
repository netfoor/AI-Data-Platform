# n8n Integration Setup Guide

## Overview

This guide will help you set up the n8n integration for your AI Data Platform. The integration allows you to automate data ingestion workflows using your existing n8n.cloud account.

## Prerequisites

- ✅ n8n.cloud account at https://fortino200502rom.app.n8n.cloud
- ✅ Python virtual environment with dependencies installed
- ✅ DuckDB database initialized

## Step 1: Environment Configuration

Create a `.env` file in your project root with the following settings:

```bash
# n8n Integration Settings
N8N_BASE_URL=https://fortino200502rom.app.n8n.cloud
N8N_API_KEY=your_n8n_api_key_here
N8N_WEBHOOK_SECRET=your_webhook_secret_here
N8N_WORKFLOW_ID=your_workflow_id_here
N8N_ENABLE_AUTOMATION=true
N8N_RETRY_ATTEMPTS=3
N8N_RETRY_DELAY_SECONDS=60
```

## Step 2: Get n8n API Key

1. Go to https://fortino200502rom.app.n8n.cloud
2. Navigate to Settings → API Keys
3. Create a new API key with appropriate permissions
4. Copy the API key to your `.env` file

## Step 3: Create Data Ingestion Workflow

### 3.1 Create New Workflow

1. In n8n.cloud, click "New Workflow"
2. Name it "Data Ingestion - AI Platform"
3. Save the workflow

### 3.2 Add Workflow Nodes

#### Node 1: Manual Trigger
- Type: Manual Trigger
- Name: "Start Data Ingestion"
- Description: "Manual trigger for data ingestion process"

#### Node 2: CSV Reader
- Type: CSV File
- Name: "Read ads_spend.csv"
- Configuration:
  - File Path: `ads_spend.csv`
  - Delimiter: `,`
  - Has Header: `true`

#### Node 3: Data Transformation
- Type: Function
- Name: "Add Metadata"
- Code:
```javascript
// Add metadata to each record
const records = $input.all();
const transformedRecords = records.map(record => ({
  ...record.json,
  load_date: new Date().toISOString(),
  source_file_name: 'ads_spend.csv',
  batch_id: $('Start Data Ingestion').first().json.batch_id || Date.now().toString()
}));

return transformedRecords.map(record => ({ json: record }));
```

#### Node 4: HTTP Request (to Local ETL Pipeline)
- Type: HTTP Request
- Name: "Trigger ETL Pipeline"
- Configuration:
  - Method: `POST`
  - URL: `http://localhost:8000/api/ingest`
  - Headers: `Content-Type: application/json`
  - Body: 
```json
{
  "csv_file_path": "ads_spend.csv",
  "batch_id": "{{ $('Start Data Ingestion').first().json.batch_id }}"
}
```

#### Node 5: Success Notification
- Type: Email or Slack (your preference)
- Name: "Success Notification"
- Configure to send success message when ETL completes

#### Node 6: Error Handling
- Type: Error Trigger
- Name: "Error Handler"
- Connect to notification node for error alerts

### 3.3 Connect the Nodes

```
Manual Trigger → CSV Reader → Data Transformation → HTTP Request → Success Notification
                                    ↓
                              Error Handler → Error Notification
```

### 3.4 Save and Activate

1. Save the workflow
2. Click "Activate" to enable it
3. Copy the Workflow ID from the URL

## Step 4: Update Environment Configuration

Update your `.env` file with the actual workflow ID:

```bash
N8N_WORKFLOW_ID=your_actual_workflow_id_here
```

## Step 5: Test the Integration

### 5.1 Test Connection

```bash
python -m ai_data_platform n8n test
```

### 5.2 Test Workflow Setup

```bash
python -m ai_data_platform n8n setup
```

### 5.3 Test Data Ingestion

```bash
python -m ai_data_platform n8n ingest
```

## Step 6: Schedule Automation

### Option 1: n8n Scheduler
1. Add a "Cron" node to your workflow
2. Set it to run daily at your preferred time (e.g., 09:00)
3. Connect it to the Manual Trigger node

### Option 2: External Scheduler
Use your system's cron or Windows Task Scheduler to call:

```bash
python -m ai_data_platform n8n ingest
```

## Troubleshooting

### Common Issues

1. **Connection Failed**
   - Check your n8n.cloud URL
   - Verify API key permissions
   - Ensure n8n instance is running

2. **Workflow Not Found**
   - Verify workflow ID in `.env`
   - Check if workflow is activated
   - Ensure workflow name matches exactly

3. **ETL Pipeline Fails**
   - Check local ETL pipeline logs
   - Verify CSV file path
   - Check database connection

### Debug Commands

```bash
# Check platform status
python -m ai_data_platform info

# Check workflow status
python -m ai_data_platform n8n status

# Run ETL directly (bypass n8n)
python -m ai_data_platform data ingest
```

## Next Steps

After successful setup:

1. **Monitor Workflows**: Use `python -m ai_data_platform n8n status`
2. **View Logs**: Check `logs/ai_data_platform.log`
3. **Scale Up**: Add more data sources to the workflow
4. **Customize**: Modify transformation logic as needed

## Support

If you encounter issues:

1. Check the logs in `logs/ai_data_platform.log`
2. Verify n8n workflow configuration
3. Test individual components separately
4. Review the troubleshooting section above

---

**Note**: This integration provides a bridge between n8n.cloud and your local AI Data Platform. The n8n workflow handles orchestration and scheduling, while your Python code handles the actual data processing and storage.

