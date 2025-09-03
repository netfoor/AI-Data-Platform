"""
Parameterized SQL Query Interface for AI Data Platform
Provides predefined SQL templates and execution utilities for common analytics queries
"""
import logging
from datetime import date, datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass

from ..database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

@dataclass
class QueryResult:
    """Result of a SQL query execution"""
    data: List[Dict[str, Any]]
    row_count: int
    execution_time: float
    query: str
    parameters: Dict[str, Any]
    success: bool = True
    error_message: Optional[str] = None

class SQLQueryInterface:
    """Interface for executing parameterized SQL queries with predefined templates"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """Initialize SQL query interface
        
        Args:
            db_connection: Database connection instance. If None, uses global instance.
        """
        self.db = db_connection or DatabaseConnection()
        self._query_templates = self._initialize_query_templates()
    
    def _initialize_query_templates(self) -> Dict[str, str]:
        """Initialize predefined SQL query templates"""
        return {
            # Basic metrics queries
            "daily_metrics": """
                SELECT 
                    date,
                    SUM(spend) as total_spend,
                    SUM(conversions) as total_conversions,
                    SUM(clicks) as total_clicks,
                    SUM(impressions) as total_impressions,
                    CASE 
                        WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                        ELSE NULL 
                    END as cac,
                    CASE 
                        WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                        ELSE NULL 
                    END as roas
                FROM raw_ads_spend 
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date DESC
            """,
            
            "platform_performance": """
                SELECT 
                    platform,
                    SUM(spend) as total_spend,
                    SUM(conversions) as total_conversions,
                    SUM(conversions) * 100 as total_revenue,
                    CASE 
                        WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                        ELSE NULL 
                    END as cac,
                    CASE 
                        WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                        ELSE NULL 
                    END as roas,
                    COUNT(DISTINCT date) as days_with_data,
                    AVG(spend) as avg_daily_spend,
                    AVG(conversions) as avg_daily_conversions
                FROM raw_ads_spend 
                WHERE date BETWEEN ? AND ?
                GROUP BY platform
                ORDER BY total_spend DESC
            """,
            
            "campaign_analysis": """
                SELECT 
                    campaign,
                    platform,
                    SUM(spend) as total_spend,
                    SUM(conversions) as total_conversions,
                    SUM(conversions) * 100 as total_revenue,
                    CASE 
                        WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                        ELSE NULL 
                    END as cac,
                    CASE 
                        WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                        ELSE NULL 
                    END as roas,
                    COUNT(DISTINCT date) as days_with_data
                FROM raw_ads_spend 
                WHERE date BETWEEN ? AND ?
                GROUP BY campaign, platform
                ORDER BY total_spend DESC
            """,
            
            "country_performance": """
                SELECT 
                    country,
                    SUM(spend) as total_spend,
                    SUM(conversions) as total_conversions,
                    SUM(conversions) * 100 as total_revenue,
                    CASE 
                        WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                        ELSE NULL 
                    END as cac,
                    CASE 
                        WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                        ELSE NULL 
                    END as roas,
                    COUNT(DISTINCT date) as days_with_data
                FROM raw_ads_spend 
                WHERE date BETWEEN ? AND ?
                GROUP BY country
                ORDER BY total_spend DESC
            """,
            
            "device_performance": """
                SELECT 
                    device,
                    SUM(spend) as total_spend,
                    SUM(conversions) as total_conversions,
                    SUM(conversions) * 100 as total_revenue,
                    CASE 
                        WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                        ELSE NULL 
                    END as cac,
                    CASE 
                        WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                        ELSE NULL 
                    END as roas,
                    COUNT(DISTINCT date) as days_with_data
                FROM raw_ads_spend 
                WHERE date BETWEEN ? AND ?
                GROUP BY device
                ORDER BY total_spend DESC
            """,
            
            "account_summary": """
                SELECT 
                    account,
                    SUM(spend) as total_spend,
                    SUM(conversions) as total_conversions,
                    SUM(conversions) * 100 as total_revenue,
                    CASE 
                        WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                        ELSE NULL 
                    END as cac,
                    CASE 
                        WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                        ELSE NULL 
                    END as roas,
                    COUNT(DISTINCT date) as days_with_data,
                    COUNT(DISTINCT campaign) as campaign_count,
                    COUNT(DISTINCT platform) as platform_count
                FROM raw_ads_spend 
                WHERE date BETWEEN ? AND ?
                GROUP BY account
                ORDER BY total_spend DESC
            """,
            
            "period_comparison": """
                WITH current_period AS (
                    SELECT 
                        SUM(spend) as current_spend,
                        SUM(conversions) as current_conversions,
                        CASE 
                            WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                            ELSE NULL 
                        END as current_cac,
                        CASE 
                            WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                            ELSE NULL 
                        END as current_roas
                    FROM raw_ads_spend 
                    WHERE date BETWEEN ? AND ?
                ),
                previous_period AS (
                    SELECT 
                        SUM(spend) as previous_spend,
                        SUM(conversions) as previous_conversions,
                        CASE 
                            WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                            ELSE NULL 
                        END as previous_cac,
                        CASE 
                            WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                            ELSE NULL 
                        END as previous_roas
                    FROM raw_ads_spend 
                    WHERE date BETWEEN ? AND ?
                )
                SELECT 
                    c.current_spend,
                    c.current_conversions,
                    c.current_cac,
                    c.current_roas,
                    p.previous_spend,
                    p.previous_conversions,
                    p.previous_cac,
                    p.previous_roas,
                    CASE 
                        WHEN p.previous_spend > 0 THEN ((c.current_spend - p.previous_spend) / p.previous_spend) * 100
                        ELSE NULL 
                    END as spend_change_percent,
                    CASE 
                        WHEN p.previous_conversions > 0 THEN ((c.current_conversions - p.previous_conversions) / p.previous_conversions) * 100
                        ELSE NULL 
                    END as conversions_change_percent,
                    CASE 
                        WHEN p.previous_cac IS NOT NULL AND c.current_cac IS NOT NULL THEN ((c.current_cac - p.previous_cac) / p.previous_cac) * 100
                        ELSE NULL 
                    END as cac_change_percent,
                    CASE 
                        WHEN p.previous_roas IS NOT NULL AND c.current_roas IS NOT NULL THEN ((c.current_roas - p.previous_roas) / p.previous_roas) * 100
                        ELSE NULL 
                    END as roas_change_percent
                FROM current_period c
                CROSS JOIN previous_period p
            """,
            
            "trend_analysis": """
                SELECT 
                    date,
                    SUM(spend) as daily_spend,
                    SUM(conversions) as daily_conversions,
                    SUM(conversions) * 100 as daily_revenue,
                    CASE 
                        WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                        ELSE NULL 
                    END as daily_cac,
                    CASE 
                        WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                        ELSE NULL 
                    END as daily_roas,
                    AVG(SUM(spend)) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7d_spend,
                    AVG(SUM(conversions)) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7d_conversions
                FROM raw_ads_spend 
                WHERE date BETWEEN ? AND ?
                GROUP BY date
                ORDER BY date DESC
            """
        }
    
    def get_available_queries(self) -> List[str]:
        """Get list of available predefined query names"""
        return list(self._query_templates.keys())
    
    def get_query_template(self, query_name: str) -> Optional[str]:
        """Get a specific query template by name"""
        return self._query_templates.get(query_name)
    
    def execute_predefined_query(self, query_name: str, parameters: Dict[str, Any]) -> QueryResult:
        """Execute a predefined query with parameters
        
        Args:
            query_name: Name of the predefined query to execute
            parameters: Dictionary of parameters for the query
            
        Returns:
            QueryResult with execution results
        """
        if query_name not in self._query_templates:
            return QueryResult(
                data=[],
                row_count=0,
                execution_time=0.0,
                query="",
                parameters=parameters,
                success=False,
                error_message=f"Unknown query: {query_name}"
            )
        
        query_template = self._query_templates[query_name]
        return self.execute_custom_query(query_template, parameters)
    
    def execute_custom_query(self, query: str, parameters: Dict[str, Any]) -> QueryResult:
        """Execute a custom SQL query with parameters
        
        Args:
            query: SQL query string
            parameters: Dictionary of parameters for the query
            
        Returns:
            QueryResult with execution results
        """
        import time
        start_time = time.time()
        
        try:
            # Convert parameters to positional format for DuckDB
            param_list = self._convert_parameters_to_positional(query, parameters)
            
            # Execute the query
            result = self.db.execute_query(query, param_list)
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            if result.description:
                column_names = [desc[0] for desc in result.description]
                data = [dict(zip(column_names, row)) for row in rows]
            else:
                data = []
            
            execution_time = time.time() - start_time
            
            return QueryResult(
                data=data,
                row_count=len(data),
                execution_time=execution_time,
                query=query,
                parameters=parameters,
                success=True
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Query execution failed: {e}")
            
            return QueryResult(
                data=[],
                row_count=0,
                execution_time=execution_time,
                query=query,
                parameters=parameters,
                success=False,
                error_message=str(e)
            )
    
    def _convert_parameters_to_positional(self, query: str, parameters: Dict[str, Any]) -> List[Any]:
        """Convert named parameters to positional parameters for DuckDB
        
        Args:
            query: SQL query string
            parameters: Dictionary of named parameters
            
        Returns:
            List of positional parameters in order of appearance in query
        """
        # For now, we'll use a simple approach with positional parameters
        # In a more sophisticated implementation, we could parse the query
        # and map named parameters to positions
        
        # Extract date parameters for common queries
        param_list = []
        
        if 'start_date' in parameters:
            param_list.append(parameters['start_date'])
        if 'end_date' in parameters:
            param_list.append(parameters['end_date'])
        if 'previous_start_date' in parameters:
            param_list.append(parameters['previous_start_date'])
        if 'previous_end_date' in parameters:
            param_list.append(parameters['previous_end_date'])
        
        return param_list
    
    def format_query_result(self, result: QueryResult, format_type: str = "table") -> str:
        """Format query results for display
        
        Args:
            result: QueryResult to format
            format_type: Type of formatting ("table", "json", "summary")
            
        Returns:
            Formatted string representation
        """
        if not result.success:
            return f"❌ Query failed: {result.error_message}"
        
        if result.row_count == 0:
            return "📊 No data returned from query"
        
        if format_type == "json":
            import json
            return json.dumps(result.data, indent=2, default=str)
        
        elif format_type == "summary":
            return self._format_summary(result)
        
        else:  # table format
            return self._format_table(result)
    
    def _format_summary(self, result: QueryResult) -> str:
        """Format results as a summary"""
        if result.row_count == 0:
            return "No data available"
        
        summary_parts = [f"📊 Query Results Summary:"]
        summary_parts.append(f"   • Rows returned: {result.row_count}")
        summary_parts.append(f"   • Execution time: {result.execution_time:.3f}s")
        
        # Add sample data if available
        if result.data:
            sample = result.data[0]
            summary_parts.append(f"   • Sample row keys: {', '.join(sample.keys())}")
        
        return "\n".join(summary_parts)
    
    def _format_table(self, result: QueryResult) -> str:
        """Format results as a table"""
        if result.row_count == 0:
            return "No data available"
        
        if not result.data:
            return "No data available"
        
        # Get column names from first row
        columns = list(result.data[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = max(
                len(str(col)),
                max(len(str(row.get(col, ''))) for row in result.data[:10])  # Limit to first 10 rows for width calculation
            )
        
        # Build table header
        table_lines = []
        
        # Header separator
        header_sep = "+" + "+".join("-" * (width + 2) for width in col_widths.values()) + "+"
        table_lines.append(header_sep)
        
        # Header row
        header_row = "|" + "|".join(f" {col:^{col_widths[col]}} " for col in columns) + "|"
        table_lines.append(header_row)
        table_lines.append(header_sep)
        
        # Data rows (limit to first 20 for display)
        for i, row in enumerate(result.data[:20]):
            data_row = "|" + "|".join(
                f" {str(row.get(col, '')):^{col_widths[col]}} " for col in columns
            ) + "|"
            table_lines.append(data_row)
        
        # Footer separator
        table_lines.append(header_sep)
        
        # Add row count info
        if result.row_count > 20:
            table_lines.append(f"Showing first 20 of {result.row_count} rows")
        
        return "\n".join(table_lines)
    
    def get_query_help(self, query_name: Optional[str] = None) -> str:
        """Get help information for queries
        
        Args:
            query_name: Specific query name, or None for all queries
            
        Returns:
            Help text string
        """
        if query_name:
            if query_name not in self._query_templates:
                return f"❌ Unknown query: {query_name}"
            
            return self._get_single_query_help(query_name)
        
        # Return help for all queries
        help_text = ["🔍 Available Predefined Queries:"]
        help_text.append("=" * 50)
        
        for name in self._query_templates.keys():
            help_text.append(f"• {name}")
        
        help_text.append("\n💡 Usage:")
        help_text.append("  result = interface.execute_predefined_query('query_name', parameters)")
        help_text.append("\n📖 For detailed help on a specific query:")
        help_text.append("  help_text = interface.get_query_help('query_name')")
        
        return "\n".join(help_text)
    
    def _get_single_query_help(self, query_name: str) -> str:
        """Get help for a specific query"""
        help_info = {
            "daily_metrics": {
                "description": "Get daily performance metrics including CAC and ROAS",
                "parameters": ["start_date", "end_date"],
                "returns": "Daily spend, conversions, CAC, ROAS, clicks, impressions"
            },
            "platform_performance": {
                "description": "Compare performance across different advertising platforms",
                "parameters": ["start_date", "end_date"],
                "returns": "Platform-level metrics with CAC, ROAS, and averages"
            },
            "campaign_analysis": {
                "description": "Analyze performance by campaign and platform",
                "parameters": ["start_date", "end_date"],
                "returns": "Campaign metrics broken down by platform"
            },
            "country_performance": {
                "description": "Geographic performance analysis by country",
                "parameters": ["start_date", "end_date"],
                "returns": "Country-level metrics with CAC and ROAS"
            },
            "device_performance": {
                "description": "Performance analysis by device type",
                "parameters": ["start_date", "end_date"],
                "returns": "Device-level metrics with CAC and ROAS"
            },
            "account_summary": {
                "description": "Account-level performance summary",
                "parameters": ["start_date", "end_date"],
                "returns": "Account metrics with campaign and platform counts"
            },
            "period_comparison": {
                "description": "Compare two time periods side by side",
                "parameters": ["start_date", "end_date", "previous_start_date", "previous_end_date"],
                "returns": "Period comparison with percentage changes"
            },
            "trend_analysis": {
                "description": "Time series analysis with rolling averages",
                "parameters": ["start_date", "end_date"],
                "returns": "Daily trends with 7-day rolling averages"
            }
        }
        
        if query_name not in help_info:
            return f"❌ No help available for: {query_name}"
        
        info = help_info[query_name]
        help_text = [
            f"🔍 Query: {query_name}",
            f"📝 Description: {info['description']}",
            f"📊 Parameters: {', '.join(info['parameters'])}",
            f"📈 Returns: {info['returns']}",
            "",
            "💡 Example:",
            f"  parameters = {{'start_date': '2025-06-01', 'end_date': '2025-06-30'}}",
            f"  result = interface.execute_predefined_query('{query_name}', parameters)"
        ]
        
        return "\n".join(help_text)

# Global instance
sql_interface = SQLQueryInterface()