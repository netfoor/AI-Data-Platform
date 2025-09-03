# AI Data Platform - Installation & Setup Guide

## 🚀 Quick Start

Get the AI Data Platform running in under 10 minutes with Docker Compose:

```bash
# Clone the repository
git clone <repository-url>
cd Figure-Agency

# Start all services
docker compose up -d --build

# Access the platform
# UI: http://localhost:8501
# API: http://localhost:8001
# n8n: http://localhost:5678
```

## 📋 Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Ubuntu 18.04+
- **Docker**: Docker Desktop 4.0+ or Docker Engine 20.10+
- **Memory**: Minimum 8GB RAM (16GB recommended)
- **Storage**: 10GB free disk space
- **Network**: Internet connection for Docker image downloads

### Software Dependencies
- **Docker Desktop**: For Windows/macOS users
- **Docker Engine**: For Linux users
- **Docker Compose**: Included with Docker Desktop, or install separately

## 🐳 Docker Installation

### Windows
1. **Download Docker Desktop**: Visit [docker.com](https://www.docker.com/products/docker-desktop)
2. **Install**: Run the installer and follow the setup wizard
3. **Enable WSL2**: If prompted, enable Windows Subsystem for Linux 2
4. **Restart**: Restart your computer after installation
5. **Verify**: Open Docker Desktop and ensure it's running

### macOS
1. **Download Docker Desktop**: Visit [docker.com](https://www.docker.com/products/docker-desktop)
2. **Install**: Drag Docker.app to Applications folder
3. **Launch**: Open Docker Desktop from Applications
4. **Verify**: Check that Docker is running in the menu bar

### Linux (Ubuntu)
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up stable repository
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker
```

## 📁 Project Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd Figure-Agency
```

### 2. Verify Project Structure
```bash
# Check that all required files exist
ls -la

# Expected structure:
# ├── docker-compose.yml
# ├── Dockerfile.api
# ├── Dockerfile.ui
# ├── requirements.txt
# ├── ai_data_platform/
# ├── ui/
# ├── workflows/
# └── data/
```

### 3. Prepare Data Directory
```bash
# Create data directory if it doesn't exist
mkdir -p data

# Copy sample data (if available)
cp ads_spend.csv data/
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=true

# Database Configuration
DATABASE_PATH=data/ai_data_platform.duckdb

# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678/

# OpenAI Configuration (for NLQ features)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/ai_data_platform.log
```

### Docker Compose Configuration

The `docker-compose.yml` file is pre-configured with:

```yaml
version: '3.8'
services:
  api:
    build: .
    dockerfile: Dockerfile.api
    ports:
      - "8001:8000"  # Host port 8001, container port 8000
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - DATABASE_PATH=/app/data/ai_data_platform.duckdb
      - LOG_LEVEL=INFO

  ui:
    build: .
    dockerfile: Dockerfile.ui
    ports:
      - "8501:8501"
    depends_on:
      - api
    environment:
      - API_BASE_URL=http://localhost:8001

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    volumes:
      - ./workflows:/home/node/.n8n/workflows
      - ./data:/home/node/.n8n/data
    environment:
      - WEBHOOK_URL=http://localhost:5678/
      - N8N_BASIC_AUTH_ACTIVE=false
```

## 🚀 Starting the Platform

### 1. Build and Start Services
```bash
# Build all services (first time only)
docker compose build

# Start all services in background
docker compose up -d

# Check service status
docker compose ps
```

### 2. Verify Services
```bash
# Check if all containers are running
docker ps

# Expected output:
# CONTAINER ID   IMAGE                    PORTS                    NAMES
# abc123...      figure-agency-api       0.0.0.0:8001->8000/tcp  ai-platform-api
# def456...      figure-agency-ui        0.0.0.0:8501->8501/tcp  ai-platform-ui
# ghi789...      n8nio/n8n:latest        0.0.0.0:5678->5678/tcp  ai-platform-n8n
```

### 3. Test Service Health
```bash
# Test API health
curl http://localhost:8001/health

# Test UI accessibility
curl http://localhost:8501

# Test n8n accessibility
curl http://localhost:5678
```

## 🌐 Accessing the Platform

### Web Interfaces
- **Main Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8001/docs
- **n8n Workflows**: http://localhost:5678

### API Endpoints
- **Health Check**: `GET http://localhost:8001/health`
- **Data Ingestion**: `POST http://localhost:8001/ingest`
- **Natural Language Query**: `POST http://localhost:8001/nlq`
- **Metrics**: `GET http://localhost:8001/metrics`

## 📊 Initial Data Setup

### 1. Sample Data Structure
Your CSV file should have this structure:
```csv
date,platform,account,campaign,country,device,spend,clicks,impressions,conversions
2025-06-01,Meta,CompanyA,SummerSale,US,Mobile,100.50,50,1000,5
2025-06-01,Google,CompanyA,SummerSale,US,Desktop,150.00,75,1500,8
```

### 2. Load Sample Data
```bash
# Via web interface
# 1. Open http://localhost:8501
# 2. Click "Data Ingestion"
# 3. Enter path: data/ads_spend.csv
# 4. Click "Ingest Data"

# Via API
curl -X POST "http://localhost:8001/ingest" \
  -H "Content-Type: application/json" \
  -d '{"csv_file_path": "data/ads_spend.csv"}'
```

### 3. Verify Data Loading
```bash
# Check if data was loaded
curl "http://localhost:8001/metrics?start_date=2025-06-01&end_date=2025-06-30"
```

## 🔄 Workflow Setup

### 1. Import n8n Workflows
1. **Open n8n**: Navigate to http://localhost:5678
2. **Click "Import"**: In the top navigation
3. **Select Workflow File**: Choose from `workflows/` directory
4. **Review Configuration**: Check workflow settings
5. **Click "Import"**: Add workflow to n8n

### 2. Available Workflows
- **Data Ingestion**: `workflows/consolidated-data-ingestion-workflow.json`
- **NLQ Translation**: `workflows/nlq-translation-workflow.json`

### 3. Configure Workflows
1. **Edit Workflow**: Click on imported workflow
2. **Update URLs**: Ensure API endpoints point to correct ports
3. **Set Environment Variables**: Configure API keys and settings
4. **Test Workflow**: Run manual execution to verify

## 🧪 Testing the Setup

### 1. Run Test Suite
```bash
# Install testing dependencies
pip install pytest pytest-cov httpx fastapi[testing]

# Run comprehensive tests
python run_tests.py all

# Expected: 72%+ pass rate (some tests require specific setup)
```

### 2. Manual Testing
```bash
# Test data ingestion
curl -X POST "http://localhost:8001/ingest" \
  -H "Content-Type: application/json" \
  -d '{"csv_file_path": "data/ads_spend.csv"}'

# Test natural language query
curl -X POST "http://localhost:8001/nlq" \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me daily metrics"}'

# Test metrics endpoint
curl "http://localhost:8001/metrics?start_date=2025-06-01&end_date=2025-06-30"
```

## 🔧 Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using port 8000
netstat -ano | findstr :8000

# Solution: Use different ports in docker-compose.yml
ports:
  - "8001:8000"  # Host port 8001, container port 8000
```

#### Docker Connection Issues
```bash
# Ensure Docker Desktop is running
# Check Docker service status
docker version

# Restart Docker Desktop if needed
```

#### Service Startup Failures
```bash
# Check service logs
docker compose logs api
docker compose logs ui
docker compose logs n8n

# Restart specific service
docker compose restart api
```

#### Database Issues
```bash
# Check database file permissions
ls -la data/ai_data_platform.duckdb

# Recreate database if corrupted
rm data/ai_data_platform.duckdb
docker compose restart api
```

### Performance Issues

#### Memory Usage
```bash
# Check container resource usage
docker stats

# Restart services to clear memory
docker compose restart
```

#### Slow Response Times
```bash
# Check database size
du -h data/ai_data_platform.duckdb

# Verify indexes are created
docker compose exec api python -c "
from ai_data_platform.database.schema import SchemaManager
from ai_data_platform.database.connection import DatabaseConnection
db = DatabaseConnection()
schema = SchemaManager(db)
schema.create_indexes()
"
```

## 📈 Monitoring & Maintenance

### Health Checks
```bash
# Regular health monitoring
curl http://localhost:8001/health

# Check service status
docker compose ps

# Monitor resource usage
docker stats
```

### Log Management
```bash
# View real-time logs
docker compose logs -f api

# Check log files
tail -f logs/ai_data_platform.log

# Rotate logs (if needed)
# Add logrotate configuration for production
```

### Backup & Recovery
```bash
# Backup database
cp data/ai_data_platform.duckdb data/backup_$(date +%Y%m%d_%H%M%S).duckdb

# Backup workflows
cp -r workflows workflows_backup_$(date +%Y%m%d_%H%M%S)

# Restore from backup
cp data/backup_YYYYMMDD_HHMMSS.duckdb data/ai_data_platform.duckdb
```

## 🚀 Production Deployment

### Environment Considerations
- **SSL/TLS**: Use reverse proxy (nginx) for HTTPS
- **Authentication**: Implement user authentication
- **Monitoring**: Add Prometheus/Grafana monitoring
- **Logging**: Centralized logging with ELK stack
- **Backup**: Automated backup strategies

### Scaling
- **Horizontal Scaling**: Multiple API instances behind load balancer
- **Database**: Consider PostgreSQL for larger datasets
- **Caching**: Redis for frequently accessed data
- **Queue**: Celery for background task processing

---

*This installation guide provides everything needed to get the AI Data Platform running. For advanced configuration and troubleshooting, refer to the System Architecture and Troubleshooting guides.*
