"""
DuckDB insertion functions with error handling for data ingestion
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from ..database.connection import db
from ..models.ads_spend import AdsSpendRecordWithMetadata

logger = logging.getLogger(__name__)


class DatabaseLoader:
    """Handles loading data into DuckDB with error handling and retry logic"""
    
    def __init__(self):
        """Initialize database loader"""
        self.db = db
        logger.info("Initialized database loader")
    
    def ensure_tables_exist(self) -> None:
        """Ensure required tables exist in the database"""
        logger.info("Ensuring database tables exist")
        
        # Create raw_ads_spend table
        create_raw_table_sql = """
        CREATE TABLE IF NOT EXISTS raw_ads_spend (
            date DATE NOT NULL,
            platform VARCHAR NOT NULL,
            account VARCHAR NOT NULL,
            campaign VARCHAR NOT NULL,
            country VARCHAR NOT NULL,
            device VARCHAR NOT NULL,
            spend DECIMAL(10,2) NOT NULL,
            clicks INTEGER NOT NULL,
            impressions INTEGER NOT NULL,
            conversions INTEGER NOT NULL,
            load_date TIMESTAMP NOT NULL,
            source_file_name VARCHAR NOT NULL,
            batch_id VARCHAR NOT NULL
        );
        """
        
        # Create index for better query performance
        create_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_raw_ads_spend_date_platform 
        ON raw_ads_spend (date, platform);
        """
        
        create_batch_index_sql = """
        CREATE INDEX IF NOT EXISTS idx_raw_ads_spend_batch_id 
        ON raw_ads_spend (batch_id);
        """
        
        try:
            self.db.execute_query(create_raw_table_sql)
            self.db.execute_query(create_index_sql)
            self.db.execute_query(create_batch_index_sql)
            logger.info("Database tables and indexes created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def insert_records(self, records: List[AdsSpendRecordWithMetadata]) -> Tuple[int, int, List[str]]:
        """Insert records into the database with error handling
        
        Args:
            records: List of AdsSpendRecordWithMetadata to insert
            
        Returns:
            Tuple of (successful_inserts, failed_inserts, error_messages)
        """
        if not records:
            logger.warning("No records provided for insertion")
            return 0, 0, []
        
        logger.info(f"Starting insertion of {len(records)} records")
        
        # Ensure tables exist
        self.ensure_tables_exist()
        
        successful_inserts = 0
        failed_inserts = 0
        error_messages = []
        
        # Prepare insert statement
        insert_sql = """
        INSERT INTO raw_ads_spend (
            date, platform, account, campaign, country, device,
            spend, clicks, impressions, conversions,
            load_date, source_file_name, batch_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # Convert records to parameter tuples
        insert_params = []
        for record in records:
            try:
                params = (
                    record.date,
                    record.platform,
                    record.account,
                    record.campaign,
                    record.country,
                    record.device,
                    float(record.spend),  # Convert Decimal to float for DuckDB
                    record.clicks,
                    record.impressions,
                    record.conversions,
                    record.load_date,
                    record.source_file_name,
                    record.batch_id
                )
                insert_params.append(params)
            except Exception as e:
                failed_inserts += 1
                error_msg = f"Error preparing record for insertion: {e}"
                error_messages.append(error_msg)
                logger.error(error_msg)
        
        # Batch insert with error handling
        if insert_params:
            try:
                with self.db.get_connection() as conn:
                    conn.executemany(insert_sql, insert_params)
                    successful_inserts = len(insert_params)
                    logger.info(f"Successfully inserted {successful_inserts} records")
                    
            except Exception as e:
                # If batch insert fails, try individual inserts
                logger.warning(f"Batch insert failed: {e}. Attempting individual inserts...")
                successful_inserts, individual_failures, individual_errors = self._insert_individually(
                    insert_sql, insert_params
                )
                failed_inserts += individual_failures
                error_messages.extend(individual_errors)
        
        total_processed = successful_inserts + failed_inserts
        success_rate = (successful_inserts / total_processed * 100) if total_processed > 0 else 0
        
        logger.info(
            f"Insertion completed: {successful_inserts} successful, {failed_inserts} failed "
            f"({success_rate:.1f}% success rate)"
        )
        
        return successful_inserts, failed_inserts, error_messages
    
    def _insert_individually(self, insert_sql: str, insert_params: List[tuple]) -> Tuple[int, int, List[str]]:
        """Insert records individually when batch insert fails
        
        Args:
            insert_sql: SQL insert statement
            insert_params: List of parameter tuples
            
        Returns:
            Tuple of (successful_inserts, failed_inserts, error_messages)
        """
        successful = 0
        failed = 0
        errors = []
        
        for i, params in enumerate(insert_params):
            try:
                with self.db.get_connection() as conn:
                    conn.execute(insert_sql, params)
                    successful += 1
            except Exception as e:
                failed += 1
                error_msg = f"Failed to insert record {i+1}: {e}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        return successful, failed, errors
    
    def check_batch_exists(self, batch_id: str) -> bool:
        """Check if a batch has already been loaded
        
        Args:
            batch_id: Batch identifier to check
            
        Returns:
            True if batch exists, False otherwise
        """
        check_sql = "SELECT COUNT(*) FROM raw_ads_spend WHERE batch_id = ?"
        
        try:
            result = self.db.execute_query(check_sql, [batch_id])
            count = result.fetchone()[0]
            exists = count > 0
            
            if exists:
                logger.info(f"Batch {batch_id} already exists with {count} records")
            else:
                logger.debug(f"Batch {batch_id} does not exist")
                
            return exists
            
        except Exception as e:
            logger.error(f"Error checking batch existence: {e}")
            return False
    
    def get_batch_info(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a loaded batch
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Dictionary with batch information or None if not found
        """
        info_sql = """
        SELECT 
            batch_id,
            source_file_name,
            MIN(load_date) as first_load_date,
            MAX(load_date) as last_load_date,
            COUNT(*) as record_count,
            MIN(date) as earliest_data_date,
            MAX(date) as latest_data_date
        FROM raw_ads_spend 
        WHERE batch_id = ?
        GROUP BY batch_id, source_file_name
        """
        
        try:
            result = self.db.execute_query(info_sql, [batch_id])
            row = result.fetchone()
            
            if row:
                return {
                    'batch_id': row[0],
                    'source_file_name': row[1],
                    'first_load_date': row[2],
                    'last_load_date': row[3],
                    'record_count': row[4],
                    'earliest_data_date': row[5],
                    'latest_data_date': row[6]
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting batch info: {e}")
            return None
    
    def delete_batch(self, batch_id: str) -> int:
        """Delete all records for a specific batch
        
        Args:
            batch_id: Batch identifier to delete
            
        Returns:
            Number of records deleted
        """
        delete_sql = "DELETE FROM raw_ads_spend WHERE batch_id = ?"
        
        try:
            # First check how many records will be deleted
            count_sql = "SELECT COUNT(*) FROM raw_ads_spend WHERE batch_id = ?"
            result = self.db.execute_query(count_sql, [batch_id])
            record_count = result.fetchone()[0]
            
            if record_count == 0:
                logger.info(f"No records found for batch {batch_id}")
                return 0
            
            # Delete the records
            self.db.execute_query(delete_sql, [batch_id])
            logger.info(f"Deleted {record_count} records for batch {batch_id}")
            
            return record_count
            
        except Exception as e:
            logger.error(f"Error deleting batch {batch_id}: {e}")
            raise
    
    def get_table_stats(self) -> Dict[str, Any]:
        """Get statistics about the raw_ads_spend table
        
        Returns:
            Dictionary with table statistics
        """
        stats_sql = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT batch_id) as total_batches,
            COUNT(DISTINCT source_file_name) as total_source_files,
            MIN(date) as earliest_date,
            MAX(date) as latest_date,
            MIN(load_date) as first_load_date,
            MAX(load_date) as last_load_date
        FROM raw_ads_spend
        """
        
        try:
            result = self.db.execute_query(stats_sql)
            row = result.fetchone()
            
            if row:
                return {
                    'total_records': row[0],
                    'total_batches': row[1],
                    'total_source_files': row[2],
                    'earliest_date': row[3],
                    'latest_date': row[4],
                    'first_load_date': row[5],
                    'last_load_date': row[6]
                }
            else:
                return {
                    'total_records': 0,
                    'total_batches': 0,
                    'total_source_files': 0,
                    'earliest_date': None,
                    'latest_date': None,
                    'first_load_date': None,
                    'last_load_date': None
                }
                
        except Exception as e:
            logger.error(f"Error getting table stats: {e}")
            return {}


def create_database_loader() -> DatabaseLoader:
    """Factory function to create a database loader
    
    Returns:
        DatabaseLoader instance
    """
    return DatabaseLoader()