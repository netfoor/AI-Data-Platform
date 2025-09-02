"""
Unit tests for KPI computation engine
"""
import pytest
from decimal import Decimal
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock

from ai_data_platform.analytics.kpi_engine import KPIEngine, KPICalculationResult
from ai_data_platform.models.ads_spend import KPIMetrics


class TestKPIEngine:
    """Test cases for KPI computation engine"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_db = Mock()
        self.engine = KPIEngine(db_connection=self.mock_db)
    
    def test_calculate_cac_normal_case(self):
        """Test CAC calculation with normal values"""
        spend = Decimal('100.00')
        conversions = 4
        
        result = self.engine.calculate_cac(spend, conversions)
        
        assert result == Decimal('25.0000')
    
    def test_calculate_cac_zero_conversions(self):
        """Test CAC calculation with zero conversions (division by zero)"""
        spend = Decimal('100.00')
        conversions = 0
        
        result = self.engine.calculate_cac(spend, conversions)
        
        assert result is None
    
    def test_calculate_cac_negative_conversions(self):
        """Test CAC calculation with negative conversions"""
        spend = Decimal('100.00')
        conversions = -1
        
        result = self.engine.calculate_cac(spend, conversions)
        
        assert result is None
    
    def test_calculate_cac_negative_spend(self):
        """Test CAC calculation with negative spend"""
        spend = Decimal('-50.00')
        conversions = 2
        
        result = self.engine.calculate_cac(spend, conversions)
        
        assert result == Decimal('0.0000')  # Negative spend treated as 0
    
    def test_calculate_cac_high_precision(self):
        """Test CAC calculation with high precision values"""
        spend = Decimal('123.456')
        conversions = 7
        
        result = self.engine.calculate_cac(spend, conversions)
        
        # Should round to 4 decimal places
        expected = Decimal('17.6366')
        assert result == expected
    
    def test_calculate_roas_normal_case(self):
        """Test ROAS calculation with normal values"""
        revenue = Decimal('200.00')
        spend = Decimal('100.00')
        
        result = self.engine.calculate_roas(revenue, spend)
        
        assert result == Decimal('2.0000')
    
    def test_calculate_roas_zero_spend(self):
        """Test ROAS calculation with zero spend (division by zero)"""
        revenue = Decimal('200.00')
        spend = Decimal('0.00')
        
        result = self.engine.calculate_roas(revenue, spend)
        
        assert result is None
    
    def test_calculate_roas_negative_spend(self):
        """Test ROAS calculation with negative spend"""
        revenue = Decimal('200.00')
        spend = Decimal('-50.00')
        
        result = self.engine.calculate_roas(revenue, spend)
        
        assert result is None
    
    def test_calculate_roas_negative_revenue(self):
        """Test ROAS calculation with negative revenue"""
        revenue = Decimal('-100.00')
        spend = Decimal('50.00')
        
        result = self.engine.calculate_roas(revenue, spend)
        
        assert result == Decimal('0.0000')  # Negative revenue treated as 0
    
    def test_calculate_roas_high_precision(self):
        """Test ROAS calculation with high precision values"""
        revenue = Decimal('333.333')
        spend = Decimal('111.111')
        
        result = self.engine.calculate_roas(revenue, spend)
        
        # Should round to 4 decimal places
        expected = Decimal('3.0000')
        assert result == expected
    
    def test_calculate_revenue_normal_case(self):
        """Test revenue calculation with normal values"""
        conversions = 5
        revenue_per_conversion = Decimal('100.00')
        
        result = self.engine.calculate_revenue(conversions, revenue_per_conversion)
        
        assert result == Decimal('500.00')
    
    def test_calculate_revenue_default_rate(self):
        """Test revenue calculation with default conversion rate"""
        conversions = 3
        
        result = self.engine.calculate_revenue(conversions)
        
        assert result == Decimal('300.00')  # Default rate is 100
    
    def test_calculate_revenue_zero_conversions(self):
        """Test revenue calculation with zero conversions"""
        conversions = 0
        
        result = self.engine.calculate_revenue(conversions)
        
        assert result == Decimal('0.00')
    
    def test_calculate_revenue_negative_conversions(self):
        """Test revenue calculation with negative conversions"""
        conversions = -2
        
        result = self.engine.calculate_revenue(conversions)
        
        assert result == Decimal('0.00')  # Negative conversions treated as 0
    
    def test_compute_kpis_for_record_normal_case(self):
        """Test KPI computation for a single record with normal values"""
        spend = Decimal('100.00')
        conversions = 4
        
        result = self.engine.compute_kpis_for_record(spend, conversions)
        
        assert isinstance(result, KPICalculationResult)
        assert result.cac == Decimal('25.0000')
        assert result.roas == Decimal('4.0000')  # (4 * 100) / 100
        assert result.revenue == Decimal('400.00')
        assert result.total_spend == spend
        assert result.total_conversions == conversions
        assert not result.has_errors
        assert len(result.error_messages) == 0
    
    def test_compute_kpis_for_record_zero_conversions(self):
        """Test KPI computation with zero conversions"""
        spend = Decimal('100.00')
        conversions = 0
        
        result = self.engine.compute_kpis_for_record(spend, conversions)
        
        assert result.cac is None
        assert result.roas == Decimal('0.0000')  # 0 revenue / 100 spend = 0
        assert result.revenue == Decimal('0.00')
        assert result.has_errors
        assert "CAC calculation: Division by zero" in result.error_messages[0]
    
    def test_compute_kpis_for_record_zero_spend(self):
        """Test KPI computation with zero spend"""
        spend = Decimal('0.00')
        conversions = 2
        
        result = self.engine.compute_kpis_for_record(spend, conversions)
        
        assert result.cac == Decimal('0.0000')  # 0 spend / 2 conversions = 0 (free acquisition)
        assert result.roas is None  # Division by zero
        assert result.revenue == Decimal('200.00')
        assert result.has_errors
        assert "ROAS calculation: Division by zero" in result.error_messages[0]
    
    def test_compute_kpis_for_record_custom_revenue_rate(self):
        """Test KPI computation with custom revenue per conversion"""
        spend = Decimal('50.00')
        conversions = 1
        custom_rate = Decimal('150.00')
        
        result = self.engine.compute_kpis_for_record(spend, conversions, custom_rate)
        
        assert result.cac == Decimal('50.0000')
        assert result.roas == Decimal('3.0000')  # 150 / 50
        assert result.revenue == Decimal('150.00')
    
    @patch('ai_data_platform.analytics.kpi_engine.datetime')
    def test_aggregate_raw_data_to_kpis(self, mock_datetime):
        """Test aggregation of raw data to KPIs"""
        # Mock datetime.now()
        mock_now = datetime(2025, 1, 15, 12, 0, 0)
        mock_datetime.now.return_value = mock_now
        
        # Mock database query result
        mock_result = Mock()
        mock_result.description = [
            ('date', None), ('platform', None), ('account', None),
            ('campaign', None), ('country', None), ('device', None),
            ('total_spend', None), ('total_conversions', None),
            ('total_clicks', None), ('total_impressions', None)
        ]
        mock_result.fetchall.return_value = [
            (date(2025, 1, 1), 'Meta', 'AcctA', 'Campaign1', 'US', 'Desktop', 100.0, 4, 50, 1000),
            (date(2025, 1, 1), 'Google', 'AcctB', 'Campaign2', 'CA', 'Mobile', 200.0, 2, 30, 800)
        ]
        
        self.mock_db.execute_query.return_value = mock_result
        
        # Test aggregation
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)
        
        result = self.engine.aggregate_raw_data_to_kpis(start_date, end_date)
        
        assert len(result) == 2
        
        # Check first KPI record
        kpi1 = result[0]
        assert isinstance(kpi1, KPIMetrics)
        assert kpi1.date == date(2025, 1, 1)
        assert kpi1.platform == 'Meta'
        assert kpi1.total_spend == Decimal('100.0')
        assert kpi1.total_conversions == 4
        assert kpi1.cac == Decimal('25.0000')
        assert kpi1.roas == Decimal('4.0000')
        assert kpi1.revenue == Decimal('400.00')
        
        # Check second KPI record
        kpi2 = result[1]
        assert kpi2.platform == 'Google'
        assert kpi2.cac == Decimal('100.0000')  # 200 / 2
        assert kpi2.roas == Decimal('1.0000')   # 200 / 200
    
    def test_store_kpi_metrics_empty_list(self):
        """Test storing empty list of KPI metrics"""
        result = self.engine.store_kpi_metrics([])
        
        assert result == 0
        self.mock_db.execute_many.assert_not_called()
    
    def test_store_kpi_metrics_success(self):
        """Test successful storage of KPI metrics"""
        kpi_metrics = [
            KPIMetrics(
                date=date(2025, 1, 1),
                platform='Meta',
                account='AcctA',
                campaign='Campaign1',
                country='US',
                device='Desktop',
                total_spend=Decimal('100.00'),
                total_conversions=4,
                cac=Decimal('25.0000'),
                roas=Decimal('4.0000'),
                revenue=Decimal('400.00')
            )
        ]
        
        result = self.engine.store_kpi_metrics(kpi_metrics)
        
        assert result == 1
        self.mock_db.execute_many.assert_called_once()
        
        # Check the parameters passed to execute_many
        call_args = self.mock_db.execute_many.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "INSERT OR REPLACE INTO kpi_metrics" in query
        assert len(params) == 1
        assert params[0][0] == date(2025, 1, 1)  # date
        assert params[0][1] == 'Meta'            # platform
        assert params[0][6] == 100.0             # total_spend
        assert params[0][7] == 4                 # total_conversions
    
    def test_get_kpi_metrics_with_filters(self):
        """Test retrieving KPI metrics with filters"""
        # Mock database query result
        mock_result = Mock()
        mock_result.description = [
            ('date', None), ('platform', None), ('total_spend', None),
            ('cac', None), ('roas', None)
        ]
        mock_result.fetchall.return_value = [
            (date(2025, 1, 1), 'Meta', 100.0, 25.0, 4.0),
            (date(2025, 1, 2), 'Meta', 150.0, 30.0, 3.5)
        ]
        
        self.mock_db.execute_query.return_value = mock_result
        
        # Test with filters
        result = self.engine.get_kpi_metrics(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
            platform='Meta'
        )
        
        assert len(result) == 2
        assert result[0]['platform'] == 'Meta'
        assert result[0]['total_spend'] == 100.0
        
        # Verify query was called with correct parameters
        call_args = self.mock_db.execute_query.call_args
        query = call_args[0][0]
        params = call_args[0][1]
        
        assert "date >= $start_date" in query
        assert "date <= $end_date" in query
        assert "platform = $platform" in query
        assert params['start_date'] == date(2025, 1, 1)
        assert params['end_date'] == date(2025, 1, 31)
        assert params['platform'] == 'Meta'
    
    def test_validate_kpi_calculations(self):
        """Test KPI calculation validation"""
        # Mock database query result
        mock_result = Mock()
        mock_result.description = [
            ('date', None), ('platform', None), ('spend_diff', None), ('conversions_diff', None)
        ]
        mock_result.fetchall.return_value = [
            (date(2025, 1, 1), 'Meta', 0.0, 0),      # Perfect match
            (date(2025, 1, 2), 'Google', 0.05, 1)   # Small mismatch
        ]
        
        self.mock_db.execute_query.return_value = mock_result
        
        result = self.engine.validate_kpi_calculations()
        
        assert result['total_comparisons'] == 2
        assert result['mismatches'] == 1  # Only the Google record has significant differences
        assert len(result['spend_differences']) == 2
        assert len(result['conversion_differences']) == 2
        assert len(result['details']) == 1  # Only mismatched records in details
    
    def test_edge_case_very_small_spend(self):
        """Test KPI calculation with very small spend amounts"""
        spend = Decimal('0.01')
        conversions = 1
        
        result = self.engine.compute_kpis_for_record(spend, conversions)
        
        assert result.cac == Decimal('0.0100')
        assert result.roas == Decimal('10000.0000')  # 100 / 0.01
    
    def test_edge_case_very_large_numbers(self):
        """Test KPI calculation with very large numbers"""
        spend = Decimal('999999.99')
        conversions = 1000000
        
        result = self.engine.compute_kpis_for_record(spend, conversions)
        
        assert result.cac == Decimal('1.0000')  # Approximately 1.0
        assert result.roas == Decimal('100.0000')  # 100M / 1M
    
    def test_rounding_precision(self):
        """Test that KPI calculations maintain proper precision"""
        # Test case that would result in repeating decimals
        spend = Decimal('100.00')
        conversions = 3  # 100/3 = 33.333...
        
        result = self.engine.compute_kpis_for_record(spend, conversions)
        
        # Should round to 4 decimal places
        assert result.cac == Decimal('33.3333')
        assert result.roas == Decimal('3.0000')  # 300/100
    
    def test_database_error_handling(self):
        """Test error handling when database operations fail"""
        self.mock_db.execute_query.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception) as exc_info:
            self.engine.aggregate_raw_data_to_kpis()
        
        assert "Database connection failed" in str(exc_info.value)
    
    def test_compute_and_store_kpis_integration(self):
        """Test the complete compute and store workflow"""
        # Mock the aggregation method
        mock_kpi_metrics = [
            KPIMetrics(
                date=date(2025, 1, 1),
                platform='Meta',
                account='AcctA',
                campaign='Campaign1',
                country='US',
                device='Desktop',
                total_spend=Decimal('100.00'),
                total_conversions=4,
                cac=Decimal('25.0000'),
                roas=Decimal('4.0000'),
                revenue=Decimal('400.00')
            )
        ]
        
        with patch.object(self.engine, 'aggregate_raw_data_to_kpis', return_value=mock_kpi_metrics):
            with patch.object(self.engine, 'store_kpi_metrics', return_value=1) as mock_store:
                
                result = self.engine.compute_and_store_kpis(
                    start_date=date(2025, 1, 1),
                    end_date=date(2025, 1, 31)
                )
                
                assert result == 1
                mock_store.assert_called_once_with(mock_kpi_metrics)