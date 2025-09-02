"""
Integration tests for KPI computation engine
"""
import pytest
import tempfile
import os
from decimal import Decimal
from datetime import date, datetime
from pathlib import Path

from ai_data_platform.database.connection import DatabaseConnection
from ai_data_platform.database.init_db import initialize_database
from ai_data_platform.analytics.kpi_engine import KPIEngine
from ai_data_platform.models.ads_spend import AdsSpendRecordWithMetadata


class TestKPIIntegration:
    """Integration tests for KPI computation with real database"""
    
    def setup_method(self):
        """Set up test database and sample data"""
        # Use in-memory database for testing
        self.db = DatabaseConnection(db_path=":memory:")
        
        # Initialize schema manually for testing
        from ai_data_platform.database.schema import SchemaManager
        schema_manager = SchemaManager(self.db)
        schema_manager.create_raw_ads_spend_table()
        schema_manager.create_kpi_metrics_table()
        
        # Initialize KPI engine
        self.kpi_engine = KPIEngine(db_connection=self.db)
        
        # Insert sample data
        self._insert_sample_data()
    
    def teardown_method(self):
        """Clean up test database"""
        self.db.disconnect()
    
    def _insert_sample_data(self):
        """Insert sample advertising spend data"""
        sample_records = [
            # Meta campaigns
            (date(2025, 1, 1), 'Meta', 'AcctA', 'Prospecting', 'US', 'Desktop', 100.0, 50, 1000, 4),
            (date(2025, 1, 1), 'Meta', 'AcctA', 'Retargeting', 'US', 'Mobile', 150.0, 75, 1500, 6),
            (date(2025, 1, 2), 'Meta', 'AcctB', 'Prospecting', 'CA', 'Desktop', 200.0, 100, 2000, 8),
            
            # Google campaigns
            (date(2025, 1, 1), 'Google', 'AcctA', 'Brand_Search', 'US', 'Desktop', 80.0, 40, 800, 2),
            (date(2025, 1, 1), 'Google', 'AcctB', 'Generic_Search', 'CA', 'Mobile', 120.0, 60, 1200, 3),
            (date(2025, 1, 2), 'Google', 'AcctA', 'Brand_Search', 'US', 'Mobile', 90.0, 45, 900, 1),
            
            # Edge cases
            (date(2025, 1, 3), 'Meta', 'AcctC', 'Test_Campaign', 'BR', 'Desktop', 50.0, 25, 500, 0),  # Zero conversions
            (date(2025, 1, 3), 'Google', 'AcctC', 'Test_Campaign', 'MX', 'Mobile', 0.0, 0, 0, 2),     # Zero spend
        ]
        
        insert_query = """
        INSERT INTO raw_ads_spend (
            date, platform, account, campaign, country, device,
            spend, clicks, impressions, conversions,
            load_date, source_file_name, batch_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        parameters_list = []
        for i, record in enumerate(sample_records):
            parameters_list.append([
                *record,  # date through conversions
                datetime.now(),  # load_date
                'test_data.csv',  # source_file_name
                f'test_batch_{i}'  # batch_id
            ])
        
        self.db.execute_many(insert_query, parameters_list)
    
    def test_compute_and_store_kpis_full_workflow(self):
        """Test complete KPI computation and storage workflow"""
        # Compute KPIs for all data
        stored_count = self.kpi_engine.compute_and_store_kpis()
        
        # Should have computed KPIs for all unique dimension combinations
        assert stored_count == 8  # 8 unique records in sample data
        
        # Verify KPIs were stored in database
        kpi_data = self.kpi_engine.get_kpi_metrics()
        assert len(kpi_data) == 8
        
        # Check specific KPI calculations
        meta_prospecting = next(
            (kpi for kpi in kpi_data 
             if kpi['platform'] == 'Meta' and kpi['campaign'] == 'Prospecting' and kpi['date'] == date(2025, 1, 1)),
            None
        )
        assert meta_prospecting is not None
        assert meta_prospecting['total_spend'] == 100.0
        assert meta_prospecting['total_conversions'] == 4
        assert meta_prospecting['cac'] == 25.0  # 100 / 4
        assert meta_prospecting['roas'] == 4.0  # 400 / 100
        assert meta_prospecting['revenue'] == 400.0  # 4 * 100
    
    def test_kpi_calculations_with_edge_cases(self):
        """Test KPI calculations handle edge cases correctly"""
        # Compute KPIs
        self.kpi_engine.compute_and_store_kpis()
        kpi_data = self.kpi_engine.get_kpi_metrics()
        
        # Find zero conversions record
        zero_conversions = next(
            (kpi for kpi in kpi_data 
             if kpi['total_conversions'] == 0),
            None
        )
        assert zero_conversions is not None
        assert zero_conversions['cac'] is None  # Division by zero
        assert zero_conversions['roas'] == 0.0  # 0 revenue / spend
        assert zero_conversions['revenue'] == 0.0
        
        # Find zero spend record
        zero_spend = next(
            (kpi for kpi in kpi_data 
             if kpi['total_spend'] == 0.0),
            None
        )
        assert zero_spend is not None
        assert zero_spend['cac'] == 0.0  # 0 spend / conversions
        assert zero_spend['roas'] is None  # Division by zero
        assert zero_spend['revenue'] == 200.0  # 2 * 100
    
    def test_kpi_aggregation_by_platform(self):
        """Test KPI aggregation by platform dimension"""
        # Compute KPIs aggregated by date and platform only
        stored_count = self.kpi_engine.compute_and_store_kpis(
            dimensions=['date', 'platform']
        )
        
        # Should have fewer records due to aggregation
        assert stored_count < 8
        
        kpi_data = self.kpi_engine.get_kpi_metrics()
        
        # Find Meta platform aggregation for Jan 1
        meta_jan1 = next(
            (kpi for kpi in kpi_data 
             if kpi['platform'] == 'Meta' and kpi['date'] == date(2025, 1, 1)),
            None
        )
        assert meta_jan1 is not None
        # Should aggregate both Meta campaigns from Jan 1
        assert meta_jan1['total_spend'] == 250.0  # 100 + 150
        assert meta_jan1['total_conversions'] == 10  # 4 + 6
        assert meta_jan1['cac'] == 25.0  # 250 / 10
        assert meta_jan1['roas'] == 4.0  # 1000 / 250
    
    def test_kpi_date_range_filtering(self):
        """Test KPI computation with date range filters"""
        # Compute KPIs only for Jan 1
        stored_count = self.kpi_engine.compute_and_store_kpis(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 1)
        )
        
        # Should only process Jan 1 records
        assert stored_count == 4  # 4 records on Jan 1
        
        kpi_data = self.kpi_engine.get_kpi_metrics()
        
        # All records should be from Jan 1
        for kpi in kpi_data:
            assert kpi['date'] == date(2025, 1, 1)
    
    def test_kpi_validation_against_raw_data(self):
        """Test KPI validation functionality"""
        # Compute and store KPIs
        self.kpi_engine.compute_and_store_kpis()
        
        # Validate calculations
        validation_results = self.kpi_engine.validate_kpi_calculations()
        
        # Should have no mismatches for correctly computed KPIs
        assert validation_results['total_comparisons'] > 0
        assert validation_results['mismatches'] == 0
    
    def test_kpi_retrieval_with_filters(self):
        """Test KPI retrieval with various filters"""
        # Compute KPIs
        self.kpi_engine.compute_and_store_kpis()
        
        # Test platform filter
        meta_kpis = self.kpi_engine.get_kpi_metrics(platform='Meta')
        for kpi in meta_kpis:
            assert kpi['platform'] == 'Meta'
        
        # Test date range filter
        jan1_kpis = self.kpi_engine.get_kpi_metrics(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 1)
        )
        for kpi in jan1_kpis:
            assert kpi['date'] == date(2025, 1, 1)
        
        # Test combined filters
        meta_jan1_kpis = self.kpi_engine.get_kpi_metrics(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 1),
            platform='Meta'
        )
        for kpi in meta_jan1_kpis:
            assert kpi['platform'] == 'Meta'
            assert kpi['date'] == date(2025, 1, 1)
        
        assert len(meta_jan1_kpis) == 2  # 2 Meta campaigns on Jan 1
    
    def test_kpi_upsert_behavior(self):
        """Test that KPI computation handles upserts correctly"""
        # Compute KPIs first time
        first_count = self.kpi_engine.compute_and_store_kpis()
        
        # Compute KPIs again (should replace existing records)
        second_count = self.kpi_engine.compute_and_store_kpis()
        
        # Should have same count both times
        assert first_count == second_count
        
        # Should still have same number of records in database
        kpi_data = self.kpi_engine.get_kpi_metrics()
        assert len(kpi_data) == first_count
    
    def test_precision_and_rounding(self):
        """Test that KPI calculations maintain proper precision"""
        # Add a record that will result in repeating decimals
        insert_query = """
        INSERT INTO raw_ads_spend (
            date, platform, account, campaign, country, device,
            spend, clicks, impressions, conversions,
            load_date, source_file_name, batch_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # 100 / 3 = 33.333... (repeating decimal)
        self.db.execute_query(insert_query, [
            date(2025, 1, 4), 'Meta', 'AcctD', 'Precision_Test', 'US', 'Desktop',
            100.0, 50, 1000, 3,  # spend=100, conversions=3
            datetime.now(), 'precision_test.csv', 'precision_batch'
        ])
        
        # Compute KPIs
        self.kpi_engine.compute_and_store_kpis()
        
        # Find the precision test record
        kpi_data = self.kpi_engine.get_kpi_metrics()
        precision_kpi = next(
            (kpi for kpi in kpi_data 
             if kpi['campaign'] == 'Precision_Test'),
            None
        )
        
        assert precision_kpi is not None
        # CAC should be rounded to 4 decimal places: 33.3333
        assert abs(float(precision_kpi['cac']) - 33.3333) < 0.0001
        # ROAS should be 3.0000 (300 / 100)
        assert abs(float(precision_kpi['roas']) - 3.0000) < 0.0001