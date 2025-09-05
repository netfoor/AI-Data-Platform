# Project Organization Guide

This document explains the new organized structure of the AI Data Platform project.

## 📁 Folder Structure

### `/config/` - Configuration Files
Contains all configuration and setup files:
- `docker-compose.yml` - Main Docker orchestration
- `docker-compose.prod.yml` - Production Docker setup
- `requirements.txt` - Python dependencies
- `pytest.ini` - Testing configuration
- `Dockerfile.*` - Docker build files
- `render.yaml` - Render deployment config

### `/scripts/` - Utility Scripts
Organized by purpose:

#### `/scripts/deployment/`
- `deploy-to-render.bat` - Windows deployment script
- `deploy-to-render.sh` - Unix deployment script

#### `/scripts/development/`
- `setup_env.py` - Environment setup utility
- `check_database.py` - Database verification
- `check_workflow.py` - Workflow validation
- `force_activate.py` - Development utilities
- `rest_api_backup.py` - API backup

#### `/scripts/n8n/`
- `create_*.py` - Workflow creation scripts
- `fix_*.py` - Workflow repair utilities
- `get_*.py` - Data retrieval scripts

#### `/scripts/testing/`
- `test_*.py` - Individual test scripts
- `run_tests.py` - Test runner

### `/examples/` - Examples and Templates
- `api_test_examples.md` - API usage examples
- `*.json` - Workflow configuration examples
- Sample configurations and templates

## 🚀 Updated Usage

### Environment Setup
```bash
# Use the new path for setup
python scripts/development/setup_env.py
```

### Running Tests
```bash
# Run all tests
python scripts/testing/run_tests.py

# Run specific tests
python scripts/testing/test_api.py
```

### Deployment
```bash
# Deploy to Render (Windows)
scripts/deployment/deploy-to-render.bat

# Deploy to Render (Unix/Linux)
scripts/deployment/deploy-to-render.sh
```

### Docker Setup
```bash
# All Docker files are now in config/
docker-compose -f config/docker-compose.yml up
```

## 📝 Benefits of This Organization

1. **Clean Root Directory** - Only essential files at project root
2. **Logical Grouping** - Related scripts grouped by purpose
3. **Easy Navigation** - Clear folder structure for developers
4. **Better Maintenance** - Easier to find and update specific scripts
5. **Professional Structure** - Industry-standard project organization

## 🔧 Migration Notes

If you have existing scripts or workflows that reference the old paths, update them to use the new structure:

- `setup_env.py` → `scripts/development/setup_env.py`
- `docker-compose.yml` → `config/docker-compose.yml`
- `test_*.py` → `scripts/testing/test_*.py`
- Examples and templates → `examples/`

## 📋 Root Directory Contents

After organization, the root directory contains only:
- `README.md` - Project overview
- `SECURITY.md` - Security guidelines
- `AI_DATA_PLATFORM_GUIDE.md` - Comprehensive guide
- `.env.example` - Environment template
- `.gitignore` - Git ignore rules
- Core application folders (`ai_data_platform/`, `data/`, `docs/`, etc.)
