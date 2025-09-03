"""
Main entry point for AI Data Platform
"""
import logging
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_data_platform.config import settings
from ai_data_platform.utils.logging import setup_logging

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Database path: {settings.database.path}")
    
    # Initialize database connection
    from ai_data_platform.database.connection import db
    
    try:
        # Test database connection
        with db.get_connection() as conn:
            result = conn.execute("SELECT 'Database connection successful' as message").fetchone()
            logger.info(result[0])
            
        logger.info("AI Data Platform initialized successfully")
        logger.info("Ready for data ingestion and analysis")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI Data Platform: {e}")
        sys.exit(1)

def cli_main():
    """CLI entry point"""
    from ai_data_platform.cli import cli
    cli()

if __name__ == "__main__":
    # Check if CLI arguments are provided
    if len(sys.argv) > 1:
        cli_main()
    else:
        main()