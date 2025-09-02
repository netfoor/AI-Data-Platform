"""
Main CLI interface for AI Data Platform
"""
import click
import logging
from pathlib import Path
import sys

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ai_data_platform.utils.logging import setup_logging
from ai_data_platform.analytics.cli import kpi_cli

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.version_option(version='0.1.0', prog_name='AI Data Platform')
def cli(verbose: bool):
    """AI Data Platform - Comprehensive data engineering solution"""
    setup_logging()
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@cli.command()
def init():
    """Initialize the AI Data Platform database and schema"""
    from ai_data_platform.database.init_db import DatabaseInitializer
    
    try:
        initializer = DatabaseInitializer()
        initializer.initialize_database()
        click.echo("✅ AI Data Platform initialized successfully")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        click.echo(f"❌ Initialization failed: {e}", err=True)
        raise click.Abort()


@cli.command()
def status():
    """Show AI Data Platform status and statistics"""
    from ai_data_platform.database.connection import DatabaseConnection
    
    try:
        db = DatabaseConnection()
        
        # Check database connection
        with db.get_connection() as conn:
            conn.execute("SELECT 1").fetchone()
        
        click.echo("🟢 Database: Connected")
        
        # Get table statistics
        raw_count_result = db.execute_query("SELECT COUNT(*) FROM raw_ads_spend")
        raw_count = raw_count_result.fetchone()[0]
        
        kpi_count_result = db.execute_query("SELECT COUNT(*) FROM kpi_metrics")
        kpi_count = kpi_count_result.fetchone()[0]
        
        click.echo(f"📊 Raw records: {raw_count:,}")
        click.echo(f"📈 KPI records: {kpi_count:,}")
        
        if raw_count > 0:
            # Get date range
            date_range_result = db.execute_query(
                "SELECT MIN(date) as min_date, MAX(date) as max_date FROM raw_ads_spend"
            )
            min_date, max_date = date_range_result.fetchone()
            click.echo(f"📅 Date range: {min_date} to {max_date}")
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        click.echo(f"❌ Status check failed: {e}", err=True)
        raise click.Abort()


# Add subcommands
cli.add_command(kpi_cli, name='kpi')


@cli.command()
@click.argument('csv_file', type=click.Path(exists=True))
@click.option('--batch-id', help='Custom batch ID (optional)')
@click.option('--skip-existing', is_flag=True, default=True,
              help='Skip processing if batch already exists')
def ingest(csv_file: str, batch_id: str, skip_existing: bool):
    """Ingest CSV data into the platform"""
    from ai_data_platform.ingestion.etl_pipeline import create_etl_pipeline, run_etl_pipeline
    
    try:
        click.echo(f"Ingesting data from: {csv_file}")
        
        # Create and run ETL pipeline
        pipeline = create_etl_pipeline()
        result = run_etl_pipeline(
            pipeline=pipeline,
            csv_file_path=csv_file,
            batch_id=batch_id,
            skip_existing=skip_existing
        )
        
        if result['success']:
            click.echo(f"✅ Successfully ingested {result['records_processed']} records")
            if result.get('batch_id'):
                click.echo(f"Batch ID: {result['batch_id']}")
        else:
            click.echo(f"❌ Ingestion failed: {result.get('error', 'Unknown error')}", err=True)
            raise click.Abort()
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        click.echo(f"❌ Ingestion failed: {e}", err=True)
        raise click.Abort()


if __name__ == '__main__':
    cli()