# Security Configuration Guide

## Environment Variables

This project uses environment variables to manage sensitive configuration data. **Never commit sensitive data to git!**

### Setup Instructions

1. Copy the template file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your actual values:
   - Replace all placeholder values with real credentials
   - Use strong passwords and encryption keys
   - Keep API keys secure

### Important Security Notes

- ✅ The `.env` file is already in `.gitignore` and will NOT be committed
- ✅ `N8N_AUTOMATION_PROMPT.md` is excluded from git (contains sensitive prompts)
- ✅ All Docker Compose files now use environment variables
- ⚠️ Never share your `.env` file or commit it to version control
- ⚠️ Rotate API keys and passwords regularly
- ⚠️ Use different credentials for development and production

### Required Environment Variables

See `.env.example` for a complete list of required variables including:
- N8N authentication credentials
- API keys for external services
- Database passwords (if using external DB)
- Webhook secrets

### Production Deployment

For production environments:
1. Use strong, unique passwords
2. Enable HTTPS/SSL
3. Use environment-specific `.env` files
4. Consider using a secrets management service
5. Enable logging and monitoring

## Files Excluded from Git

The following files contain sensitive information and are excluded:
- `.env` - Environment variables with real credentials
- `N8N_AUTOMATION_PROMPT.md` - AI automation prompts
- `logs/` - Log files that might contain sensitive data
- `data/*.duckdb*` - Database files with actual data
