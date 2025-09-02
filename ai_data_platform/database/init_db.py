"""
Database initialization script for the AI Data Platform
"""
import logging
from pathlib import Path
from typing import Optional

from .connection import DatabaseConnection, db
from .schema import SchemaManager

logger = logging.getLogger(__name__)


def initialize_database(db_path: Optional[str] = None, force_recreate: bool = False) -> bool:
    """Initialize the database with all required tables, indexes, and views
    
    Args:
        db_path: Path to the database file. If None, uses default from config.
        force_recreate: If True, drops existing tables before creating new ones.
        
    Returns:
        True if initialization was successful, False otherwise.
    """
    try:
        # Use provided db_path or default connection
        if db_path:
            db_conn = DatabaseConnection(db_path)
        else:
            db_conn = db
        
        schema_manager = SchemaManager(db_conn)
        
        logger.info("Starting database initialization...")
        
        # If force_recreate is True, drop existing tables
        if force_recreate:
            logger.info("Force recreate enabled - dropping existing tables...")
            try:
                schema_manager.drop_table("kpi_metrics")
                schema_manager.drop_table("raw_ads_spend")
            except Exception as e:
                logger.warning(f"Error dropping tables (may not exist): {e}")
        
        # Create tables
        logger.info("Creating database tables...")
        schema_manager.create_raw_ads_spend_table()
        schema_manager.create_kpi_metrics_table()
        
        # Create indexes for performance
        logger.info("Creating database indexes...")
        schema_manager.create_indexes()
        
        # Create useful views
        logger.info("Creating database views...")
        schema_manager.create_views()
        
        # Verify tables were created successfully
        tables_to_verify = ["raw_ads_spend", "kpi_metrics"]
        for table_name in tables_to_verify:
            if not schema_manager.table_exists(table_name):
                raise Exception(f"Table {table_name} was not created successfully")
            
            row_count = schema_manager.get_table_row_count(table_name)
            logger.info(f"Table {table_name} created successfully with {row_count} rows")
        
        logger.info("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def reset_database(db_path: Optional[str] = None) -> bool:
    """Reset the database by dropping and recreating all tables
    
    Args:
        db_path: Path to the database file. If None, uses default from config.
        
    Returns:
        True if reset was successful, False otherwise.
    """
    logger.warning("Resetting database - all data will be lost!")
    return initialize_database(db_path, force_recreate=True)


def verify_database_health(db_path: Optional[str] = None) -> dict:
    """Verify database health and return status information
    
    Args:
        db_path: Path to the database file. If None, uses default from config.
        
    Returns:
        Dictionary with health check results
    """
    health_status = {
        "healthy": False,
        "tables_exist": {},
        "row_counts": {},
        "errors": []
    }
    
    try:
        # Use provided db_path or default connection
        if db_path:
            db_conn = DatabaseConnection(db_path)
        else:
            db_conn = db
        
        schema_manager = SchemaManager(db_conn)
        
        # Check if required tables exist
        required_tables = ["raw_ads_spend", "kpi_metrics"]
        for table_name in required_tables:
            try:
                exists = schema_manager.table_exists(table_name)
                health_status["tables_exist"][table_name] = exists
                
                if exists:
                    row_count = schema_manager.get_table_row_count(table_name)
                    health_status["row_counts"][table_name] = row_count
                else:
                    health_status["errors"].append(f"Table {table_name} does not exist")
                    
            except Exception as e:
                health_status["errors"].append(f"Error checking table {table_name}: {e}")
        
        # Check if all required tables exist
        all_tables_exist = all(health_status["tables_exist"].values())
        health_status["healthy"] = all_tables_exist and len(health_status["errors"]) == 0
        
        if health_status["healthy"]:
            logger.info("Database health check passed")
        else:
            logger.warning(f"Database health check failed: {health_status['errors']}")
            
    except Exception as e:
        health_status["errors"].append(f"Database connection error: {e}")
        logger.error(f"Database health check failed: {e}")
    
    return health_status


def get_database_info(db_path: Optional[str] = None) -> dict:
    """Get detailed information about the database structure
    
    Args:
        db_path: Path to the database file. If None, uses default from config.
        
    Returns:
        Dictionary with database information
    """
    db_info = {
        "tables": {},
        "views": [],
        "indexes": []
    }
    
    try:
        # Use provided db_path or default connection
        if db_path:
            db_conn = DatabaseConnection(db_path)
        else:
            db_conn = db
        
        schema_manager = SchemaManager(db_conn)
        
        # Get table information
        tables = ["raw_ads_spend", "kpi_metrics"]
        for table_name in tables:
            if schema_manager.table_exists(table_name):
                try:
                    table_info = schema_manager.get_table_info(table_name)
                    row_count = schema_manager.get_table_row_count(table_name)
                    
                    db_info["tables"][table_name] = {
                        "columns": table_info,
                        "row_count": row_count
                    }
                except Exception as e:
                    logger.error(f"Error getting info for table {table_name}: {e}")
        
        # Get views information
        try:
            views_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_type = 'VIEW'
            """
            result = db_conn.execute_query(views_query)
            db_info["views"] = [row[0] for row in result.fetchall()]
        except Exception as e:
            logger.error(f"Error getting views information: {e}")
        
        logger.info("Retrieved database information successfully")
        
    except Exception as e:
        logger.error(f"Failed to get database information: {e}")
    
    return db_info


if __name__ == "__main__":
    # Configure logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database
    success = initialize_database()
    if success:
        print("Database initialized successfully!")
        
        # Print health check
        health = verify_database_health()
        print(f"Database health: {'✓ Healthy' if health['healthy'] else '✗ Unhealthy'}")
        
        # Print database info
        info = get_database_info()
        print(f"Tables created: {list(info['tables'].keys())}")
        print(f"Views created: {info['views']}")
    else:
        print("Database initialization failed!")
        exit(1)