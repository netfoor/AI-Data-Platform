"""
Database schema creation and management for DuckDB
"""
import logging
from typing import List, Optional

from .connection import DatabaseConnection

logger = logging.getLogger(__name__)


class SchemaManager:
    """Manages database schema creation and updates"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """Initialize schema manager
        
        Args:
            db_connection: Database connection instance. If None, uses global instance.
        """
        self.db = db_connection or DatabaseConnection()
    
    def create_raw_ads_spend_table(self) -> None:
        """Create the raw_ads_spend table for storing ingested advertising data"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS raw_ads_spend (
            date DATE NOT NULL,
            platform VARCHAR(20) NOT NULL,
            account VARCHAR(50) NOT NULL,
            campaign VARCHAR(100) NOT NULL,
            country VARCHAR(3) NOT NULL,
            device VARCHAR(20) NOT NULL,
            spend DECIMAL(10,2) NOT NULL CHECK (spend >= 0),
            clicks INTEGER NOT NULL CHECK (clicks >= 0),
            impressions INTEGER NOT NULL CHECK (impressions >= 0),
            conversions INTEGER NOT NULL CHECK (conversions >= 0),
            load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            source_file_name VARCHAR(255) NOT NULL,
            batch_id VARCHAR(100) NOT NULL,
            
            -- Constraints
            CHECK (clicks <= impressions),
            CHECK (platform IN ('Meta', 'Google')),
            CHECK (device IN ('Desktop', 'Mobile')),
            CHECK (country IN ('US', 'CA', 'BR', 'MX'))
        );
        """
        
        try:
            self.db.execute_query(create_table_sql)
            logger.info("Created raw_ads_spend table successfully")
        except Exception as e:
            logger.error(f"Failed to create raw_ads_spend table: {e}")
            raise
    
    def create_kpi_metrics_table(self) -> None:
        """Create the kpi_metrics table for storing computed KPI metrics"""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS kpi_metrics (
            date DATE NOT NULL,
            platform VARCHAR(20) NOT NULL,
            account VARCHAR(50) NOT NULL,
            campaign VARCHAR(100) NOT NULL,
            country VARCHAR(3) NOT NULL,
            device VARCHAR(20) NOT NULL,
            total_spend DECIMAL(10,2) NOT NULL CHECK (total_spend >= 0),
            total_conversions INTEGER NOT NULL CHECK (total_conversions >= 0),
            cac DECIMAL(10,4) CHECK (cac >= 0),  -- Can be NULL for division by zero
            roas DECIMAL(10,4) CHECK (roas >= 0),  -- Can be NULL for division by zero
            revenue DECIMAL(10,2) NOT NULL CHECK (revenue >= 0),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Constraints
            CHECK (platform IN ('Meta', 'Google', 'ALL')),
            CHECK (device IN ('Desktop', 'Mobile', 'ALL')),
            CHECK (country IN ('US', 'CA', 'BR', 'MX', 'ALL')),
            
            -- Primary key to prevent duplicates
            PRIMARY KEY (date, platform, account, campaign, country, device)
        );
        """
        
        try:
            self.db.execute_query(create_table_sql)
            logger.info("Created kpi_metrics table successfully")
        except Exception as e:
            logger.error(f"Failed to create kpi_metrics table: {e}")
            raise
    
    def create_indexes(self) -> None:
        """Create indexes for better query performance"""
        indexes = [
            # Indexes for raw_ads_spend table
            "CREATE INDEX IF NOT EXISTS idx_raw_ads_spend_date ON raw_ads_spend(date);",
            "CREATE INDEX IF NOT EXISTS idx_raw_ads_spend_platform ON raw_ads_spend(platform);",
            "CREATE INDEX IF NOT EXISTS idx_raw_ads_spend_batch_id ON raw_ads_spend(batch_id);",
            "CREATE INDEX IF NOT EXISTS idx_raw_ads_spend_load_date ON raw_ads_spend(load_date);",
            "CREATE INDEX IF NOT EXISTS idx_raw_ads_spend_composite ON raw_ads_spend(date, platform, account);",
            
            # Indexes for kpi_metrics table
            "CREATE INDEX IF NOT EXISTS idx_kpi_metrics_date ON kpi_metrics(date);",
            "CREATE INDEX IF NOT EXISTS idx_kpi_metrics_platform ON kpi_metrics(platform);",
            "CREATE INDEX IF NOT EXISTS idx_kpi_metrics_created_at ON kpi_metrics(created_at);",
        ]
        
        for index_sql in indexes:
            try:
                self.db.execute_query(index_sql)
                logger.debug(f"Created index: {index_sql.split('idx_')[1].split(' ')[0]}")
            except Exception as e:
                logger.error(f"Failed to create index: {e}")
                logger.error(f"Index SQL: {index_sql}")
                raise
        
        logger.info("Created all database indexes successfully")
    
    def create_views(self) -> None:
        """Create useful views for data analysis"""
        views = [
            # Daily aggregated metrics view
            """
            CREATE OR REPLACE VIEW daily_metrics AS
            SELECT 
                date,
                platform,
                SUM(spend) as total_spend,
                SUM(clicks) as total_clicks,
                SUM(impressions) as total_impressions,
                SUM(conversions) as total_conversions,
                CASE 
                    WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                    ELSE NULL 
                END as cac,
                CASE 
                    WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100) / SUM(spend)
                    ELSE NULL 
                END as roas,
                SUM(conversions) * 100 as revenue
            FROM raw_ads_spend
            GROUP BY date, platform
            ORDER BY date DESC, platform;
            """,
            
            # Platform performance comparison view
            """
            CREATE OR REPLACE VIEW platform_performance AS
            SELECT 
                platform,
                COUNT(DISTINCT date) as active_days,
                SUM(spend) as total_spend,
                SUM(conversions) as total_conversions,
                AVG(CASE 
                    WHEN conversions > 0 THEN spend / conversions
                    ELSE NULL 
                END) as avg_cac,
                AVG(CASE 
                    WHEN spend > 0 THEN (conversions * 100) / spend
                    ELSE NULL 
                END) as avg_roas,
                MIN(date) as first_activity,
                MAX(date) as last_activity
            FROM raw_ads_spend
            GROUP BY platform
            ORDER BY total_spend DESC;
            """,
            
            # Recent data quality view
            """
            CREATE OR REPLACE VIEW data_quality_summary AS
            SELECT 
                batch_id,
                source_file_name,
                load_date,
                COUNT(*) as record_count,
                COUNT(CASE WHEN spend = 0 THEN 1 END) as zero_spend_records,
                COUNT(CASE WHEN conversions = 0 THEN 1 END) as zero_conversion_records,
                COUNT(CASE WHEN clicks > impressions THEN 1 END) as invalid_click_records,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM raw_ads_spend
            GROUP BY batch_id, source_file_name, load_date
            ORDER BY load_date DESC;
            """
        ]
        
        for view_sql in views:
            try:
                self.db.execute_query(view_sql)
                view_name = view_sql.split('VIEW ')[1].split(' AS')[0]
                logger.debug(f"Created view: {view_name}")
            except Exception as e:
                logger.error(f"Failed to create view: {e}")
                logger.error(f"View SQL: {view_sql[:100]}...")
                raise
        
        logger.info("Created all database views successfully")
    
    def drop_table(self, table_name: str) -> None:
        """Drop a table if it exists
        
        Args:
            table_name: Name of the table to drop
        """
        drop_sql = f"DROP TABLE IF EXISTS {table_name};"
        try:
            self.db.execute_query(drop_sql)
            logger.info(f"Dropped table: {table_name}")
        except Exception as e:
            logger.error(f"Failed to drop table {table_name}: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> List[dict]:
        """Get information about a table's structure
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of column information dictionaries
        """
        info_sql = f"DESCRIBE {table_name};"
        try:
            result = self.db.execute_query(info_sql)
            return result.fetchall()
        except Exception as e:
            logger.error(f"Failed to get table info for {table_name}: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        return self.db.table_exists(table_name)
    
    def get_table_row_count(self, table_name: str) -> int:
        """Get the number of rows in a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Number of rows in the table
        """
        count_sql = f"SELECT COUNT(*) FROM {table_name};"
        try:
            result = self.db.execute_query(count_sql)
            return result.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to get row count for {table_name}: {e}")
            raise