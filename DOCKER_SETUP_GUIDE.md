# Docker-based n8n Setup Guide

## 🎯 **Overview**

This guide will help you set up a **complete Docker-based n8n solution** for your AI Data Platform. This approach gives you:

- ✅ **Full API access** (no trial limitations)
- ✅ **Complete automation** capabilities
- ✅ **Professional workflow management**
- ✅ **Easy deployment** and scaling
- ✅ **Future integration** with your AI platform

## 🚀 **Quick Start (5 minutes)**

### 1. **Access n8n Interface**
- Open your browser and go to: **http://localhost:5678**
- Login with:
  - **Username**: `admin`
  - **Password**: `aiplatform2024`

### 2. **Import the Workflow**
- Click **"Import from file"** in n8n
- Select: `workflows/data-ingestion-workflow.json`
- Click **"Import"**

### 3. **Activate the Workflow**
- Click **"Activate"** button
- Your workflow is now running! 🎉

## 📋 **What's Included**

### **Complete Workflow Features:**
- 📅 **Daily Scheduler** (9 AM UTC)
- 📁 **CSV File Reader** (ads_spend.csv)
- 🔄 **Data Transformation** (adds metadata)
- 🌐 **HTTP Trigger** (calls your ETL pipeline)
- ✅ **Success/Error Handling**
- 📊 **Detailed Notifications**

### **Automation Capabilities:**
- **Manual Trigger**: Run anytime via n8n interface
- **Scheduled**: Daily at 9 AM UTC
- **Webhook**: External triggers via HTTP
- **Error Handling**: Automatic failure notifications

## 🐳 **Docker Management**

### **Start Services:**
```bash
# Start n8n only
docker-compose up -d n8n

# Start all services (future)
docker-compose up -d
```

### **Stop Services:**
```bash
# Stop n8n
docker-compose stop n8n

# Stop all services
docker-compose down
```

### **View Logs:**
```bash
# n8n logs
docker-compose logs -f n8n

# All services logs
docker-compose logs -f
```

### **Restart Services:**
```bash
# Restart n8n
docker-compose restart n8n

# Restart all
docker-compose restart
```

## 🔧 **Configuration**

### **Environment Variables:**
The workflow is configured to work with:
- **ETL Endpoint**: `http://localhost:8000/api/ingest`
- **Webhook Secret**: `ai-platform-secret-2024`
- **CSV File**: `ads_spend.csv`

### **Customization Options:**
1. **Change Schedule**: Edit the Cron node (currently: `0 9 * * *`)
2. **Modify Endpoint**: Update HTTP Request node URL
3. **Add Notifications**: Connect to email/Slack nodes
4. **File Path**: Update CSV Reader node path

## 📊 **Workflow Flow**

```
Daily Scheduler (9 AM) → Generate Batch ID → Read CSV → Transform Data → Trigger ETL → Check Success
                                                                                    ↓
                                                                              Success/Error Notifications
```

## 🧪 **Testing the Workflow**

### **Manual Test:**
1. Go to n8n interface: http://localhost:5678
2. Find your workflow
3. Click **"Execute Workflow"**
4. Watch the execution in real-time

### **Scheduled Test:**
1. Wait for 9 AM UTC (or change the schedule)
2. Workflow runs automatically
3. Check execution history

### **API Test:**
```bash
# Test the webhook endpoint
curl -X POST http://localhost:5678/webhook/start-webhook \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

## 🔗 **Integration with Your AI Platform**

### **Current Setup:**
- n8n runs on **port 5678**
- Your AI platform will run on **port 8000**
- They communicate via HTTP requests

### **Future Deployment:**
When you're ready to deploy both services together:

1. **Uncomment** the AI platform service in `docker-compose.yml`
2. **Build** your AI platform Docker image
3. **Run** both services together: `docker-compose up -d`

## 📁 **File Structure**

```
Figure-Agency/
├── docker-compose.yml              # Docker services configuration
├── workflows/
│   └── data-ingestion-workflow.json  # Complete n8n workflow
├── data/                           # Shared data directory
├── ai_data_platform/              # Your Python application
└── DOCKER_SETUP_GUIDE.md         # This guide
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Port Already in Use:**
   ```bash
   # Check what's using port 5678
   netstat -ano | findstr :5678
   
   # Kill the process or change port in docker-compose.yml
   ```

2. **Workflow Won't Import:**
   - Ensure n8n is running: `docker-compose ps`
   - Check file path: `workflows/data-ingestion-workflow.json`
   - Verify JSON syntax

3. **ETL Pipeline Not Responding:**
   - Ensure your AI platform is running on port 8000
   - Check the endpoint URL in the workflow
   - Verify webhook secret matches

### **Debug Commands:**
```bash
# Check container status
docker-compose ps

# View n8n logs
docker-compose logs n8n

# Access n8n container
docker exec -it n8n-ai-platform bash

# Restart n8n
docker-compose restart n8n
```

## 🔮 **Future Enhancements**

### **Planned Features:**
- **Email Notifications**: Success/failure alerts
- **Slack Integration**: Team notifications
- **Multiple Data Sources**: Support for more CSV files
- **Advanced Scheduling**: Multiple time slots
- **Monitoring Dashboard**: Workflow health checks

### **Scaling Options:**
- **Multiple n8n Workers**: For high-volume processing
- **Load Balancing**: Distribute workflow execution
- **Database Integration**: Store workflow results
- **API Gateway**: Centralized workflow management

## 🎉 **Success Indicators**

### **Workflow is Working When:**
- ✅ n8n interface accessible at http://localhost:5678
- ✅ Workflow imported and activated
- ✅ Manual execution successful
- ✅ Scheduled execution running
- ✅ ETL pipeline receiving requests
- ✅ Success/error notifications working

## 📞 **Support**

### **If You Need Help:**
1. **Check logs**: `docker-compose logs n8n`
2. **Verify configuration**: Check docker-compose.yml
3. **Test components**: Manual workflow execution
4. **Review this guide**: All common issues covered

---

## 🚀 **Next Steps**

1. **Import the workflow** into n8n
2. **Test manual execution**
3. **Verify scheduled execution**
4. **Customize as needed**
5. **Integrate with your AI platform**

**Your n8n automation is ready to go! 🎯**

