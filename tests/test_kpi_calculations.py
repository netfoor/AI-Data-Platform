"""
Unit tests for KPI calculation functions
Tests edge cases, error handling, and calculation accuracy
"""
import pytest
from decimal import Decimal
from datetime import date, datetime

from ai_data_platform.analytics.kpi_engine import KPIEngine, KPICalculationResult


class TestKPICalculations:
    """Test KPI calculation accuracy and edge cases"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.kpi_engine = KPIEngine()
    
    @pytest.mark.unit
    def test_cac_calculation_basic(self):
        """Test basic CAC calculation"""
        spend = Decimal('100.00')
        conversions = 5
        
        cac = self.kpi_engine.calculate_cac(spend, conversions)
        expected = Decimal('20.00')
        
        assert cac == expected
        assert isinstance(cac, Decimal)
    
    @pytest.mark.unit
    def test_cac_division_by_zero(self):
        """Test CAC calculation with zero conversions"""
        spend = Decimal('100.00')
        conversions = 0
        
        cac = self.kpi_engine.calculate_cac(spend, conversions)
        assert cac is None
    
    @pytest.mark.unit
    def test_cac_negative_spend(self):
        """Test CAC calculation with negative spend"""
        spend = Decimal('-50.00')
        conversions = 2
        
        cac = self.kpi_engine.calculate_cac(spend, conversions)
        expected = Decimal('0.00')  # Should treat negative as 0
        
        assert cac == expected
    
    @pytest.mark.unit
    def test_roas_calculation_basic(self):
        """Test basic ROAS calculation"""
        revenue = Decimal('500.00')
        spend = Decimal('100.00')
        
        roas = self.kpi_engine.calculate_roas(revenue, spend)
        expected = Decimal('5.0000')
        
        assert roas == expected
        assert isinstance(roas, Decimal)
    
    @pytest.mark.unit
    def test_roas_division_by_zero(self):
        """Test ROAS calculation with zero spend"""
        revenue = Decimal('500.00')
        spend = Decimal('0.00')
        
        roas = self.kpi_engine.calculate_roas(revenue, spend)
        assert roas is None
    
    @pytest.mark.unit
    def test_roas_negative_revenue(self):
        """Test ROAS calculation with negative revenue"""
        revenue = Decimal('-100.00')
        spend = Decimal('50.00')
        
        roas = self.kpi_engine.calculate_roas(revenue, spend)
        expected = Decimal('0.0000')  # Should treat negative as 0
        
        assert roas == expected
    
    @pytest.mark.unit
    def test_revenue_calculation(self):
        """Test revenue calculation from conversions"""
        conversions = 10
        revenue_per_conversion = Decimal('50.00')
        
        revenue = self.kpi_engine.calculate_revenue(conversions, revenue_per_conversion)
        expected = Decimal('500.00')
        
        assert revenue == expected
    
    @pytest.mark.unit
    def test_revenue_negative_conversions(self):
        """Test revenue calculation with negative conversions"""
        conversions = -5
        revenue_per_conversion = Decimal('50.00')
        
        revenue = self.kpi_engine.calculate_revenue(conversions, revenue_per_conversion)
        expected = Decimal('0.00')  # Should treat negative as 0
        
        assert revenue == expected
    
    @pytest.mark.unit
    def test_compute_kpis_for_record(self):
        """Test complete KPI computation for a single record"""
        spend = Decimal('200.00')
        conversions = 4
        
        result = self.kpi_engine.compute_kpis_for_record(spend, conversions)
        
        assert isinstance(result, KPICalculationResult)
        assert result.cac == Decimal('50.0000')
        assert result.roas == Decimal('2.0000')
        assert result.revenue == Decimal('400.00')
        assert result.total_spend == spend
        assert result.total_conversions == conversions
        assert result.has_errors is False
        assert len(result.error_messages) == 0
    
    @pytest.mark.unit
    def test_compute_kpis_zero_conversions(self):
        """Test KPI computation with zero conversions"""
        spend = Decimal('100.00')
        conversions = 0
        
        result = self.kpi_engine.compute_kpis_for_record(spend, conversions)
        
        assert result.cac is None
        assert result.roas == Decimal('0.0000')
        assert result.revenue == Decimal('0.00')
        assert result.has_errors is True
        assert "Division by zero" in result.error_messages[0]
    
    @pytest.mark.unit
    def test_compute_kpis_zero_spend(self):
        """Test KPI computation with zero spend"""
        spend = Decimal('0.00')
        conversions = 5
        
        result = self.kpi_engine.compute_kpis_for_record(spend, conversions)
        
        assert result.cac == Decimal('0.0000')
        assert result.roas is None
        assert result.revenue == Decimal('500.00')
        assert result.has_errors is True
        assert "Division by zero" in result.error_messages[0]
    
    @pytest.mark.unit
    def test_decimal_precision(self):
        """Test decimal precision in calculations"""
        spend = Decimal('123.4567')
        conversions = 3
        
        cac = self.kpi_engine.calculate_cac(spend, conversions)
        # Should round to 4 decimal places
        assert cac == Decimal('41.1522')
        
        revenue = Decimal('123.4567')
        roas = self.kpi_engine.calculate_roas(revenue, spend)
        # Should round to 4 decimal places
        assert roas == Decimal('1.0000')


class TestKPIValidation:
    """Test KPI validation and business logic"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.kpi_engine = KPIEngine()
    
    @pytest.mark.unit
    def test_validate_kpi_calculations(self):
        """Test KPI validation against raw data"""
        # This test requires database connection and data
        # Will be implemented in integration tests
        pass
    
    @pytest.mark.unit
    def test_platform_metrics_calculation(self):
        """Test platform-level metrics aggregation"""
        # This test requires database connection and data
        # Will be implemented in integration tests
        pass
    
    def test_period_metrics_calculation(self):
        """Test period-level metrics calculation"""
        # This test requires database connection and data
        # Will be implemented in integration tests
        pass


if __name__ == "__main__":
    pytest.main([__file__])
