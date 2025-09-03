"""
DuckDB database connection utilities
"""
import duckdb
import logging
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

from ..config import settings

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages DuckDB database connections"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection
        
        Args:
            db_path: Path to DuckDB database file. If None, uses in-memory database.
        """
        self.db_path = db_path or settings.database.path
        self._connection: Optional[duckdb.DuckDBPyConnection] = None
        
    def connect(self) -> duckdb.DuckDBPyConnection:
        """Establish database connection"""
        if self._connection is None:
            try:
                # Ensure database directory exists
                if self.db_path != ":memory:":
                    db_file = Path(self.db_path)
                    db_file.parent.mkdir(parents=True, exist_ok=True)
                
                self._connection = duckdb.connect(self.db_path)
                logger.info(f"Connected to DuckDB database: {self.db_path}")
                
                # Configure DuckDB settings for better performance
                self._connection.execute("PRAGMA enable_progress_bar=false")
                self._connection.execute("PRAGMA threads=4")
                
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
                
        return self._connection
    
    def disconnect(self):
        """Close database connection"""
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = self.connect()
        try:
            yield conn
        finally:
            # Don't close the connection here as it might be reused
            pass
    
    def execute_query(self, query: str, parameters: Optional[dict] = None):
        """Execute a SQL query
        
        Args:
            query: SQL query string
            parameters: Optional query parameters (dict for named, tuple/list for positional)
            
        Returns:
            Query result
        """
        with self.get_connection() as conn:
            try:
                if parameters:
                    # Handle both named (dict) and positional (tuple/list) parameters
                    if isinstance(parameters, dict):
                        result = conn.execute(query, parameters)
                    else:
                        result = conn.execute(query, parameters)
                else:
                    result = conn.execute(query)
                logger.debug(f"Executed query: {query[:100]}...")
                return result
            except Exception as e:
                logger.error(f"Query execution failed: {e}")
                logger.error(f"Query: {query}")
                raise
    
    def execute_many(self, query: str, parameters_list: list) -> None:
        """Execute a query multiple times with different parameters
        
        Args:
            query: SQL query string
            parameters_list: List of parameter dictionaries
        """
        with self.get_connection() as conn:
            try:
                conn.executemany(query, parameters_list)
                logger.debug(f"Executed batch query with {len(parameters_list)} parameter sets")
            except Exception as e:
                logger.error(f"Batch query execution failed: {e}")
                raise
    
    def fetch_df(self, query: str, parameters: Optional[dict] = None):
        """Execute query and return results as pandas DataFrame
        
        Args:
            query: SQL query string
            parameters: Optional query parameters
            
        Returns:
            pandas DataFrame with query results
        """
        result = self.execute_query(query, parameters)
        return result.df()
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_name = ?
        """
        result = self.execute_query(query, [table_name])
        return result.fetchone()[0] > 0

# Global database connection instance
db = DatabaseConnection()