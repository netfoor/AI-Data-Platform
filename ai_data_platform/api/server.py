"""
Server module for running the AI Data Platform REST API
"""
import uvicorn
import logging
from pathlib import Path

from .rest_api import app
from ..config import settings

logger = logging.getLogger(__name__)

def run_server(
    host: str = "127.0.0.1",
    port: int = 8000,
    reload: bool = False,
    log_level: str = "info"
):
    """Run the FastAPI server
    
    Args:
        host: Host to bind to
        port: Port to bind to
        reload: Enable auto-reload for development
        log_level: Logging level
    """
    try:
        logger.info(f"Starting AI Data Platform API server on {host}:{port}")
        logger.info(f"API documentation available at: http://{host}:{port}/docs")
        logger.info(f"ReDoc documentation available at: http://{host}:{port}/redoc")
        
        uvicorn.run(
            "ai_data_platform.api.rest_api:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        raise

if __name__ == "__main__":
    # Run server when module is executed directly
    run_server()
