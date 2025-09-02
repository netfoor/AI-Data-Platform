"""
Command-line interface for KPI computation and analysis
"""
import click
import logging
from datetime import date, datetime, timedelta
from typing import Optional

from .kpi_engine import KPIEngine
from ..utils.logging import setup_logging

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def kpi_cli(verbose: bool):
    """KPI computation and analysis commands"""
    setup_logging(verbose)


@kpi_cli.command()
@click.option('--start-date', type=click.DateTime(formats=['%Y-%m-%d']), 
              help='Start date for KPI computation (YYYY-MM-DD)')
@click.option('--end-date', type=click.DateTime(formats=['%Y-%m-%d']),
              help='End date for KPI computation (YYYY-MM-DD)')
@click.option('--dimensions', multiple=True, 
              type=click.Choice(['date', 'platform', 'account', 'campaign', 'country', 'device']),
              help='Dimensions to group by (can be specified multiple times)')
@click.option('--force', is_flag=True, help='Force recomputation of existing KPIs')
def compute(start_date: Optional[datetime], end_date: Optional[datetime], 
           dimensions: tuple, force: bool):
    """Compute KPIs from raw advertising spend data"""
    
    # Convert datetime to date
    start_date_obj = start_date.date() if start_date else None
    end_date_obj = end_date.date() if end_date else None
    
    # Default to all dimensions if none specified
    dimensions_list = list(dimensions) if dimensions else None
    
    click.echo(f"Computing KPIs for period: {start_date_obj} to {end_date_obj}")
    if dimensions_list:
        click.echo(f"Grouping by dimensions: {', '.join(dimensions_list)}")
    
    try:
        engine = KPIEngine()
        
        if force:
            click.echo("Force mode enabled - existing KPIs will be replaced")
        
        # Compute and store KPIs
        count = engine.compute_and_store_kpis(
            start_date=start_date_obj,
            end_date=end_date_obj,
            dimensions=dimensions_list
        )
        
        click.echo(f"✅ Successfully computed and stored {count} KPI records")
        
    except Exception as e:
        logger.error(f"KPI computation failed: {e}")
        click.echo(f"❌ KPI computation failed: {e}", err=True)
        raise click.Abort()


@kpi_cli.command()
@click.option('--start-date', type=click.DateTime(formats=['%Y-%m-%d']),
              help='Start date for KPI retrieval (YYYY-MM-DD)')
@click.option('--end-date', type=click.DateTime(formats=['%Y-%m-%d']),
              help='End date for KPI retrieval (YYYY-MM-DD)')
@click.option('--platform', type=click.Choice(['Meta', 'Google']),
              help='Filter by platform')
@click.option('--account', help='Filter by account')
@click.option('--format', 'output_format', type=click.Choice(['table', 'json', 'csv']),
              default='table', help='Output format')
@click.option('--limit', type=int, default=50, help='Maximum number of records to display')
def show(start_date: Optional[datetime], end_date: Optional[datetime],
         platform: Optional[str], account: Optional[str], 
         output_format: str, limit: int):
    """Display computed KPI metrics"""
    
    # Convert datetime to date
    start_date_obj = start_date.date() if start_date else None
    end_date_obj = end_date.date() if end_date else None
    
    try:
        engine = KPIEngine()
        
        # Retrieve KPI metrics
        kpi_data = engine.get_kpi_metrics(
            start_date=start_date_obj,
            end_date=end_date_obj,
            platform=platform,
            account=account
        )
        
        if not kpi_data:
            click.echo("No KPI metrics found for the specified criteria")
            return
        
        # Limit results
        kpi_data = kpi_data[:limit]
        
        if output_format == 'json':
            import json
            click.echo(json.dumps(kpi_data, indent=2, default=str))
        
        elif output_format == 'csv':
            import csv
            import sys
            
            if kpi_data:
                writer = csv.DictWriter(sys.stdout, fieldnames=kpi_data[0].keys())
                writer.writeheader()
                writer.writerows(kpi_data)
        
        else:  # table format
            _display_kpi_table(kpi_data)
        
    except Exception as e:
        logger.error(f"KPI retrieval failed: {e}")
        click.echo(f"❌ KPI retrieval failed: {e}", err=True)
        raise click.Abort()


@kpi_cli.command()
def validate():
    """Validate KPI calculations against raw data"""
    
    try:
        engine = KPIEngine()
        
        click.echo("Validating KPI calculations...")
        validation_results = engine.validate_kpi_calculations()
        
        click.echo(f"\n📊 Validation Results:")
        click.echo(f"Total comparisons: {validation_results['total_comparisons']}")
        click.echo(f"Mismatches found: {validation_results['mismatches']}")
        
        if validation_results['mismatches'] == 0:
            click.echo("✅ All KPI calculations are accurate!")
        else:
            click.echo(f"⚠️  Found {validation_results['mismatches']} discrepancies")
            
            if validation_results['details']:
                click.echo("\nFirst few discrepancies:")
                for i, detail in enumerate(validation_results['details'][:5]):
                    click.echo(f"  {i+1}. Date: {detail['date']}, Platform: {detail['platform']}")
                    click.echo(f"     Spend diff: {detail['spend_diff']:.2f}")
                    click.echo(f"     Conversions diff: {detail['conversions_diff']}")
        
    except Exception as e:
        logger.error(f"KPI validation failed: {e}")
        click.echo(f"❌ KPI validation failed: {e}", err=True)
        raise click.Abort()


@kpi_cli.command()
def stats():
    """Display KPI computation statistics"""
    
    try:
        engine = KPIEngine()
        
        # Get summary statistics
        query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT date) as unique_dates,
            COUNT(DISTINCT platform) as unique_platforms,
            COUNT(DISTINCT account) as unique_accounts,
            MIN(date) as earliest_date,
            MAX(date) as latest_date,
            SUM(total_spend) as total_spend,
            SUM(total_conversions) as total_conversions,
            AVG(cac) as avg_cac,
            AVG(roas) as avg_roas,
            COUNT(CASE WHEN cac IS NULL THEN 1 END) as null_cac_count,
            COUNT(CASE WHEN roas IS NULL THEN 1 END) as null_roas_count
        FROM kpi_metrics
        """
        
        result = engine.db.execute_query(query)
        stats = result.fetchone()
        
        if stats and stats[0] > 0:  # total_records > 0
            click.echo("📈 KPI Metrics Statistics:")
            click.echo(f"  Total records: {stats[0]:,}")
            click.echo(f"  Date range: {stats[4]} to {stats[5]}")
            click.echo(f"  Unique dates: {stats[1]}")
            click.echo(f"  Platforms: {stats[2]}")
            click.echo(f"  Accounts: {stats[3]}")
            click.echo(f"  Total spend: ${stats[6]:,.2f}")
            click.echo(f"  Total conversions: {stats[7]:,}")
            click.echo(f"  Average CAC: ${stats[8]:.2f}" if stats[8] else "  Average CAC: N/A")
            click.echo(f"  Average ROAS: {stats[9]:.2f}x" if stats[9] else "  Average ROAS: N/A")
            click.echo(f"  Records with NULL CAC: {stats[10]}")
            click.echo(f"  Records with NULL ROAS: {stats[11]}")
        else:
            click.echo("No KPI metrics found in database")
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        click.echo(f"❌ Stats retrieval failed: {e}", err=True)
        raise click.Abort()


@kpi_cli.command()
@click.option('--days', type=int, default=30, help='Number of days to compute (default: 30)')
def compute_recent(days: int):
    """Compute KPIs for recent data (last N days)"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    click.echo(f"Computing KPIs for last {days} days ({start_date} to {end_date})")
    
    try:
        engine = KPIEngine()
        count = engine.compute_and_store_kpis(start_date=start_date, end_date=end_date)
        click.echo(f"✅ Successfully computed and stored {count} KPI records")
        
    except Exception as e:
        logger.error(f"Recent KPI computation failed: {e}")
        click.echo(f"❌ Recent KPI computation failed: {e}", err=True)
        raise click.Abort()


def _display_kpi_table(kpi_data: list):
    """Display KPI data in a formatted table"""
    
    if not kpi_data:
        return
    
    # Table headers
    headers = ['Date', 'Platform', 'Account', 'Campaign', 'Spend', 'Conv', 'CAC', 'ROAS', 'Revenue']
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    
    for row in kpi_data[:10]:  # Sample first 10 rows for width calculation
        values = [
            str(row['date']),
            str(row['platform']),
            str(row['account'])[:15],  # Truncate long account names
            str(row['campaign'])[:20],  # Truncate long campaign names
            f"${row['total_spend']:,.0f}",
            str(row['total_conversions']),
            f"${row['cac']:.2f}" if row['cac'] else "N/A",
            f"{row['roas']:.2f}x" if row['roas'] else "N/A",
            f"${row['revenue']:,.0f}"
        ]
        
        for i, value in enumerate(values):
            col_widths[i] = max(col_widths[i], len(value))
    
    # Print header
    header_row = " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    click.echo(header_row)
    click.echo("-" * len(header_row))
    
    # Print data rows
    for row in kpi_data:
        values = [
            str(row['date']).ljust(col_widths[0]),
            str(row['platform']).ljust(col_widths[1]),
            str(row['account'])[:15].ljust(col_widths[2]),
            str(row['campaign'])[:20].ljust(col_widths[3]),
            f"${row['total_spend']:,.0f}".rjust(col_widths[4]),
            str(row['total_conversions']).rjust(col_widths[5]),
            (f"${row['cac']:.2f}" if row['cac'] else "N/A").rjust(col_widths[6]),
            (f"{row['roas']:.2f}x" if row['roas'] else "N/A").rjust(col_widths[7]),
            f"${row['revenue']:,.0f}".rjust(col_widths[8])
        ]
        
        click.echo(" | ".join(values))


if __name__ == '__main__':
    kpi_cli()