"""
Integration tests for database operations
Tests database schema, data persistence, and KPI storage
"""
import pytest
import tempfile
import os
from pathlib import Path
from datetime import date, datetime
from decimal import Decimal

from ai_data_platform.database.connection import DatabaseConnection
from ai_data_platform.database.schema import SchemaManager
from ai_data_platform.analytics.kpi_engine import KPIEngine
from ai_data_platform.models.ads_spend import KPIMetrics


class TestDatabaseIntegration:
    """Test database operations and data persistence"""
    
    def setup_method(self):
        """Set up test database"""
        # Use in-memory database for testing
        self.db_path = ":memory:"
        
        # Create connection first
        self.db = DatabaseConnection(db_path=self.db_path)
        
        # Initialize database schema using the same connection
        schema_manager = SchemaManager(self.db)
        schema_manager.create_raw_ads_spend_table()
        schema_manager.create_kpi_metrics_table()
        schema_manager.create_indexes()
        schema_manager.create_views()
        
        # Initialize KPI engine with test database
        self.kpi_engine = KPIEngine(self.db)
    
    def teardown_method(self):
        """Clean up test database"""
        self.db.disconnect()
    
    @pytest.mark.integration
    def test_database_initialization(self):
        """Test database schema creation"""
        # Check if tables exist
        tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
        result = self.db.execute_query(tables_query)
        tables = [row[0] for row in result.fetchall()]
        
        expected_tables = ['raw_ads_spend', 'kpi_metrics']
        for table in expected_tables:
            assert table in tables
    
    @pytest.mark.integration
    def test_raw_ads_spend_schema(self):
        """Test raw_ads_spend table schema"""
        schema_query = "PRAGMA table_info(raw_ads_spend)"
        result = self.db.execute_query(schema_query)
        columns = {row[1]: row[2] for row in result.fetchall()}
        
        expected_columns = {
            'date': 'DATE',
            'platform': 'VARCHAR',
            'account': 'VARCHAR',
            'campaign': 'VARCHAR',
            'country': 'VARCHAR',
            'device': 'VARCHAR',
            'spend': 'DECIMAL',
            'clicks': 'INTEGER',
            'impressions': 'INTEGER',
            'conversions': 'INTEGER',
            'load_date': 'TIMESTAMP',
            'source_file_name': 'VARCHAR',
            'batch_id': 'VARCHAR'
        }
        
        for col, expected_type in expected_columns.items():
            assert col in columns
    
    @pytest.mark.integration
    def test_kpi_metrics_schema(self):
        """Test kpi_metrics table schema"""
        schema_query = "PRAGMA table_info(kpi_metrics)"
        result = self.db.execute_query(schema_query)
        columns = {row[1]: row[2] for row in result.fetchall()}
        
        expected_columns = {
            'date': 'DATE',
            'platform': 'VARCHAR',
            'account': 'VARCHAR',
            'campaign': 'VARCHAR',
            'country': 'VARCHAR',
            'device': 'VARCHAR',
            'total_spend': 'DECIMAL',
            'total_conversions': 'INTEGER',
            'cac': 'DECIMAL',
            'roas': 'DECIMAL',
            'revenue': 'DECIMAL',
            'created_at': 'TIMESTAMP'
        }
        
        for col, expected_type in expected_columns.items():
            assert col in columns
    
    @pytest.mark.integration
    def test_data_insertion_and_retrieval(self):
        """Test data insertion and retrieval"""
        # Insert test data
        test_data = [
            ('2025-06-01', 'Meta', 'TestAccount', 'TestCampaign', 'US', 'Mobile', 100.00, 50, 1000, 5),
            ('2025-06-01', 'Google', 'TestAccount', 'TestCampaign', 'US', 'Desktop', 150.00, 75, 1500, 8),
            ('2025-06-02', 'Meta', 'TestAccount', 'TestCampaign', 'US', 'Mobile', 120.00, 60, 1200, 6)
        ]
        
        insert_query = """
        INSERT INTO raw_ads_spend 
        (date, platform, account, campaign, country, device, spend, clicks, impressions, conversions, 
         load_date, source_file_name, batch_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for row in test_data:
            params = list(row) + [datetime.now(), 'test.csv', 'test_batch_001']
            self.db.execute_query(insert_query, params)
        
        # Verify data was inserted
        count_query = "SELECT COUNT(*) FROM raw_ads_spend"
        result = self.db.execute_query(count_query)
        count = result.fetchone()[0]
        assert count == 3
        
        # Test data retrieval
        select_query = "SELECT platform, SUM(spend) as total_spend FROM raw_ads_spend GROUP BY platform ORDER BY platform"
        result = self.db.execute_query(select_query)
        platforms = result.fetchall()
        
        assert len(platforms) == 2
        # Order is alphabetical: Google, Meta
        assert platforms[0][0] == 'Google'
        assert platforms[0][1] == 150.00
        assert platforms[1][0] == 'Meta'
        assert platforms[1][1] == 220.00  # 100 + 120
    
    @pytest.mark.integration
    def test_kpi_storage_and_retrieval(self):
        """Test KPI metrics storage and retrieval"""
        # Create test KPI metrics
        test_kpis = [
            KPIMetrics(
                date=date(2025, 6, 1),
                platform='Meta',
                account='TestAccount',
                campaign='TestCampaign',
                country='US',
                device='Mobile',
                total_spend=Decimal('100.00'),
                total_conversions=5,
                cac=Decimal('20.00'),
                roas=Decimal('5.00'),
                revenue=Decimal('500.00'),
                created_at=datetime.now()
            ),
            KPIMetrics(
                date=date(2025, 6, 1),
                platform='Google',
                account='TestAccount',
                campaign='TestCampaign',
                country='US',
                device='Desktop',
                total_spend=Decimal('150.00'),
                total_conversions=8,
                cac=Decimal('18.75'),
                roas=Decimal('5.33'),
                revenue=Decimal('800.00'),
                created_at=datetime.now()
            )
        ]
        
        # Store KPIs
        stored_count = self.kpi_engine.store_kpi_metrics(test_kpis)
        assert stored_count == 2
        
        # Retrieve KPIs
        retrieved_kpis = self.kpi_engine.get_kpi_metrics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 1)
        )
        
        assert len(retrieved_kpis) == 2
        
        # Verify Meta KPI
        meta_kpi = next(k for k in retrieved_kpis if k['platform'] == 'Meta')
        assert meta_kpi['total_spend'] == 100.0
        assert meta_kpi['total_conversions'] == 5
        assert meta_kpi['cac'] == 20.0
        assert meta_kpi['roas'] == 5.0
        
        # Verify Google KPI
        google_kpi = next(k for k in retrieved_kpis if k['platform'] == 'Google')
        assert google_kpi['total_spend'] == 150.0
        assert google_kpi['total_conversions'] == 8
        assert google_kpi['cac'] == 18.75
        assert google_kpi['roas'] == pytest.approx(Decimal('5.33'), abs=0.01)
    
    @pytest.mark.integration
    def test_kpi_computation_and_storage(self):
        """Test complete KPI computation and storage workflow"""
        # Insert test raw data
        test_data = [
            ('2025-06-01', 'Meta', 'TestAccount', 'TestCampaign', 'US', 'Mobile', 100.00, 50, 1000, 5),
            ('2025-06-01', 'Meta', 'TestAccount', 'TestCampaign', 'US', 'Desktop', 80.00, 40, 800, 4),
            ('2025-06-01', 'Google', 'TestAccount', 'TestCampaign', 'US', 'Mobile', 120.00, 60, 1200, 6)
        ]
        
        insert_query = """
        INSERT INTO raw_ads_spend 
        (date, platform, account, campaign, country, device, spend, clicks, impressions, conversions, 
         load_date, source_file_name, batch_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        for row in test_data:
            params = list(row) + [datetime.now(), 'test.csv', 'test_batch_002']
            self.db.execute_query(insert_query, params)
        
        # Compute and store KPIs
        stored_count = self.kpi_engine.compute_and_store_kpis(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 1),
            dimensions=['platform']
        )
        
        assert stored_count == 2  # Meta and Google
        
        # Verify computed KPIs
        meta_kpis = self.kpi_engine.get_kpi_metrics(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 1),
            platform='Meta'
        )
        
        assert len(meta_kpis) == 1
        meta_kpi = meta_kpis[0]
        
        # Meta total: 100 + 80 = 180, conversions: 5 + 4 = 9
        assert meta_kpi['total_spend'] == 180.0
        assert meta_kpi['total_conversions'] == 9
        assert meta_kpi['cac'] == 20.0  # 180 / 9
        assert meta_kpi['roas'] == 5.0   # (9 * 100) / 180


if __name__ == "__main__":
    pytest.main([__file__])
