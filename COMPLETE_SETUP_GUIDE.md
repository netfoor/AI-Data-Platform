# 🚀 Complete n8n Integration Setup Guide

## 🎯 **What We've Built**

You now have a **complete, professional-grade n8n automation system** for your AI Data Platform:

- ✅ **Docker-based n8n** (running on localhost:5678)
- ✅ **Complete workflow JSON** (ready to import)
- ✅ **Full API integration** (programmatic workflow management)
- ✅ **Enhanced CLI commands** (with API key support)
- ✅ **Professional automation** (scheduled + manual triggers)

## 🚀 **Quick Start (3 steps)**

### **Step 1: Get Your n8n API Key**
```bash
# Run the helper script
python get_n8n_api_key.py

# Or manually:
# 1. Go to http://localhost:5678
# 2. Settings → API Keys → Create API Key
# 3. Copy the key (looks like: n8n_api_xxxxxxxxxxxxxxxx)
```

### **Step 2: Set Up the Workflow**
```bash
# Create and activate the workflow automatically
python -m ai_data_platform n8n setup --api-key YOUR_API_KEY_HERE
```

### **Step 3: Test Everything**
```bash
# Test connection
python -m ai_data_platform n8n test --api-key YOUR_API_KEY_HERE

# Check status
python -m ai_data_platform n8n status --api-key YOUR_API_KEY_HERE

# Run data ingestion
python -m ai_data_platform n8n ingest --api-key YOUR_API_KEY_HERE
```

## 🔑 **API Key Management**

### **Option 1: Environment Variable (Recommended)**
```bash
# Windows PowerShell
$env:N8N_API_KEY="your_api_key_here"

# Windows Command Prompt
set N8N_API_KEY=your_api_key_here

# Then run commands without --api-key flag
python -m ai_data_platform n8n setup
python -m ai_data_platform n8n test
```

### **Option 2: Command Line Parameter**
```bash
# Pass API key with each command
python -m ai_data_platform n8n setup --api-key your_api_key_here
python -m ai_data_platform n8n test --api-key your_api_key_here
```

## 📋 **What Each Command Does**

### **`n8n setup`**
- 🔍 Tests connection to n8n
- 📋 Creates the data ingestion workflow
- 🚀 Activates the workflow automatically
- 📊 Returns workflow ID for future use

### **`n8n test`**
- 🔌 Tests n8n API connection
- 📋 Lists all existing workflows
- 🟢 Shows active/inactive status
- ✅ Confirms everything is working

### **`n8n status`**
- 📊 Shows detailed workflow information
- 📈 Lists recent executions
- 🔄 Shows workflow version and metadata
- 📅 Shows creation and update times

### **`n8n ingest`**
- 🚀 Triggers the data ingestion workflow
- 📁 Processes the specified CSV file
- 🔄 Runs the complete ETL pipeline
- 📊 Returns execution results

## 🎯 **Workflow Features**

### **Automation Capabilities:**
- 📅 **Daily Scheduler**: Runs automatically at 9 AM UTC
- 🖱️ **Manual Trigger**: Run anytime via CLI or n8n interface
- 🌐 **Webhook Support**: External triggers via HTTP
- 🔄 **Error Handling**: Automatic failure notifications
- 📊 **Execution Monitoring**: Track all runs and results

### **Data Processing:**
- 📁 **CSV Reading**: Processes ads_spend.csv
- 🔄 **Data Transformation**: Adds metadata and timestamps
- 🌐 **ETL Integration**: Calls your local ETL pipeline
- ✅ **Success/Error Handling**: Comprehensive status reporting

## 🐳 **Docker Management**

### **Start/Stop n8n:**
```bash
# Start n8n
docker-compose up -d n8n

# Stop n8n
docker-compose stop n8n

# View logs
docker-compose logs -f n8n

# Restart
docker-compose restart n8n
```

### **Check Status:**
```bash
# Container status
docker-compose ps

# n8n logs
docker-compose logs n8n
```

## 🔧 **Configuration Options**

### **Environment Variables:**
```bash
# n8n settings
N8N_BASE_URL=http://localhost:5678
N8N_API_KEY=your_api_key_here
N8N_WEBHOOK_SECRET=ai-platform-secret-2024

# AI Platform settings
API_HOST=127.0.0.1
API_PORT=8000
```

### **Customization:**
- **Change Schedule**: Edit the Cron node in n8n (currently: `0 9 * * *`)
- **Modify Endpoint**: Update HTTP Request node URL
- **Add Notifications**: Connect to email/Slack nodes
- **File Path**: Update CSV Reader node path

## 🧪 **Testing Your Setup**

### **1. Connection Test:**
```bash
python -m ai_data_platform n8n test --api-key YOUR_KEY
```
**Expected Output:**
```
🔍 Testing n8n connection...
✅ Successfully connected to n8n instance!
📋 Found X workflows:
  - AI Data Platform - Data Ingestion (🟢 Active)
```

### **2. Workflow Setup:**
```bash
python -m ai_data_platform n8n setup --api-key YOUR_KEY
```
**Expected Output:**
```
🔍 Testing n8n connection...
✅ Connected to n8n successfully!
📋 Setting up data ingestion workflow...
🎉 Workflow created and activated successfully!
📊 Workflow ID: workflow_xxxxxxxx
🚀 Ready to run data ingestion!
```

### **3. Data Ingestion:**
```bash
python -m ai_data_platform n8n ingest --api-key YOUR_KEY
```
**Expected Output:**
```
🚀 Triggering data ingestion workflow for ads_spend.csv...
✅ Data ingestion workflow executed successfully!
📊 Check n8n interface for execution details
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"Cannot connect to n8n"**
   ```bash
   # Check if Docker is running
   docker ps
   
   # Start n8n
   docker-compose up -d n8n
   
   # Check logs
   docker-compose logs n8n
   ```

2. **"API key required"**
   ```bash
   # Get your API key from n8n
   python get_n8n_api_key.py
   
   # Or set environment variable
   $env:N8N_API_KEY="your_key_here"
   ```

3. **"Workflow not found"**
   ```bash
   # Set up the workflow first
   python -m ai_data_platform n8n setup --api-key YOUR_KEY
   ```

4. **"Permission denied"**
   ```bash
   # Check Docker permissions
   docker-compose down
   docker-compose up -d n8n
   ```

### **Debug Commands:**
```bash
# Test n8n connection directly
curl http://localhost:5678

# Check container status
docker-compose ps

# View n8n logs
docker-compose logs -f n8n

# Access n8n container
docker exec -it n8n-ai-platform bash
```

## 🔮 **Future Enhancements**

### **Immediate Next Steps:**
1. **Test the complete workflow** with real data
2. **Customize the schedule** to your needs
3. **Add email notifications** for success/failure
4. **Integrate with your AI platform** API

### **Advanced Features:**
- **Multiple data sources** (more CSV files)
- **Advanced scheduling** (multiple time slots)
- **Slack/Teams integration** for notifications
- **Monitoring dashboard** for workflow health
- **Data validation** and quality checks

## 🎉 **Success Indicators**

### **Everything is Working When:**
- ✅ n8n accessible at http://localhost:5678
- ✅ API key authentication successful
- ✅ Workflow created and activated
- ✅ Manual execution successful
- ✅ Scheduled execution running
- ✅ ETL pipeline receiving requests
- ✅ Success/error notifications working

## 📞 **Getting Help**

### **If You Need Support:**
1. **Check logs**: `docker-compose logs n8n`
2. **Test connection**: `python -m ai_data_platform n8n test --api-key YOUR_KEY`
3. **Verify workflow**: `python -m ai_data_platform n8n status --api-key YOUR_KEY`
4. **Review this guide**: All common issues covered

---

## 🚀 **You're Ready to Go!**

**Your n8n automation system is now:**
- 🐳 **Running in Docker** (no trial limitations)
- 🔑 **Fully API-enabled** (complete automation)
- 📋 **Workflow-ready** (import with one command)
- 🚀 **Production-ready** (professional-grade setup)

**Next command to run:**
```bash
python get_n8n_api_key.py
```

**Then:**
```bash
python -m ai_data_platform n8n setup --api-key YOUR_API_KEY
```

**🎯 You'll have a fully automated data ingestion system!**

