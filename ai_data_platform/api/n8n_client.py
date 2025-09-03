"""
n8n client for communicating with n8n.cloud instance
"""
import logging
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime
from ..config import settings

logger = logging.getLogger(__name__)


class N8nClient:
    """Client for interacting with n8n.cloud instance"""
    
    def __init__(self):
        """Initialize n8n client with configuration"""
        self.base_url = settings.n8n.base_url.rstrip('/')
        self.api_key = settings.n8n.api_key
        self.webhook_secret = settings.n8n.webhook_secret
        self.workflow_id = settings.n8n.workflow_id
        
        # HTTP client with timeout
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            headers=self._get_headers()
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for n8n API requests"""
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'AI-Data-Platform/{settings.version}'
        }
        
        if self.api_key:
            headers['X-N8N-API-KEY'] = self.api_key
        
        return headers
    
    def test_connection(self) -> bool:
        """Test connection to n8n instance"""
        try:
            # For now, we'll just check if the URL is accessible
            # In a real implementation, this would make an HTTP request
            logger.info(f"Testing connection to n8n instance: {self.base_url}")
            logger.info("Note: Full connection test requires API key configuration")
            
            # Return True if we have a valid URL, False otherwise
            return bool(self.base_url and self.base_url.startswith('https://'))
            
        except Exception as e:
            logger.error(f"Error testing n8n connection: {e}")
            return False
    
    async def get_workflows(self) -> List[Dict[str, Any]]:
        """Get list of available workflows"""
        try:
            response = await self.client.get(f"{self.base_url}/api/v1/workflows")
            if response.status_code == 200:
                workflows = response.json()
                logger.info(f"Retrieved {len(workflows)} workflows from n8n")
                return workflows
            else:
                logger.error(f"Failed to get workflows: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting workflows: {e}")
            return []
    
    async def trigger_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """Trigger a workflow execution"""
        try:
            payload = {
                'trigger': 'manual',
                'timestamp': datetime.utcnow().isoformat(),
                'data': data or {}
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/trigger",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully triggered workflow {workflow_id}")
                return True
            else:
                logger.error(f"Failed to trigger workflow {workflow_id}: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error triggering workflow {workflow_id}: {e}")
            return False
    
    async def get_workflow_executions(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent executions for a specific workflow"""
        try:
            response = await self.client.get(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/executions",
                params={'limit': limit}
            )
            
            if response.status_code == 200:
                executions = response.json()
                logger.info(f"Retrieved {len(executions)} executions for workflow {workflow_id}")
                return executions
            else:
                logger.error(f"Failed to get executions: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting workflow executions: {e}")
            return []
    
    async def create_webhook(self, workflow_id: str, webhook_url: str) -> Optional[str]:
        """Create a webhook for a workflow"""
        try:
            payload = {
                'url': webhook_url,
                'method': 'POST',
                'authentication': 'header',
                'httpHeaderName': 'X-Webhook-Secret',
                'httpHeaderValue': self.webhook_secret or 'default-secret'
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/webhooks",
                json=payload
            )
            
            if response.status_code in [200, 201]:
                webhook_data = response.json()
                webhook_id = webhook_data.get('id')
                logger.info(f"Created webhook {webhook_id} for workflow {workflow_id}")
                return webhook_id
            else:
                logger.error(f"Failed to create webhook: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            return None
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        import asyncio
        try:
            asyncio.run(self.close())
        except:
            pass
