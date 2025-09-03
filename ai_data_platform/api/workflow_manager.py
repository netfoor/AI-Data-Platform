"""
Workflow manager for orchestrating n8n workflows with ETL pipeline
"""
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from .n8n_client import N8nClient
from ..ingestion.etl_pipeline import ETLPipeline, ETLPipelineResult
from ..config import settings

logger = logging.getLogger(__name__)


class WorkflowManager:
    """Manages n8n workflow orchestration and ETL pipeline integration"""
    
    def __init__(self):
        """Initialize workflow manager"""
        self.n8n_client = N8nClient()
        self.etl_pipeline: Optional[ETLPipeline] = None
        
    def setup_data_ingestion_workflow(self) -> bool:
        """Set up the automated data ingestion workflow in n8n"""
        try:
            logger.info("Setting up data ingestion workflow in n8n")
            
            # For now, we'll just provide setup instructions
            # In a real implementation, this would test connection and create workflows
            logger.info("n8n workflow setup requires manual configuration")
            logger.info("Please follow the setup guide in N8N_SETUP_GUIDE.md")
            
            return False
                
        except Exception as e:
            logger.error(f"Error setting up data ingestion workflow: {e}")
            return False
    
    def _find_ingestion_workflow(self, workflows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Find existing data ingestion workflow"""
        for workflow in workflows:
            if workflow.get('name', '').lower().startswith('data ingestion'):
                return workflow
        return None
    
    async def _create_ingestion_workflow(self) -> bool:
        """Create new data ingestion workflow in n8n"""
        try:
            # This would typically involve creating the workflow via n8n API
            # For now, we'll log that manual creation is needed
            logger.info("Please create the data ingestion workflow manually in n8n.cloud")
            logger.info("The workflow should include:")
            logger.info("1. CSV file reader node")
            logger.info("2. Data transformation node")
            logger.info("3. HTTP request node to trigger local ETL pipeline")
            logger.info("4. Error handling and notification nodes")
            
            return False
            
        except Exception as e:
            logger.error(f"Error creating ingestion workflow: {e}")
            return False
    
    def trigger_data_ingestion(self, csv_file_path: Optional[str] = None) -> ETLPipelineResult:
        """Trigger data ingestion workflow and execute ETL pipeline"""
        try:
            logger.info("Starting automated data ingestion workflow")
            
            # If n8n workflow is configured, trigger it
            if settings.n8n.workflow_id and settings.n8n.enable_automation:
                logger.info("Triggering n8n workflow for data ingestion")
                # Note: This would be async in a real implementation
                # For now, we'll just log the attempt
                logger.info(f"Would trigger workflow {settings.n8n.workflow_id}")
            
            # Execute ETL pipeline directly
            return self._execute_etl_pipeline(csv_file_path)
            
        except Exception as e:
            logger.error(f"Error in data ingestion workflow: {e}")
            result = ETLPipelineResult()
            result.success = False
            result.error_message = str(e)
            return result
    
    def _execute_etl_pipeline(self, csv_file_path: Optional[str] = None) -> ETLPipelineResult:
        """Execute ETL pipeline directly"""
        try:
            # Use default CSV file if none specified
            if not csv_file_path:
                csv_file_path = str(Path(settings.data.input_directory) / 'ads_spend.csv')
            
            # Initialize ETL pipeline
            self.etl_pipeline = ETLPipeline(csv_file_path)
            
            # Execute pipeline
            result = self.etl_pipeline.run()
            
            if result.success:
                logger.info("ETL pipeline executed successfully")
                # Update n8n with success status if workflow was triggered
                if settings.n8n.workflow_id:
                    self._update_workflow_status(settings.n8n.workflow_id, 'success', result)
            else:
                logger.error("ETL pipeline failed")
                # Update n8n with failure status if workflow was triggered
                if settings.n8n.workflow_id:
                    self._update_workflow_status(settings.n8n.workflow_id, 'failed', result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing ETL pipeline: {e}")
            result = ETLPipelineResult()
            result.success = False
            result.error_message = str(e)
            return result
    
    def _update_workflow_status(self, workflow_id: str, status: str, result: ETLPipelineResult):
        """Update workflow status in n8n"""
        try:
            status_data = {
                'status': status,
                'execution_time': datetime.utcnow().isoformat(),
                'result_summary': result.get_summary()
            }
            
            # This would typically update the workflow execution status
            # For now, we'll just log it
            logger.info(f"Workflow {workflow_id} status: {status}")
            logger.info(f"Result summary: {result.get_summary()}")
            
        except Exception as e:
            logger.error(f"Error updating workflow status: {e}")
    
    async def schedule_ingestion(self, schedule_type: str = 'daily', time: str = '09:00') -> bool:
        """Schedule automated data ingestion"""
        try:
            logger.info(f"Scheduling {schedule_type} data ingestion at {time}")
            
            # This would typically involve setting up cron jobs or n8n schedules
            # For now, we'll log the scheduling request
            logger.info("Please configure the schedule manually in n8n.cloud:")
            logger.info(f"- Schedule type: {schedule_type}")
            logger.info(f"- Time: {time}")
            logger.info("- Trigger: Cron expression or n8n scheduler node")
            
            return True
            
        except Exception as e:
            logger.error(f"Error scheduling ingestion: {e}")
            return False
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current status of all workflows"""
        try:
            if not settings.n8n.workflow_id:
                return {'status': 'no_workflow_configured'}
            
            # For now, return basic status
            # In a real implementation, this would fetch from n8n API
            return {
                'workflow_id': settings.n8n.workflow_id,
                'status': 'configured_but_not_connected',
                'automation_enabled': settings.n8n.enable_automation,
                'note': 'Use N8N_SETUP_GUIDE.md to complete setup'
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {'status': 'error', 'error': str(e)}
    
    async def close(self):
        """Close workflow manager and cleanup resources"""
        try:
            await self.n8n_client.close()
        except Exception as e:
            logger.error(f"Error closing workflow manager: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        asyncio.run(self.close())
