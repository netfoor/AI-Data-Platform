"""
SQL query templates for KPI computation and analysis
"""
from typing import Dict, Optional, List
from datetime import date


class KPIQueries:
    """Collection of SQL queries for KPI computation and analysis"""
    
    @staticmethod
    def compute_daily_kpis(start_date: Optional[date] = None, 
                          end_date: Optional[date] = None) -> Dict[str, str]:
        """Generate SQL query for daily KPI computation
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Dictionary with query and parameters
        """
        query = """
        SELECT 
            date,
            platform,
            account,
            campaign,
            country,
            device,
            SUM(spend) as total_spend,
            SUM(conversions) as total_conversions,
            SUM(clicks) as total_clicks,
            SUM(impressions) as total_impressions,
            SUM(conversions) * 100 as revenue,
            CASE 
                WHEN SUM(conversions) > 0 THEN ROUND(SUM(spend) / SUM(conversions), 4)
                ELSE NULL 
            END as cac,
            CASE 
                WHEN SUM(spend) > 0 THEN ROUND((SUM(conversions) * 100) / SUM(spend), 4)
                ELSE NULL 
            END as roas,
            CURRENT_TIMESTAMP as created_at
        FROM raw_ads_spend
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND date >= $start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= $end_date"
            params['end_date'] = end_date
        
        query += """
        GROUP BY date, platform, account, campaign, country, device
        ORDER BY date DESC, platform, account, campaign
        """
        
        return {'query': query, 'params': params}
    
    @staticmethod
    def compute_platform_kpis(start_date: Optional[date] = None,
                             end_date: Optional[date] = None) -> Dict[str, str]:
        """Generate SQL query for platform-level KPI computation
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Dictionary with query and parameters
        """
        query = """
        SELECT 
            date,
            platform,
            'ALL' as account,
            'ALL' as campaign,
            'ALL' as country,
            'ALL' as device,
            SUM(spend) as total_spend,
            SUM(conversions) as total_conversions,
            SUM(clicks) as total_clicks,
            SUM(impressions) as total_impressions,
            SUM(conversions) * 100 as revenue,
            CASE 
                WHEN SUM(conversions) > 0 THEN ROUND(SUM(spend) / SUM(conversions), 4)
                ELSE NULL 
            END as cac,
            CASE 
                WHEN SUM(spend) > 0 THEN ROUND((SUM(conversions) * 100) / SUM(spend), 4)
                ELSE NULL 
            END as roas,
            CURRENT_TIMESTAMP as created_at
        FROM raw_ads_spend
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND date >= $start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= $end_date"
            params['end_date'] = end_date
        
        query += """
        GROUP BY date, platform
        ORDER BY date DESC, platform
        """
        
        return {'query': query, 'params': params}
    
    @staticmethod
    def upsert_kpi_metrics() -> str:
        """Generate SQL query for upserting KPI metrics
        
        Returns:
            SQL upsert query string
        """
        return """
        INSERT OR REPLACE INTO kpi_metrics (
            date, platform, account, campaign, country, device,
            total_spend, total_conversions, cac, roas, revenue, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
    @staticmethod
    def get_kpi_metrics_by_period(start_date: Optional[date] = None,
                                 end_date: Optional[date] = None,
                                 platform: Optional[str] = None) -> Dict[str, str]:
        """Generate SQL query for retrieving KPI metrics by period
        
        Args:
            start_date: Start date filter
            end_date: End date filter
            platform: Platform filter
            
        Returns:
            Dictionary with query and parameters
        """
        query = """
        SELECT 
            date,
            platform,
            account,
            campaign,
            country,
            device,
            total_spend,
            total_conversions,
            cac,
            roas,
            revenue,
            created_at
        FROM kpi_metrics
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND date >= $start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= $end_date"
            params['end_date'] = end_date
        
        if platform:
            query += " AND platform = $platform"
            params['platform'] = platform
        
        query += " ORDER BY date DESC, platform, account, campaign"
        
        return {'query': query, 'params': params}
    
    @staticmethod
    def aggregate_kpis_by_dimensions(dimensions: List[str],
                                   start_date: Optional[date] = None,
                                   end_date: Optional[date] = None) -> Dict[str, str]:
        """Generate SQL query for aggregating KPIs by custom dimensions
        
        Args:
            dimensions: List of dimensions to group by
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            Dictionary with query and parameters
        """
        valid_dimensions = {'date', 'platform', 'account', 'campaign', 'country', 'device'}
        dimensions = [dim for dim in dimensions if dim in valid_dimensions]
        
        if not dimensions:
            dimensions = ['date', 'platform']
        
        dimension_columns = ', '.join(dimensions)
        group_by_clause = ', '.join(dimensions)
        
        query = f"""
        SELECT 
            {dimension_columns},
            SUM(total_spend) as total_spend,
            SUM(total_conversions) as total_conversions,
            SUM(revenue) as revenue,
            CASE 
                WHEN SUM(total_conversions) > 0 THEN ROUND(SUM(total_spend) / SUM(total_conversions), 4)
                ELSE NULL 
            END as cac,
            CASE 
                WHEN SUM(total_spend) > 0 THEN ROUND(SUM(revenue) / SUM(total_spend), 4)
                ELSE NULL 
            END as roas
        FROM kpi_metrics
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND date >= $start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= $end_date"
            params['end_date'] = end_date
        
        query += f" GROUP BY {group_by_clause} ORDER BY {group_by_clause}"
        
        return {'query': query, 'params': params}
    
    @staticmethod
    def validate_kpi_calculations() -> str:
        """Generate SQL query for validating KPI calculations against raw data
        
        Returns:
            SQL validation query string
        """
        return """
        WITH raw_aggregated AS (
            SELECT 
                date, platform, account, campaign, country, device,
                SUM(spend) as raw_spend,
                SUM(conversions) as raw_conversions,
                SUM(conversions) * 100 as raw_revenue,
                CASE 
                    WHEN SUM(conversions) > 0 THEN ROUND(SUM(spend) / SUM(conversions), 4)
                    ELSE NULL 
                END as raw_cac,
                CASE 
                    WHEN SUM(spend) > 0 THEN ROUND((SUM(conversions) * 100) / SUM(spend), 4)
                    ELSE NULL 
                END as raw_roas
            FROM raw_ads_spend
            GROUP BY date, platform, account, campaign, country, device
        ),
        kpi_stored AS (
            SELECT 
                date, platform, account, campaign, country, device,
                total_spend as kpi_spend,
                total_conversions as kpi_conversions,
                revenue as kpi_revenue,
                cac as kpi_cac,
                roas as kpi_roas
            FROM kpi_metrics
        )
        SELECT 
            r.date, r.platform, r.account, r.campaign, r.country, r.device,
            r.raw_spend, k.kpi_spend,
            r.raw_conversions, k.kpi_conversions,
            r.raw_revenue, k.kpi_revenue,
            r.raw_cac, k.kpi_cac,
            r.raw_roas, k.kpi_roas,
            ABS(r.raw_spend - COALESCE(k.kpi_spend, 0)) as spend_diff,
            ABS(r.raw_conversions - COALESCE(k.kpi_conversions, 0)) as conversions_diff,
            ABS(COALESCE(r.raw_cac, 0) - COALESCE(k.kpi_cac, 0)) as cac_diff,
            ABS(COALESCE(r.raw_roas, 0) - COALESCE(k.kpi_roas, 0)) as roas_diff
        FROM raw_aggregated r
        LEFT JOIN kpi_stored k ON (
            r.date = k.date AND 
            r.platform = k.platform AND 
            r.account = k.account AND 
            r.campaign = k.campaign AND 
            r.country = k.country AND 
            r.device = k.device
        )
        WHERE (
            ABS(r.raw_spend - COALESCE(k.kpi_spend, 0)) > 0.01 OR
            ABS(r.raw_conversions - COALESCE(k.kpi_conversions, 0)) > 0 OR
            ABS(COALESCE(r.raw_cac, 0) - COALESCE(k.kpi_cac, 0)) > 0.0001 OR
            ABS(COALESCE(r.raw_roas, 0) - COALESCE(k.kpi_roas, 0)) > 0.0001
        )
        ORDER BY r.date DESC, r.platform, r.account
        """
    
    @staticmethod
    def get_kpi_summary_stats() -> str:
        """Generate SQL query for KPI summary statistics
        
        Returns:
            SQL summary statistics query string
        """
        return """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT date) as unique_dates,
            COUNT(DISTINCT platform) as unique_platforms,
            COUNT(DISTINCT account) as unique_accounts,
            COUNT(DISTINCT campaign) as unique_campaigns,
            MIN(date) as earliest_date,
            MAX(date) as latest_date,
            SUM(total_spend) as total_spend,
            SUM(total_conversions) as total_conversions,
            SUM(revenue) as total_revenue,
            AVG(cac) as avg_cac,
            AVG(roas) as avg_roas,
            COUNT(CASE WHEN cac IS NULL THEN 1 END) as null_cac_count,
            COUNT(CASE WHEN roas IS NULL THEN 1 END) as null_roas_count,
            MIN(created_at) as first_computation,
            MAX(created_at) as last_computation
        FROM kpi_metrics
        """
    
    @staticmethod
    def delete_kpi_metrics_by_date(start_date: date, end_date: date) -> Dict[str, str]:
        """Generate SQL query for deleting KPI metrics by date range
        
        Args:
            start_date: Start date for deletion
            end_date: End date for deletion
            
        Returns:
            Dictionary with query and parameters
        """
        query = """
        DELETE FROM kpi_metrics 
        WHERE date >= $start_date AND date <= $end_date
        """
        
        params = {
            'start_date': start_date,
            'end_date': end_date
        }
        
        return {'query': query, 'params': params}