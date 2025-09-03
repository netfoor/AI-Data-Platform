"""
End-to-End Pipeline Tests
Tests complete data flow from CSV ingestion to API responses
"""
import pytest
import tempfile
import os
import shutil
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

from ai_data_platform.ingestion.etl_pipeline import run_etl_pipeline
from ai_data_platform.analytics.kpi_engine import KPIEngine
from ai_data_platform.analytics.sql_queries import sql_interface
from ai_data_platform.database.connection import DatabaseConnection
from ai_data_platform.database.schema import SchemaManager


class TestEndToEndPipeline:
    """Test complete data pipeline from ingestion to analysis"""
    
    def setup_method(self):
        """Set up test environment"""
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data"
        self.data_dir.mkdir()
        
        # Use in-memory database for testing
        self.db_path = ":memory:"
        
        # Initialize test database
        self.db = DatabaseConnection(db_path=self.db_path)
        
        # Initialize database schema using the same connection
        schema_manager = SchemaManager(self.db)
        schema_manager.create_raw_ads_spend_table()
        schema_manager.create_kpi_metrics_table()
        schema_manager.create_indexes()
        schema_manager.create_views()
        
        # Create test CSV file
        self.test_csv = self.data_dir / "test_ads_spend.csv"
        self._create_test_csv()
        
        # Initialize components
        self.kpi_engine = KPIEngine(self.db)
    
    def teardown_method(self):
        """Clean up test environment"""
        self.db.disconnect()
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_csv(self):
        """Create test CSV file with sample data"""
        csv_content = """date,platform,account,campaign,country,device,spend,clicks,impressions,conversions
2025-06-01,Meta,TestAccount,TestCampaign,US,Mobile,100.00,50,1000,5
2025-06-01,Meta,TestAccount,TestCampaign,US,Desktop,80.00,40,800,4
2025-06-01,Google,TestAccount,TestCampaign,US,Mobile,120.00,60,1200,6
2025-06-01,Google,TestAccount,TestCampaign,US,Desktop,90.00,45,900,4
2025-06-02,Meta,TestAccount,TestCampaign,US,Mobile,110.00,55,1100,5
2025-06-02,Meta,TestAccount,TestCampaign,US,Desktop,85.00,42,850,4
2025-06-02,Google,TestAccount,TestCampaign,US,Mobile,125.00,62,1250,6
2025-06-02,Google,TestAccount,TestCampaign,US,Desktop,95.00,47,950,4
2025-05-01,Meta,TestAccount,TestCampaign,US,Mobile,95.00,47,950,4
2025-05-01,Meta,TestAccount,TestCampaign,US,Desktop,75.00,37,750,3
2025-05-01,Google,TestAccount,TestCampaign,US,Mobile,115.00,57,1150,5
2025-05-01,Google,TestAccount,TestCampaign,US,Desktop,85.00,42,850,4"""
        
        with open(self.test_csv, 'w') as f:
            f.write(csv_content)
    
    @pytest.mark.e2e
    def test_complete_etl_pipeline(self):
        """Test complete ETL pipeline execution"""
        # Run ETL pipeline
        result = run_etl_pipeline(
            csv_file_path=str(self.test_csv),
            batch_id="test_e2e_batch"
        )
        
        # Verify pipeline success
        assert result.success is True
        assert result.total_records_read == 12
        assert result.valid_records == 12
        assert result.records_inserted == 12
        assert result.records_failed == 0
        assert result.validation_success_rate == 100.0
        assert result.insertion_success_rate == 100.0
        
        # Verify batch tracking
        assert result.batch_id == "test_e2e_batch"
        assert result.source_file == str(self.test_csv)
        assert result.duration_seconds > 0
    
    @pytest.mark.e2e
    def test_data_persistence_after_etl(self):
        """Test that data persists correctly after ETL"""
        # Run ETL pipeline
        run_etl_pipeline(str(self.test_csv), "test_persistence_batch")
        
        # Verify data in database
        count_query = "SELECT COUNT(*) FROM raw_ads_spend"
        result = self.db.execute_query(count_query)
        count = result.fetchone()[0]
        assert count == 12
        
        # Verify metadata was added
        metadata_query = """
        SELECT COUNT(*) FROM raw_ads_spend 
        WHERE load_date IS NOT NULL 
        AND source_file_name IS NOT NULL 
        AND batch_id IS NOT NULL
        """
        result = self.db.execute_query(metadata_query)
        metadata_count = result.fetchone()[0]
        assert metadata_count == 12
    
    @pytest.mark.e2e
    def test_kpi_computation_after_etl(self):
        """Test KPI computation after ETL pipeline"""
        # Run ETL pipeline
        run_etl_pipeline(str(self.test_csv), "test_kpi_batch")
        
        # Compute KPIs for June 2025
        stored_count = self.kpi_engine.compute_and_store_kpis(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 2),
            dimensions=['platform']
        )
        
        assert stored_count == 2  # Meta and Google
        
        # Verify KPI calculations
        meta_kpis = self.kpi_engine.get_kpi_metrics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 2),
            platform='Meta'
        )
        
        assert len(meta_kpis) == 1
        meta_kpi = meta_kpis[0]
        
        # Meta total: 100+80+110+85 = 375, conversions: 5+4+5+4 = 18
        assert meta_kpi['total_spend'] == 375.0
        assert meta_kpi['total_conversions'] == 18
        assert meta_kpi['cac'] == pytest.approx(20.8333, abs=0.01)  # 375/18
        assert meta_kpi['roas'] == pytest.approx(4.8, abs=0.01)     # (18*100)/375
    
    @pytest.mark.e2e
    def test_sql_query_interface_after_etl(self):
        """Test SQL query interface after ETL and KPI computation"""
        # Run ETL pipeline
        run_etl_pipeline(str(self.test_csv), "test_sql_batch")
        
        # Compute KPIs
        self.kpi_engine.compute_and_store_kpis(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 2),
            dimensions=['platform']
        )
        
        # Test SQL query interface
        result = sql_interface.execute_predefined_query(
            'platform_performance',
            {
                'start_date': date(2025, 6, 1),
                'end_date': date(2025, 6, 2)
            }
        )
        
        assert result.success is True
        assert result.row_count == 2  # Meta and Google
        
        # Verify Meta data
        meta_data = next(row for row in result.data if row['platform'] == 'Meta')
        assert meta_data['total_spend'] == 375.0
        assert meta_data['total_conversions'] == 18
        assert meta_data['cac'] == pytest.approx(20.8333, abs=0.01)
        assert meta_data['roas'] == pytest.approx(4.8, abs=0.01)
    
    @pytest.mark.e2e
    def test_period_comparison_analysis(self):
        """Test period-over-period comparison analysis"""
        # Run ETL pipeline
        run_etl_pipeline(str(self.test_csv), "test_comparison_batch")
        
        # Compute KPIs for both periods
        self.kpi_engine.compute_and_store_kpis(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 2),
            dimensions=['platform']
        )
        
        self.kpi_engine.compute_and_store_kpis(
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 1),
            dimensions=['platform']
        )
        
        # Test period comparison query
        result = sql_interface.execute_predefined_query(
            'period_comparison',
            {
                'start_date': date(2025, 6, 1),
                'end_date': date(2025, 6, 2),
                'previous_start_date': date(2025, 5, 1),
                'previous_end_date': date(2025, 5, 1)
            }
        )
        
        assert result.success is True
        assert result.row_count == 1
        
        comparison_data = result.data[0]
        assert 'current_spend' in comparison_data
        assert 'previous_spend' in comparison_data
        assert 'spend_change_percent' in comparison_data
    
    @pytest.mark.e2e
    def test_data_quality_validation(self):
        """Test data quality and validation throughout pipeline"""
        # Run ETL pipeline
        result = run_etl_pipeline(str(self.test_csv), "test_quality_batch")
        
        # Verify data quality metrics
        assert result.validation_success_rate == 100.0
        assert result.insertion_success_rate == 100.0
        assert result.total_records_read == result.valid_records
        assert result.records_inserted == result.valid_records
        
        # Verify no validation errors
        assert len(result.validation_errors) == 0
        assert len(result.insertion_errors) == 0
        
        # Verify data integrity in database
        integrity_query = """
        SELECT COUNT(*) FROM raw_ads_spend 
        WHERE spend < 0 OR clicks < 0 OR impressions < 0 OR conversions < 0
        """
        result = self.db.execute_query(integrity_query)
        negative_count = result.fetchone()[0]
        assert negative_count == 0
    
    @pytest.mark.e2e
    def test_pipeline_performance(self):
        """Test pipeline performance characteristics"""
        # Run ETL pipeline multiple times to test performance
        batch_ids = []
        durations = []
        
        for i in range(3):
            batch_id = f"perf_test_batch_{i}"
            result = run_etl_pipeline(str(self.test_csv), batch_id)
            
            batch_ids.append(batch_id)
            durations.append(result.duration_seconds)
            
            # Verify consistent results
            assert result.success is True
            assert result.total_records_read == 12
            assert result.records_inserted == 12
        
        # Verify performance is reasonable (should complete in under 60 seconds)
        for duration in durations:
            assert duration < 60.0
        
        # Verify all batches are tracked
        for batch_id in batch_ids:
            batch_query = "SELECT COUNT(*) FROM raw_ads_spend WHERE batch_id = ?"
            result = self.db.execute_query(batch_query, [batch_id])
            count = result.fetchone()[0]
            assert count == 12


if __name__ == "__main__":
    pytest.main([__file__])
