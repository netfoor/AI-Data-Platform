"""
n8n API Client for AI Data Platform
Provides programmatic access to n8n workflows and automation
"""
import json
import time
import logging
from typing import Dict, List, Optional, Any
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class N8nAPIClient:
    """Full-featured n8n API client with workflow management capabilities"""
    
    def __init__(self, base_url: str, api_key: str, webhook_secret: str = "ai-platform-secret-2024"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.webhook_secret = webhook_secret
        self.session = requests.Session()
        self.session.headers.update({
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        })
        
    def test_connection(self) -> bool:
        """Test connection to n8n instance"""
        try:
            # Try different API endpoints
            endpoints = [
                "/api/v1/health",
                "/api/health", 
                "/health",
                "/api/v1/workflows",
                "/api/workflows"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        logger.info(f"Successfully connected to n8n API via {endpoint}")
                        return True
                    elif response.status_code == 401:
                        logger.info(f"n8n API accessible via {endpoint} (authentication required)")
                        return True
                except Exception:
                    continue
            
            # If no API endpoints work, try basic connection
            response = self.session.get(f"{self.base_url}", timeout=10)
            if response.status_code == 200:
                logger.info("n8n instance is accessible (basic connection)")
                return True
            else:
                logger.error(f"n8n API responded with status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to connect to n8n API: {e}")
            return False
    
    def get_workflows(self) -> List[Dict[str, Any]]:
        """Get all workflows from n8n"""
        try:
            # Try different API endpoints
            endpoints = [
                "/api/v1/workflows",
                "/api/workflows",
                "/workflows"
            ]
            
            for endpoint in endpoints:
                try:
                    response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        workflows = response.json()
                        
                        # Handle different response formats
                        if isinstance(workflows, list):
                            # Direct list of workflows
                            logger.info(f"Retrieved {len(workflows)} workflows from n8n via {endpoint}")
                            return workflows
                        elif isinstance(workflows, dict) and 'data' in workflows:
                            # Wrapped in data object
                            workflows_list = workflows.get('data', [])
                            logger.info(f"Retrieved {len(workflows_list)} workflows from n8n via {endpoint}")
                            return workflows_list
                        else:
                            logger.warning(f"Unexpected workflow response format: {type(workflows)}")
                            continue
                            
                    elif response.status_code == 401:
                        logger.info(f"n8n API accessible via {endpoint} (authentication required)")
                        return []
                except Exception as e:
                    logger.debug(f"Failed to get workflows from {endpoint}: {e}")
                    continue
            
            logger.error("Failed to get workflows from any endpoint")
            return []
        except Exception as e:
            logger.error(f"Error getting workflows: {e}")
            return []
    
    def get_workflow_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get workflow by name"""
        workflows = self.get_workflows()
        for workflow in workflows:
            if workflow.get('name') == name:
                return workflow
        return None
    
    def create_workflow(self, workflow_data: Dict[str, Any]) -> Optional[str]:
        """Create a new workflow in n8n"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/workflows",
                json=workflow_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                workflow = response.json()
                workflow_id = workflow.get('id')
                logger.info(f"Created workflow '{workflow_data.get('name')}' with ID: {workflow_id}")
                return workflow_id
            else:
                logger.error(f"Failed to create workflow: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creating workflow: {e}")
            return None
    
    def update_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> bool:
        """Update an existing workflow"""
        try:
            response = self.session.put(
                f"{self.base_url}/api/v1/workflows/{workflow_id}",
                json=workflow_data,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Updated workflow {workflow_id}")
                return True
            else:
                logger.error(f"❌ Failed to update workflow: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error updating workflow: {e}")
            return False
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow"""
        try:
            response = self.session.delete(f"{self.base_url}/api/v1/workflows/{workflow_id}", timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Deleted workflow {workflow_id}")
                return True
            else:
                logger.error(f"❌ Failed to delete workflow: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deleting workflow: {e}")
            return False
    
    def activate_workflow(self, workflow_id: str) -> bool:
        """Activate a workflow"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/workflows/{workflow_id}/activate", timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Activated workflow {workflow_id}")
                return True
            else:
                logger.error(f"❌ Failed to activate workflow: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error activating workflow: {e}")
            return False
    
    def deactivate_workflow(self, workflow_id: str) -> bool:
        """Deactivate a workflow"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/workflows/{workflow_id}/deactivate", timeout=10)
            
            if response.status_code == 200:
                logger.info(f"✅ Deactivated workflow {workflow_id}")
                return True
            else:
                logger.error(f"❌ Failed to deactivate workflow: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error deactivating workflow: {e}")
            return False
    
    def execute_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute a workflow manually"""
        try:
            payload = {"data": data} if data else {}
            response = self.session.post(
                f"{self.base_url}/api/v1/workflows/{workflow_id}/execute",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                execution_id = result.get('executionId')
                logger.info(f"✅ Executed workflow {workflow_id}, execution ID: {execution_id}")
                return execution_id
            else:
                logger.error(f"❌ Failed to execute workflow: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error executing workflow: {e}")
            return None
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/executions/{execution_id}", timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"❌ Failed to get execution status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error getting execution status: {e}")
            return None
    
    def trigger_webhook(self, webhook_url: str, data: Dict[str, Any]) -> bool:
        """Trigger a webhook endpoint"""
        try:
            response = requests.post(
                webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Webhook triggered successfully: {response.status_code}")
                return True
            else:
                logger.error(f"❌ Webhook failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error triggering webhook: {e}")
            return False
    
    def setup_data_ingestion_workflow(self, csv_file_path: str = "ads_spend.csv") -> Optional[str]:
        """Set up the complete data ingestion workflow"""
        try:
            # Check if workflow already exists
            existing_workflow = self.get_workflow_by_name("AI Data Platform - Data Ingestion")
            if existing_workflow:
                workflow_id = existing_workflow.get('id')
                logger.info(f"📋 Workflow already exists with ID: {workflow_id}")
                return workflow_id
            
            # Load workflow template
            workflow_path = Path("workflows/simple-data-ingestion-workflow.json")
            if not workflow_path.exists():
                # Fallback to original workflow
                workflow_path = Path("workflows/data-ingestion-workflow.json")
                if not workflow_path.exists():
                    logger.error(f"Workflow template not found")
                    return None
            
            with open(workflow_path, 'r', encoding='utf-8') as f:
                workflow_data = json.load(f)
            
            # Update CSV file path
            for node in workflow_data.get('nodes', []):
                if node.get('name') == 'Read CSV File':
                    node['parameters']['filePath'] = csv_file_path
                elif node.get('name') == 'Trigger ETL Pipeline':
                    # Update the CSV file path in the body parameters
                    for param in node['parameters']['bodyParameters']['parameters']:
                        if param['name'] == 'csv_file_path':
                            param['value'] = csv_file_path
            
            # Create workflow
            workflow_id = self.create_workflow(workflow_data)
            if workflow_id:
                # Activate the workflow
                if self.activate_workflow(workflow_id):
                    logger.info(f"Data ingestion workflow created and activated successfully!")
                    return workflow_id
                else:
                    logger.warning(f"Workflow created but failed to activate: {workflow_id}")
                    return workflow_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error setting up data ingestion workflow: {e}")
            return None
    
    def run_data_ingestion(self, csv_file_path: str = "ads_spend.csv") -> bool:
        """Run the data ingestion workflow"""
        try:
            # Ensure workflow exists and is active
            workflow_id = self.setup_data_ingestion_workflow(csv_file_path)
            if not workflow_id:
                return False
            
            # Execute the workflow
            execution_id = self.execute_workflow(workflow_id, {
                "csv_file_path": csv_file_path,
                "timestamp": time.time(),
                "source": "api_client"
            })
            
            if execution_id:
                logger.info(f"Data ingestion workflow executed successfully")
                return True
            else:
                logger.error("Failed to execute data ingestion workflow")
                return False
                
        except Exception as e:
            logger.error(f"Error running data ingestion: {e}")
            return False
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get comprehensive workflow status"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/workflows/{workflow_id}", timeout=10)
            
            if response.status_code == 200:
                workflow = response.json()
                return {
                    "id": workflow.get('id'),
                    "name": workflow.get('name'),
                    "active": workflow.get('active', False),
                    "created_at": workflow.get('createdAt'),
                    "updated_at": workflow.get('updatedAt'),
                    "version_id": workflow.get('versionId'),
                    "tags": workflow.get('tags', []),
                    "nodes_count": len(workflow.get('nodes', [])),
                    "status": "active" if workflow.get('active') else "inactive"
                }
            else:
                return {"error": f"Failed to get workflow: {response.status_code}"}
                
        except Exception as e:
            return {"error": f"Error getting workflow status: {e}"}
    
    def monitor_workflow_executions(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent workflow executions"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/executions",
                params={"workflowId": workflow_id, "limit": limit},
                timeout=10
            )
            
            if response.status_code == 200:
                executions = response.json()
                logger.info(f"Retrieved {len(executions)} executions for workflow {workflow_id}")
                return executions
            else:
                logger.error(f"Failed to get executions: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting executions: {e}")
            return []
