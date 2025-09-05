"""
Time-based Analysis Module for AI Data Platform
Provides period-over-period comparison analysis for CAC and ROAS metrics
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pandas as pd

logger = logging.getLogger(__name__)

@dataclass
class TimeRange:
    """Represents a time range for analysis"""
    start_date: datetime
    end_date: datetime
    label: str
    
    def __post_init__(self):
        self.days = (self.end_date - self.start_date).days + 1

@dataclass
class ComparisonResult:
    """Result of period-over-period comparison"""
    metric: str
    current_value: float
    previous_value: float
    absolute_change: float
    percentage_change: float
    trend: str  # "up", "down", "stable"
    
    def __post_init__(self):
        if self.percentage_change > 5:
            self.trend = "up"
        elif self.percentage_change < -5:
            self.trend = "down"
        else:
            self.trend = "stable"

class TimeAnalysisEngine:
    """Engine for time-based analysis and period comparisons"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        
    def get_last_30_days_range(self) -> TimeRange:
        """Get the last 30 days of available data as a time range"""
        # Use the last 30 days of available data (2025-06-01 to 2025-06-30)
        end_date = datetime(2025, 6, 30).date()
        start_date = datetime(2025, 6, 1).date()
        return TimeRange(
            start_date=start_date,
            end_date=end_date,
            label="Last 30 Days (June 2025)"
        )
    
    def get_prior_30_days_range(self) -> TimeRange:
        """Get the prior 30 days of available data as a time range"""
        # Use the prior 30 days of available data (2025-05-01 to 2025-05-31)
        end_date = datetime(2025, 5, 31).date()
        start_date = datetime(2025, 5, 1).date()
        return TimeRange(
            start_date=start_date,
            end_date=end_date,
            label="Prior 30 Days (May 2025)"
        )
    
    def get_custom_range(self, days: int, end_date: Optional[datetime] = None) -> TimeRange:
        """Get a custom time range within available data"""
        if end_date is None:
            # Default to end of available data
            end_date = datetime(2025, 6, 30).date()
        else:
            end_date = end_date.date()
            
        start_date = end_date - timedelta(days=days-1)
        
        # Ensure we don't go before available data
        min_date = datetime(2025, 1, 1).date()
        if start_date < min_date:
            start_date = min_date
            
        return TimeRange(
            start_date=start_date,
            end_date=end_date,
            label=f"Last {days} Days"
        )
    
    def calculate_period_metrics(self, time_range: TimeRange) -> Dict[str, float]:
        """Calculate CAC and ROAS for a specific time period"""
        try:
            query = """
            SELECT 
                SUM(spend) as total_spend,
                SUM(conversions) as total_conversions,
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
            """
            
            result = self.db.execute_query_raw(query, (time_range.start_date, time_range.end_date))
            row = result.fetchone()
            
            if row and row[0] is not None:
                return {
                    'total_spend': float(row[0]),
                    'total_conversions': int(row[1]),
                    'cac': float(row[2]) if row[2] else None,
                    'roas': float(row[3]) if row[3] else None
                }
            else:
                return {
                    'total_spend': 0.0,
                    'total_conversions': 0,
                    'cac': None,
                    'roas': None
                }
                
        except Exception as e:
            logger.error(f"Error calculating period metrics: {e}")
            return {
                'total_spend': 0.0,
                'total_conversions': 0,
                'cac': None,
                'roas': None
            }
    
    def compare_periods(self, current_range: TimeRange, previous_range: TimeRange) -> Dict[str, ComparisonResult]:
        """Compare two time periods and return analysis results"""
        current_metrics = self.calculate_period_metrics(current_range)
        previous_metrics = self.calculate_period_metrics(previous_range)
        
        results = {}
        
        # Compare CAC
        if current_metrics['cac'] is not None and previous_metrics['cac'] is not None:
            absolute_change = current_metrics['cac'] - previous_metrics['cac']
            percentage_change = ((current_metrics['cac'] - previous_metrics['cac']) / previous_metrics['cac']) * 100
            
            results['cac'] = ComparisonResult(
                metric='CAC',
                current_value=current_metrics['cac'],
                previous_value=previous_metrics['cac'],
                absolute_change=absolute_change,
                percentage_change=percentage_change,
                trend='stable'  # Will be set by __post_init__
            )
        
        # Compare ROAS
        if current_metrics['roas'] is not None and previous_metrics['roas'] is not None:
            absolute_change = current_metrics['roas'] - previous_metrics['roas']
            percentage_change = ((current_metrics['roas'] - previous_metrics['roas']) / previous_metrics['roas']) * 100
            
            results['roas'] = ComparisonResult(
                metric='ROAS',
                current_value=current_metrics['roas'],
                previous_value=previous_metrics['roas'],
                absolute_change=absolute_change,
                percentage_change=percentage_change,
                trend='stable'  # Will be set by __post_init__
            )
        
        return results
    
    def analyze_last_30_days_vs_prior(self) -> Dict[str, Any]:
        """Analyze last 30 days vs prior 30 days"""
        current_range = self.get_last_30_days_range()
        previous_range = self.get_prior_30_days_range()
        
        comparison = self.compare_periods(current_range, previous_range)
        
        return {
            'current_period': {
                'label': current_range.label,
                'start_date': current_range.start_date,
                'end_date': current_range.end_date,
                'days': current_range.days
            },
            'previous_period': {
                'label': previous_range.label,
                'start_date': previous_range.start_date,
                'end_date': previous_range.end_date,
                'days': previous_range.days
            },
            'comparison': comparison,
            'summary': self._generate_summary(comparison)
        }
    
    def _generate_summary(self, comparison: Dict[str, ComparisonResult]) -> str:
        """Generate a human-readable summary of the comparison"""
        if not comparison:
            return "No data available for comparison"
        
        summary_parts = []
        
        if 'cac' in comparison:
            cac = comparison['cac']
            trend_symbol = "📈" if cac.trend == "up" else "📉" if cac.trend == "down" else "➡️"
            summary_parts.append(
                f"CAC: ${cac.current_value:.2f} vs ${cac.previous_value:.2f} "
                f"({cac.percentage_change:+.1f}%) {trend_symbol}"
            )
        
        if 'roas' in comparison:
            roas = comparison['roas']
            trend_symbol = "📈" if roas.trend == "up" else "📉" if roas.trend == "down" else "➡️"
            summary_parts.append(
                f"ROAS: {roas.current_value:.2f}x vs {roas.previous_value:.2f}x "
                f"({roas.percentage_change:+.1f}%) {trend_symbol}"
            )
        
        return " | ".join(summary_parts)
    
    def format_comparison_table(self, comparison: Dict[str, ComparisonResult]) -> str:
        """Format comparison results as a compact table"""
        if not comparison:
            return "No comparison data available"
        
        table = []
        table.append("┌─────────┬──────────┬──────────┬──────────────┬──────────────┐")
        table.append("│ Metric  │ Current  │ Previous │   Change     │   Trend      │")
        table.append("├─────────┼──────────┼──────────┼──────────────┼──────────────┤")
        
        for metric_name, result in comparison.items():
            current_str = f"${result.current_value:.2f}" if metric_name == 'cac' else f"{result.current_value:.2f}x"
            previous_str = f"${result.previous_value:.2f}" if metric_name == 'cac' else f"{result.previous_value:.2f}x"
            change_str = f"{result.absolute_change:+.2f}"
            percentage_str = f"({result.percentage_change:+.1f}%)"
            change_full = f"{change_str} {percentage_str}"
            
            trend_emoji = "📈" if result.trend == "up" else "📉" if result.trend == "down" else "➡️"
            
            table.append(f"│ {metric_name.upper():7} │ {current_str:8} │ {previous_str:8} │ {change_full:12} │ {trend_emoji:12} │")
        
        table.append("└─────────┴──────────┴──────────┴──────────────┴──────────────┘")
        
        return "\n".join(table)
    
    def get_daily_metrics_trend(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get daily metrics trend for the specified number of days"""
        try:
            query = """
            SELECT 
                date,
                SUM(spend) as daily_spend,
                SUM(conversions) as daily_conversions,
                CASE 
                    WHEN SUM(conversions) > 0 THEN SUM(spend) / SUM(conversions)
                    ELSE NULL 
                END as daily_cac,
                CASE 
                    WHEN SUM(spend) > 0 THEN (SUM(conversions) * 100.0) / SUM(spend)
                    ELSE NULL 
                END as daily_roas
            FROM raw_ads_spend 
            WHERE date >= ?
            GROUP BY date
            ORDER BY date DESC
            LIMIT ?
            """
            
            # Use the end of available data instead of current date
            end_date = datetime(2025, 6, 30).date()
            start_date = end_date - timedelta(days=days-1)
            
            # Ensure we don't go before available data
            min_date = datetime(2025, 1, 1).date()
            if start_date < min_date:
                start_date = min_date
            
            result = self.db.execute_query_raw(query, (start_date, days))
            results = result.fetchall()
            
            daily_metrics = []
            for row in results:
                daily_metrics.append({
                    'date': row[0],
                    'spend': float(row[1]),
                    'conversions': int(row[2]),
                    'cac': float(row[3]) if row[3] else None,
                    'roas': float(row[4]) if row[4] else None
                })
            
            return daily_metrics
            
        except Exception as e:
            logger.error(f"Error getting daily metrics trend: {e}")
            return []

