"""
KPI computation engine for calculating marketing metrics
"""
import logging
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass

from ..database.connection import DatabaseConnection
from ..models.ads_spend import KPIMetrics, PeriodComparison

logger = logging.getLogger(__name__)


@dataclass
class KPICalculationResult:
    """Result of KPI calculation with metadata"""
    cac: Optional[Decimal]
    roas: Optional[Decimal]
    revenue: Decimal
    total_spend: Decimal
    total_conversions: int
    calculation_date: datetime
    has_errors: bool = False
    error_messages: List[str] = None
    
    def __post_init__(self):
        if self.error_messages is None:
            self.error_messages = []


class KPIEngine:
    """Engine for computing marketing KPIs with error handling and aggregation"""
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """Initialize KPI engine
        
        Args:
            db_connection: Database connection instance. If None, uses global instance.
        """
        self.db = db_connection or DatabaseConnection()
        self.revenue_per_conversion = Decimal('100')  # Default revenue per conversion
    
    def calculate_cac(self, spend: Decimal, conversions: int) -> Optional[Decimal]:
        """Calculate Customer Acquisition Cost with division by zero handling
        
        Args:
            spend: Total advertising spend
            conversions: Number of conversions
            
        Returns:
            CAC value or None if conversions is zero
        """
        try:
            if conversions <= 0:
                logger.debug(f"CAC calculation: conversions={conversions}, returning None")
                return None
            
            if spend < 0:
                logger.warning(f"CAC calculation: negative spend={spend}, treating as 0")
                spend = Decimal('0')
            
            cac = spend / Decimal(conversions)
            # Round to 4 decimal places for consistency
            return cac.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating CAC: spend={spend}, conversions={conversions}, error={e}")
            return None
    
    def calculate_roas(self, revenue: Decimal, spend: Decimal) -> Optional[Decimal]:
        """Calculate Return on Ad Spend with error handling
        
        Args:
            revenue: Total revenue generated
            spend: Total advertising spend
            
        Returns:
            ROAS value or None if spend is zero
        """
        try:
            if spend <= 0:
                logger.debug(f"ROAS calculation: spend={spend}, returning None")
                return None
            
            if revenue < 0:
                logger.warning(f"ROAS calculation: negative revenue={revenue}, treating as 0")
                revenue = Decimal('0')
            
            roas = revenue / spend
            # Round to 4 decimal places for consistency
            return roas.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
            
        except Exception as e:
            logger.error(f"Error calculating ROAS: revenue={revenue}, spend={spend}, error={e}")
            return None
    
    def calculate_revenue(self, conversions: int, revenue_per_conversion: Optional[Decimal] = None) -> Decimal:
        """Calculate revenue from conversions
        
        Args:
            conversions: Number of conversions
            revenue_per_conversion: Revenue per conversion (defaults to class setting)
            
        Returns:
            Total revenue
        """
        if revenue_per_conversion is None:
            revenue_per_conversion = self.revenue_per_conversion
        
        if conversions < 0:
            logger.warning(f"Revenue calculation: negative conversions={conversions}, treating as 0")
            conversions = 0
        
        revenue = Decimal(conversions) * revenue_per_conversion
        return revenue.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def compute_kpis_for_record(self, spend: Decimal, conversions: int, 
                               revenue_per_conversion: Optional[Decimal] = None) -> KPICalculationResult:
        """Compute all KPIs for a single record
        
        Args:
            spend: Advertising spend
            conversions: Number of conversions
            revenue_per_conversion: Revenue per conversion override
            
        Returns:
            KPICalculationResult with computed metrics
        """
        errors = []
        
        # Calculate revenue
        revenue = self.calculate_revenue(conversions, revenue_per_conversion)
        
        # Calculate CAC
        cac = self.calculate_cac(spend, conversions)
        if cac is None and conversions == 0:
            errors.append("CAC calculation: Division by zero (no conversions)")
        
        # Calculate ROAS
        roas = self.calculate_roas(revenue, spend)
        if roas is None and spend == 0:
            errors.append("ROAS calculation: Division by zero (no spend)")
        
        return KPICalculationResult(
            cac=cac,
            roas=roas,
            revenue=revenue,
            total_spend=spend,
            total_conversions=conversions,
            calculation_date=datetime.now(),
            has_errors=len(errors) > 0,
            error_messages=errors
        )
    
    def aggregate_raw_data_to_kpis(self, start_date: Optional[date] = None, 
                                  end_date: Optional[date] = None,
                                  dimensions: Optional[List[str]] = None) -> List[KPIMetrics]:
        """Aggregate raw ads spend data and compute KPIs by dimensions
        
        Args:
            start_date: Start date for aggregation (inclusive)
            end_date: End date for aggregation (inclusive)
            dimensions: List of dimensions to group by (default: all dimensions)
            
        Returns:
            List of KPIMetrics objects with computed KPIs
        """
        if dimensions is None:
            dimensions = ['date', 'platform', 'account', 'campaign', 'country', 'device']
        
        # Build the aggregation query
        dimension_columns = ', '.join(dimensions)
        group_by_clause = ', '.join(dimensions)
        
        query = f"""
        SELECT 
            {dimension_columns},
            SUM(spend) as total_spend,
            SUM(conversions) as total_conversions,
            SUM(clicks) as total_clicks,
            SUM(impressions) as total_impressions
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
        
        query += f" GROUP BY {group_by_clause} ORDER BY {group_by_clause}"
        
        try:
            result = self.db.execute_query(query, params)
            rows = result.fetchall()
            
            kpi_metrics = []
            for row in rows:
                # Create a dictionary mapping column names to values
                row_dict = dict(zip([desc[0] for desc in result.description], row))
                
                # Compute KPIs for this aggregated record
                kpi_result = self.compute_kpis_for_record(
                    spend=Decimal(str(row_dict['total_spend'])),
                    conversions=int(row_dict['total_conversions'])
                )
                
                # Create KPIMetrics object with proper defaults for missing dimensions
                kpi_metrics.append(KPIMetrics(
                    date=row_dict.get('date', date.today()),
                    platform=row_dict.get('platform', 'ALL'),
                    account=row_dict.get('account', 'ALL'),
                    campaign=row_dict.get('campaign', 'ALL'),
                    country=row_dict.get('country', 'ALL'),
                    device=row_dict.get('device', 'ALL'),
                    total_spend=kpi_result.total_spend,
                    total_conversions=kpi_result.total_conversions,
                    cac=kpi_result.cac,
                    roas=kpi_result.roas,
                    revenue=kpi_result.revenue,
                    created_at=kpi_result.calculation_date
                ))
            
            logger.info(f"Computed KPIs for {len(kpi_metrics)} aggregated records")
            return kpi_metrics
            
        except Exception as e:
            logger.error(f"Error aggregating raw data to KPIs: {e}")
            raise
    
    def store_kpi_metrics(self, kpi_metrics: List[KPIMetrics]) -> int:
        """Store computed KPI metrics in the database
        
        Args:
            kpi_metrics: List of KPIMetrics to store
            
        Returns:
            Number of records successfully stored
        """
        if not kpi_metrics:
            logger.warning("No KPI metrics to store")
            return 0
        
        # Use UPSERT to handle duplicates (replace existing records)
        upsert_query = """
        INSERT OR REPLACE INTO kpi_metrics (
            date, platform, account, campaign, country, device,
            total_spend, total_conversions, cac, roas, revenue, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        try:
            # Prepare parameter list for batch insert
            parameters_list = []
            for kpi in kpi_metrics:
                parameters_list.append([
                    kpi.date,
                    kpi.platform,
                    kpi.account,
                    kpi.campaign,
                    kpi.country,
                    kpi.device,
                    float(kpi.total_spend),
                    kpi.total_conversions,
                    float(kpi.cac) if kpi.cac is not None else None,
                    float(kpi.roas) if kpi.roas is not None else None,
                    float(kpi.revenue),
                    kpi.created_at
                ])
            
            self.db.execute_many(upsert_query, parameters_list)
            logger.info(f"Successfully stored {len(kpi_metrics)} KPI metrics")
            return len(kpi_metrics)
            
        except Exception as e:
            logger.error(f"Error storing KPI metrics: {e}")
            raise
    
    def compute_and_store_kpis(self, start_date: Optional[date] = None,
                              end_date: Optional[date] = None,
                              dimensions: Optional[List[str]] = None) -> int:
        """Compute KPIs from raw data and store them in the database
        
        Args:
            start_date: Start date for computation (inclusive)
            end_date: End date for computation (inclusive)
            dimensions: List of dimensions to group by
            
        Returns:
            Number of KPI records computed and stored
        """
        logger.info(f"Computing KPIs for period {start_date} to {end_date}")
        
        # Aggregate raw data and compute KPIs
        kpi_metrics = self.aggregate_raw_data_to_kpis(start_date, end_date, dimensions)
        
        # Store computed KPIs
        stored_count = self.store_kpi_metrics(kpi_metrics)
        
        logger.info(f"KPI computation complete: {stored_count} records stored")
        return stored_count
    
    def get_kpi_metrics(self, start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       platform: Optional[str] = None,
                       account: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve computed KPI metrics from the database
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            platform: Platform filter
            account: Account filter
            
        Returns:
            List of KPI metrics as dictionaries
        """
        query = """
        SELECT 
            date, platform, account, campaign, country, device,
            total_spend, total_conversions, cac, roas, revenue, created_at
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
        
        if account:
            query += " AND account = $account"
            params['account'] = account
        
        query += " ORDER BY date DESC, platform, account"
        
        try:
            result = self.db.execute_query(query, params)
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            kpi_data = []
            for row in rows:
                row_dict = dict(zip([desc[0] for desc in result.description], row))
                kpi_data.append(row_dict)
            
            logger.info(f"Retrieved {len(kpi_data)} KPI metrics")
            return kpi_data
            
        except Exception as e:
            logger.error(f"Error retrieving KPI metrics: {e}")
            raise
    
    def validate_kpi_calculations(self) -> Dict[str, Any]:
        """Validate KPI calculations by comparing with raw data
        
        Returns:
            Dictionary with validation results
        """
        validation_query = """
        WITH raw_aggregated AS (
            SELECT 
                date, platform,
                SUM(spend) as raw_spend,
                SUM(conversions) as raw_conversions,
                SUM(conversions) * 100 as raw_revenue,
                CASE 
                    WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                    ELSE NULL 
                END as raw_cac,
                CASE 
                    WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100) / SUM(spend)
                    ELSE NULL 
                END as raw_roas
            FROM raw_ads_spend
            GROUP BY date, platform
        ),
        kpi_aggregated AS (
            SELECT 
                date, platform,
                SUM(total_spend) as kpi_spend,
                SUM(total_conversions) as kpi_conversions,
                SUM(revenue) as kpi_revenue,
                AVG(cac) as kpi_cac,
                AVG(roas) as kpi_roas
            FROM kpi_metrics
            GROUP BY date, platform
        )
        SELECT 
            r.date, r.platform,
            r.raw_spend, k.kpi_spend,
            r.raw_conversions, k.kpi_conversions,
            r.raw_cac, k.kpi_cac,
            r.raw_roas, k.kpi_roas,
            ABS(r.raw_spend - COALESCE(k.kpi_spend, 0)) as spend_diff,
            ABS(r.raw_conversions - COALESCE(k.kpi_conversions, 0)) as conversions_diff
        FROM raw_aggregated r
        LEFT JOIN kpi_aggregated k ON r.date = k.date AND r.platform = k.platform
        ORDER BY r.date DESC, r.platform
        """
        
        try:
            result = self.db.execute_query(validation_query)
            rows = result.fetchall()
            
            validation_results = {
                'total_comparisons': len(rows),
                'mismatches': 0,
                'spend_differences': [],
                'conversion_differences': [],
                'details': []
            }
            
            for row in rows:
                row_dict = dict(zip([desc[0] for desc in result.description], row))
                
                spend_diff = float(row_dict.get('spend_diff', 0))
                conv_diff = float(row_dict.get('conversions_diff', 0))
                
                if spend_diff > 0.01 or conv_diff > 0:  # Allow for small rounding differences
                    validation_results['mismatches'] += 1
                    validation_results['details'].append(row_dict)
                
                validation_results['spend_differences'].append(spend_diff)
                validation_results['conversion_differences'].append(conv_diff)
            
            logger.info(f"KPI validation complete: {validation_results['mismatches']} mismatches found")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating KPI calculations: {e}")
            raise