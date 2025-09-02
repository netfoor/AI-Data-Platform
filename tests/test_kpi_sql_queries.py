"""
Unit tests for KPI SQL query templates
"""
import pytest
from datetime import date

from ai_data_platform.analytics.sql_queries import KPIQueries


class TestKPIQueries:
    """Test cases for KPI SQL query templates"""
    
    def test_compute_daily_kpis_no_filters(self):
        """Test daily KPI computation query without date filters"""
        result = KPIQueries.compute_daily_kpis()
        
        query = result['query']
        params = result['params']
        
        # Check query structure
        assert "SELECT" in query
        assert "FROM raw_ads_spend" in query
        assert "GROUP BY date, platform, account, campaign, country, device" in query
        assert "SUM(spend) as total_spend" in query
        assert "SUM(conversions) as total_conversions" in query
        assert "WHEN SUM(conversions) > 0" in query  # CAC calculation
        assert "WHEN SUM(spend) > 0" in query        # ROAS calculation
        
        # No date filters should be applied
        assert "$start_date" not in query
        assert "$end_date" not in query
        assert len(params) == 0
    
    def test_compute_daily_kpis_with_date_filters(self):
        """Test daily KPI computation query with date filters"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        result = KPIQueries.compute_daily_kpis(start_date, end_date)
        
        query = result['query']
        params = result['params']
        
        # Check date filters are applied
        assert "date >= $start_date" in query
        assert "date <= $end_date" in query
        assert params['start_date'] == start_date
        assert params['end_date'] == end_date
    
    def test_compute_platform_kpis(self):
        """Test platform-level KPI computation query"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        result = KPIQueries.compute_platform_kpis(start_date, end_date)
        
        query = result['query']
        params = result['params']
        
        # Check aggregation level
        assert "'ALL' as account" in query
        assert "'ALL' as campaign" in query
        assert "'ALL' as country" in query
        assert "'ALL' as device" in query
        assert "GROUP BY date, platform" in query
        
        # Check date filters
        assert "date >= $start_date" in query
        assert "date <= $end_date" in query
        assert params['start_date'] == start_date
        assert params['end_date'] == end_date
    
    def test_upsert_kpi_metrics(self):
        """Test KPI metrics upsert query"""
        query = KPIQueries.upsert_kpi_metrics()
        
        assert "INSERT OR REPLACE INTO kpi_metrics" in query
        assert "date, platform, account, campaign, country, device" in query
        assert "total_spend, total_conversions, cac, roas, revenue, created_at" in query
        assert query.count("?") == 12  # Should have 12 parameter placeholders
    
    def test_get_kpi_metrics_by_period_no_filters(self):
        """Test KPI metrics retrieval query without filters"""
        result = KPIQueries.get_kpi_metrics_by_period()
        
        query = result['query']
        params = result['params']
        
        assert "SELECT" in query
        assert "FROM kpi_metrics" in query
        assert "ORDER BY date DESC, platform, account, campaign" in query
        
        # No filters should be applied
        assert "$start_date" not in query
        assert "$end_date" not in query
        assert "$platform" not in query
        assert len(params) == 0
    
    def test_get_kpi_metrics_by_period_with_filters(self):
        """Test KPI metrics retrieval query with all filters"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        platform = 'Meta'
        
        result = KPIQueries.get_kpi_metrics_by_period(start_date, end_date, platform)
        
        query = result['query']
        params = result['params']
        
        # Check all filters are applied
        assert "date >= $start_date" in query
        assert "date <= $end_date" in query
        assert "platform = $platform" in query
        
        assert params['start_date'] == start_date
        assert params['end_date'] == end_date
        assert params['platform'] == platform
    
    def test_aggregate_kpis_by_dimensions_default(self):
        """Test KPI aggregation by dimensions with default dimensions"""
        dimensions = []  # Empty list should default to date, platform
        
        result = KPIQueries.aggregate_kpis_by_dimensions(dimensions)
        
        query = result['query']
        
        # Should default to date, platform
        assert "date, platform" in query
        assert "GROUP BY date, platform" in query
    
    def test_aggregate_kpis_by_dimensions_custom(self):
        """Test KPI aggregation by custom dimensions"""
        dimensions = ['platform', 'account', 'country']
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        result = KPIQueries.aggregate_kpis_by_dimensions(dimensions, start_date, end_date)
        
        query = result['query']
        params = result['params']
        
        # Check custom dimensions are used
        assert "platform, account, country" in query
        assert "GROUP BY platform, account, country" in query
        
        # Check date filters
        assert "date >= $start_date" in query
        assert "date <= $end_date" in query
        assert params['start_date'] == start_date
        assert params['end_date'] == end_date
    
    def test_aggregate_kpis_by_dimensions_invalid_dimensions(self):
        """Test KPI aggregation with invalid dimensions"""
        dimensions = ['invalid_dim', 'platform', 'another_invalid']
        
        result = KPIQueries.aggregate_kpis_by_dimensions(dimensions)
        
        query = result['query']
        
        # Should only include valid dimensions
        assert "platform" in query
        assert "invalid_dim" not in query
        assert "another_invalid" not in query
    
    def test_validate_kpi_calculations_query(self):
        """Test KPI validation query structure"""
        query = KPIQueries.validate_kpi_calculations()
        
        # Check CTE structure
        assert "WITH raw_aggregated AS" in query
        assert "kpi_stored AS" in query
        
        # Check joins and calculations
        assert "LEFT JOIN kpi_stored k ON" in query
        assert "ABS(r.raw_spend - COALESCE(k.kpi_spend, 0))" in query
        assert "ABS(r.raw_conversions - COALESCE(k.kpi_conversions, 0))" in query
        assert "ABS(COALESCE(r.raw_cac, 0) - COALESCE(k.kpi_cac, 0))" in query
        assert "ABS(COALESCE(r.raw_roas, 0) - COALESCE(k.kip_roas, 0))" in query or "ABS(COALESCE(r.raw_roas, 0) - COALESCE(k.kpi_roas, 0))" in query
        
        # Check filtering for significant differences
        assert "WHERE (" in query
        assert "> 0.01" in query  # Spend difference threshold
        assert "> 0.0001" in query  # CAC/ROAS difference threshold
    
    def test_get_kpi_summary_stats_query(self):
        """Test KPI summary statistics query"""
        query = KPIQueries.get_kpi_summary_stats()
        
        # Check aggregation functions
        assert "COUNT(*) as total_records" in query
        assert "COUNT(DISTINCT date) as unique_dates" in query
        assert "COUNT(DISTINCT platform) as unique_platforms" in query
        assert "SUM(total_spend) as total_spend" in query
        assert "AVG(cac) as avg_cac" in query
        assert "AVG(roas) as avg_roas" in query
        
        # Check NULL counting
        assert "COUNT(CASE WHEN cac IS NULL THEN 1 END)" in query
        assert "COUNT(CASE WHEN roas IS NULL THEN 1 END)" in query
        
        # Check date range
        assert "MIN(date) as earliest_date" in query
        assert "MAX(date) as latest_date" in query
        assert "MIN(created_at) as first_computation" in query
        assert "MAX(created_at) as last_computation" in query
    
    def test_delete_kpi_metrics_by_date(self):
        """Test KPI metrics deletion query"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        result = KPIQueries.delete_kpi_metrics_by_date(start_date, end_date)
        
        query = result['query']
        params = result['params']
        
        assert "DELETE FROM kpi_metrics" in query
        assert "date >= $start_date AND date <= $end_date" in query
        assert params['start_date'] == start_date
        assert params['end_date'] == end_date
    
    def test_kpi_calculation_formulas(self):
        """Test that KPI calculation formulas are correct in queries"""
        result = KPIQueries.compute_daily_kpis()
        query = result['query']
        
        # CAC formula: spend / conversions
        assert "SUM(spend) / SUM(conversions)" in query
        
        # ROAS formula: (conversions * 100) / spend  
        assert "(SUM(conversions) * 100) / SUM(spend)" in query
        
        # Revenue formula: conversions * 100
        assert "SUM(conversions) * 100 as revenue" in query
        
        # Division by zero handling
        assert "WHEN SUM(conversions) > 0 THEN" in query
        assert "WHEN SUM(spend) > 0 THEN" in query
        assert "ELSE NULL" in query
    
    def test_query_parameter_safety(self):
        """Test that queries use parameterized queries for safety"""
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        platform = 'Meta'
        
        # Test various query methods
        queries_to_test = [
            KPIQueries.compute_daily_kpis(start_date, end_date),
            KPIQueries.compute_platform_kpis(start_date, end_date),
            KPIQueries.get_kpi_metrics_by_period(start_date, end_date, platform),
            KPIQueries.aggregate_kpis_by_dimensions(['platform'], start_date, end_date),
            KPIQueries.delete_kpi_metrics_by_date(start_date, end_date)
        ]
        
        for result in queries_to_test:
            query = result['query']
            params = result['params']
            
            # Should use parameterized queries, not string concatenation
            if 'start_date' in params:
                assert "$start_date" in query
                assert str(start_date) not in query  # Date should not be directly in query
            
            if 'end_date' in params:
                assert "$end_date" in query
                assert str(end_date) not in query
            
            if 'platform' in params:
                assert "$platform" in query
                assert "'Meta'" not in query  # Platform should not be directly in query
    
    def test_query_ordering_consistency(self):
        """Test that queries have consistent ordering"""
        result = KPIQueries.compute_daily_kpis()
        query = result['query']
        
        # Should order by date DESC for most recent first
        assert "ORDER BY date DESC" in query
        
        result = KPIQueries.get_kpi_metrics_by_period()
        query = result['query']
        
        # Should have consistent secondary ordering
        assert "ORDER BY date DESC, platform, account, campaign" in query
    
    def test_precision_and_rounding(self):
        """Test that queries specify appropriate precision for calculations"""
        result = KPIQueries.compute_daily_kpis()
        query = result['query']
        
        # Should round CAC and ROAS to 4 decimal places
        assert "ROUND(" in query
        assert ", 4)" in query  # 4 decimal places
        
        # Should have at least 2 ROUND functions (for CAC and ROAS)
        assert query.count("ROUND(") >= 2