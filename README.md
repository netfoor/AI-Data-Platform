# AI Data Platform

A comprehensive data engineering solution for automated data ingestion, KPI modeling, and analytics accessibility.

## Features

- Automated data ingestion using n8n workflows
- DuckDB-based data warehouse
- Marketing KPI computation (CAC and ROAS)
- REST API for metrics access
- Natural language query interface
- Time-based comparative analysis

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-data-platform

# Set up virtual environment and install dependencies
python setup_env.py

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/Linux/macOS:
source venv/bin/activate

# Install dependencies (if not done by setup script)
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your settings
# Default settings should work for development
```

### 3. Initialize the Platform

```bash
# Run the main application
python -m ai_data_platform
```

## Project Structure

```
ai_data_platform/
├── ai_data_platform/          # Main application package
│   ├── api/                   # REST API endpoints
│   ├── database/              # Database utilities
│   ├── models/                # Data models
│   ├── utils/                 # Utility functions
│   ├── workflows/             # n8n workflow configs
│   └── config.py              # Configuration management
├── data/                      # Data files directory
├── logs/                      # Application logs
├── tests/                     # Test suite
├── requirements.txt           # Python dependencies
└── setup_env.py              # Environment setup script
```