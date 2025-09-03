# AI Data Platform - Workflow Guide

## 🔄 Understanding n8n Workflows

n8n is the workflow automation engine that powers the AI Data Platform. It handles data ingestion, natural language query processing, and automated data processing workflows.

### What is n8n?
- **Open-source workflow automation** platform
- **Visual workflow builder** with drag-and-drop interface
- **Node-based architecture** for easy workflow design
- **Webhook support** for real-time triggers
- **Extensive integrations** with external services

### Why n8n for This Platform?
1. **Visual Workflow Design**: Easy to understand and modify
2. **Python Integration**: Seamless connection with our FastAPI backend
3. **Webhook Support**: Real-time workflow triggering
4. **Error Handling**: Robust error handling and retry mechanisms
5. **Monitoring**: Built-in workflow execution monitoring

## 🚀 Available Workflows

### 1. **Data Ingestion Workflow**
**Purpose**: Automatically process CSV files and ingest data into the platform

**File**: `workflows/consolidated-data-ingestion-workflow.json`

**What It Does**:
- Reads CSV files from specified locations
- Validates data format and content
- Calls the FastAPI `/ingest` endpoint
- Tracks processing status and results
- Sends success/failure notifications

**When to Use**:
- Regular data ingestion (daily, weekly)
- Batch processing of multiple files
- Automated data pipeline execution
- Error handling and retry scenarios

### 2. **Natural Language Query Workflow**
**Purpose**: Process natural language questions and translate them to structured queries

**File**: `workflows/nlq-translation-workflow.json`

**What It Does**:
- Receives natural language questions via webhook
- Uses OpenAI to translate questions to structured parameters
- Parses and validates the AI response
- Calls the FastAPI `/nlq` endpoint
- Returns formatted results to the user

**When to Use**:
- User-submitted natural language queries
- AI-powered query translation
- Complex question processing
- Integration with chat interfaces

## 🛠️ Setting Up Workflows

### Prerequisites
1. **n8n Service Running**: Accessible at http://localhost:5678
2. **API Service Running**: FastAPI accessible at http://localhost:8001
3. **Workflow Files**: JSON workflow definitions in the `workflows/` directory

### Step 1: Import Workflows

#### Method 1: Import from JSON Files
1. **Open n8n**: Navigate to http://localhost:5678
2. **Click "Import"**: In the top navigation
3. **Select File**: Choose the workflow JSON file
4. **Review Settings**: Check workflow configuration
5. **Click "Import"**: Add workflow to n8n

#### Method 2: Copy-Paste JSON
1. **Open n8n**: Navigate to http://localhost:5678
2. **Click "Import"**: In the top navigation
3. **Paste JSON**: Copy workflow JSON content
4. **Click "Import"**: Add workflow to n8n

### Step 2: Configure Workflow Settings

#### Data Ingestion Workflow Configuration
```json
{
  "name": "Data Ingestion Workflow",
  "nodes": [
    {
      "id": "webhook-trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [240, 300],
      "parameters": {
        "httpMethod": "POST",
        "path": "ingest-data",
        "responseMode": "responseNode"
      }
    }
  ]
}
```

#### NLQ Translation Workflow Configuration
```json
{
  "name": "NLQ Translation Workflow",
  "nodes": [
    {
      "id": "webhook-trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [240, 300],
      "parameters": {
        "httpMethod": "POST",
        "path": "nlq-translate",
        "responseMode": "responseNode"
      }
    }
  ]
}
```

### Step 3: Configure Environment Variables

#### Required Environment Variables
```bash
# API Configuration
API_BASE_URL=http://localhost:8001
API_TIMEOUT=30000

# OpenAI Configuration (for NLQ workflow)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Notification Configuration
SLACK_WEBHOOK_URL=your_slack_webhook_url
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

#### Setting in n8n
1. **Go to Settings**: Click gear icon in n8n
2. **Select "Variables"**: Environment variables section
3. **Add Variables**: Enter each variable name and value
4. **Save Changes**: Apply configuration

## 🔧 Workflow Execution

### Manual Execution

#### Running Data Ingestion Workflow
1. **Select Workflow**: Choose "Data Ingestion Workflow"
2. **Click "Execute"**: Manual execution button
3. **Monitor Progress**: Watch real-time execution
4. **Check Results**: View execution status and logs

#### Running NLQ Translation Workflow
1. **Select Workflow**: Choose "NLQ Translation Workflow"
2. **Click "Execute"**: Manual execution button
3. **Enter Question**: Provide natural language question
4. **View Results**: See translated query and results

### Automated Execution

#### Scheduled Execution
1. **Edit Workflow**: Open workflow for editing
2. **Add Cron Node**: Schedule node for timing
3. **Configure Schedule**: Set execution frequency
4. **Save and Activate**: Enable automated execution

#### Webhook Triggers
1. **Configure Webhook**: Set webhook endpoint
2. **Test Trigger**: Verify webhook functionality
3. **Integrate with External Systems**: Connect to data sources
4. **Monitor Triggers**: Track webhook usage

### Event-Based Execution

#### File Watcher Triggers
1. **Add File Watcher Node**: Monitor file system
2. **Configure Directory**: Set watch directory
3. **Set File Patterns**: Specify file types to watch
4. **Trigger Workflow**: Execute on file changes

#### API Response Triggers
1. **Configure API Node**: Set up API monitoring
2. **Set Response Conditions**: Define trigger criteria
3. **Link to Workflow**: Connect to workflow execution
4. **Monitor API Changes**: Track API responses

## 📊 Workflow Monitoring

### Execution History

#### Viewing Past Executions
1. **Go to Executions**: Click "Executions" in navigation
2. **Filter by Workflow**: Select specific workflow
3. **Review Results**: Check success/failure status
4. **Analyze Performance**: Review execution times

#### Execution Details
- **Start Time**: When execution began
- **Duration**: Total execution time
- **Status**: Success, failed, or running
- **Error Messages**: Details of any failures
- **Data Processed**: Records and files handled

### Performance Metrics

#### Key Metrics to Monitor
- **Execution Frequency**: How often workflows run
- **Success Rate**: Percentage of successful executions
- **Average Duration**: Typical execution time
- **Error Patterns**: Common failure causes
- **Resource Usage**: CPU and memory consumption

#### Setting Up Alerts
1. **Configure Notifications**: Set up alert channels
2. **Define Thresholds**: Set performance limits
3. **Create Alert Rules**: Define when to alert
4. **Test Alert System**: Verify notification delivery

## 🔄 Workflow Customization

### Modifying Existing Workflows

#### Adding New Nodes
1. **Open Workflow**: Edit existing workflow
2. **Add Node**: Drag new node from palette
3. **Configure Node**: Set node parameters
4. **Connect Nodes**: Link to existing workflow
5. **Test Changes**: Verify workflow functionality

#### Updating Node Configuration
1. **Select Node**: Click on node to edit
2. **Modify Parameters**: Change node settings
3. **Update Connections**: Adjust node relationships
4. **Save Changes**: Apply modifications

### Creating New Workflows

#### Workflow Design Process
1. **Define Purpose**: Clear workflow objective
2. **Identify Triggers**: How workflow starts
3. **Design Flow**: Node sequence and logic
4. **Add Error Handling**: Handle failure scenarios
5. **Test Workflow**: Verify functionality
6. **Deploy**: Activate in production

#### Common Node Types
- **Triggers**: Start workflow execution
- **Data Processing**: Transform and validate data
- **API Calls**: Connect to external services
- **Conditional Logic**: Make decisions based on data
- **Notifications**: Send alerts and updates
- **File Operations**: Read/write files

## 🚨 Error Handling & Troubleshooting

### Common Workflow Errors

#### API Connection Errors
**Symptoms**:
- Workflow fails with connection timeout
- API endpoint not responding
- Network connectivity issues

**Solutions**:
1. **Check API Status**: Verify FastAPI service is running
2. **Verify URLs**: Ensure correct API endpoints
3. **Check Network**: Verify network connectivity
4. **Review Logs**: Check API service logs

#### Data Validation Errors
**Symptoms**:
- CSV parsing failures
- Data type mismatches
- Missing required fields

**Solutions**:
1. **Validate CSV Format**: Check file structure
2. **Review Data Types**: Ensure correct data types
3. **Check Required Fields**: Verify all columns exist
4. **Test with Sample Data**: Use small test files

#### OpenAI Translation Errors
**Symptoms**:
- Translation failures
- API quota exceeded
- Invalid API responses

**Solutions**:
1. **Verify API Key**: Check OpenAI API key validity
2. **Check Quota**: Monitor API usage limits
3. **Validate Responses**: Ensure proper response format
4. **Review Error Logs**: Check OpenAI API errors

### Debugging Workflows

#### Enable Debug Mode
1. **Edit Workflow**: Open workflow for editing
2. **Enable Debug**: Toggle debug mode
3. **Run Test Execution**: Execute with debug enabled
4. **Review Debug Output**: Check detailed execution logs

#### Adding Debug Nodes
1. **Insert Debug Nodes**: Add at key workflow points
2. **Configure Output**: Set what to log
3. **Run Workflow**: Execute with debug nodes
4. **Review Logs**: Check debug output

#### Log Analysis
1. **Access Logs**: View workflow execution logs
2. **Filter by Error**: Focus on error messages
3. **Trace Execution**: Follow execution path
4. **Identify Root Cause**: Find error source

## 🔧 Advanced Workflow Features

### Conditional Logic

#### If-Then-Else Logic
```json
{
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "={{ $json.status }}",
          "operation": "equal",
          "value2": "success"
        }
      ]
    }
  }
}
```

#### Switch Statements
```json
{
  "type": "n8n-nodes-base.switch",
  "parameters": {
    "rules": {
      "rules": [
        {
          "value1": "={{ $json.platform }}",
          "operation": "equal",
          "value2": "Meta"
        },
        {
          "value1": "={{ $json.platform }}",
          "operation": "equal",
          "value2": "Google"
        }
      ]
    }
  }
}
```

### Data Transformation

#### JSON Processing
```json
{
  "type": "n8n-nodes-base.set",
  "parameters": {
    "values": {
      "string": [
        {
          "name": "processed_date",
          "value": "={{ new Date($json.date).toISOString() }}"
        }
      ]
    }
  }
}
```

#### Array Operations
```json
{
  "type": "n8n-nodes-base.splitInBatches",
  "parameters": {
    "batchSize": 100,
    "options": {}
  }
}
```

### External Integrations

#### Slack Notifications
```json
{
  "type": "n8n-nodes-base.slack",
  "parameters": {
    "operation": "postMessage",
    "channel": "#alerts",
    "text": "Data ingestion completed successfully!",
    "otherOptions": {}
  }
}
```

#### Email Notifications
```json
{
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "toEmail": "team@company.com",
    "subject": "Workflow Execution Report",
    "text": "Workflow completed with status: {{ $json.status }}"
  }
}
```

## 📈 Performance Optimization

### Workflow Efficiency

#### Reducing Execution Time
1. **Parallel Processing**: Execute independent nodes simultaneously
2. **Batch Operations**: Process data in chunks
3. **Caching**: Store frequently accessed data
4. **Optimized Queries**: Use efficient data queries

#### Resource Management
1. **Memory Usage**: Monitor memory consumption
2. **CPU Utilization**: Track processing overhead
3. **Network Calls**: Minimize external API calls
4. **Database Connections**: Optimize database queries

### Scaling Workflows

#### Horizontal Scaling
1. **Multiple Instances**: Run multiple n8n instances
2. **Load Balancing**: Distribute workflow load
3. **Queue Management**: Implement job queues
4. **Resource Allocation**: Allocate resources efficiently

#### Vertical Scaling
1. **Increase Resources**: Add more CPU/memory
2. **Optimize Code**: Improve workflow efficiency
3. **Database Optimization**: Enhance database performance
4. **Caching Strategy**: Implement intelligent caching

## 🔐 Security Considerations

### Workflow Security

#### Access Control
1. **User Authentication**: Secure n8n access
2. **Role-Based Access**: Limit user permissions
3. **Workflow Isolation**: Separate user workflows
4. **Audit Logging**: Track user actions

#### Data Security
1. **Encryption**: Encrypt sensitive data
2. **Secure Storage**: Protect stored credentials
3. **Network Security**: Secure API communications
4. **Input Validation**: Validate all inputs

### API Security

#### Authentication
1. **API Keys**: Use secure API keys
2. **Token Management**: Implement token rotation
3. **Rate Limiting**: Prevent API abuse
4. **Request Validation**: Validate all requests

#### Monitoring
1. **Access Logs**: Track API usage
2. **Security Alerts**: Monitor for suspicious activity
3. **Performance Monitoring**: Track API performance
4. **Error Tracking**: Monitor API errors

---

*This workflow guide provides comprehensive information about setting up, configuring, and managing n8n workflows in the AI Data Platform. For technical implementation details, refer to the Developer Guide.*
