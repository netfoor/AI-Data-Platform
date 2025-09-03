"""
Command Line Interface for AI Data Platform
"""
import click
import asyncio
import logging
from pathlib import Path

from .config import settings
from .utils.logging import setup_logging
from .api.workflow_manager import WorkflowManager
from .ingestion.etl_pipeline import ETLPipeline

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@click.group()
@click.version_option(version=settings.version)
def cli():
    """AI Data Platform CLI - Manage data ingestion, analysis, and automation"""
    pass


@cli.group()
def n8n():
    """n8n workflow automation commands"""
    pass


@n8n.command()
@click.option('--api-key', envvar='N8N_API_KEY', help='n8n API key')
def setup(api_key):
    """Set up n8n data ingestion workflow"""
    from ai_data_platform.api.n8n_api_client import N8nAPIClient
    from ai_data_platform.config import settings
    
    try:
        if not api_key:
            click.echo("❌ N8N_API_KEY environment variable or --api-key option is required")
            click.echo("💡 Get your API key from n8n Settings > API Keys")
            return
        
        # Initialize API client
        client = N8nAPIClient(
            base_url=settings.n8n.base_url,
            api_key=api_key,
            webhook_secret=settings.n8n.webhook_secret
        )
        
        # Test connection
        click.echo("🔍 Testing n8n connection...")
        if not client.test_connection():
            click.echo("❌ Cannot connect to n8n. Check if it's running and API key is correct.")
            return
        
        click.echo("✅ Connected to n8n successfully!")
        
        # Set up workflow
        click.echo("📋 Setting up data ingestion workflow...")
        workflow_id = client.setup_data_ingestion_workflow()
        
        if workflow_id:
            click.echo(f"🎉 Workflow created and activated successfully!")
            click.echo(f"📊 Workflow ID: {workflow_id}")
            click.echo("🚀 Ready to run data ingestion!")
        else:
            click.echo("❌ Failed to create workflow. Check logs for details.")
            
    except Exception as e:
        click.echo(f"❌ Error during n8n setup: {e}")
        click.echo("💡 Make sure n8n is running and API key is correct.")


@n8n.command()
@click.option('--api-key', envvar='N8N_API_KEY', help='n8n API key')
def test(api_key):
    """Test connection to n8n instance"""
    from ai_data_platform.api.n8n_api_client import N8nAPIClient
    from ai_data_platform.config import settings
    
    try:
        if not api_key:
            click.echo("❌ N8N_API_KEY environment variable or --api-key option is required")
            click.echo("💡 Get your API key from n8n Settings > API Keys")
            return
        
        # Initialize API client
        client = N8nAPIClient(
            base_url=settings.n8n.base_url,
            api_key=api_key,
            webhook_secret=settings.n8n.webhook_secret
        )
        
        # Test connection
        click.echo("🔍 Testing n8n connection...")
        if client.test_connection():
            click.echo("✅ Successfully connected to n8n instance!")
            
            # Get workflows
            workflows = client.get_workflows()
            if workflows:
                click.echo(f"📋 Found {len(workflows)} workflows:")
                for workflow in workflows[:5]:  # Show first 5
                    status = "🟢 Active" if workflow.get('active') else "🔴 Inactive"
                    click.echo(f"  - {workflow.get('name')} ({status})")
            else:
                click.echo("📋 No workflows found")
        else:
            click.echo("❌ Failed to connect to n8n instance")
            click.echo("Please check your n8n configuration and try again")
    except Exception as e:
        click.echo(f"❌ Test failed: {e}")


@n8n.command()
@click.option('--csv-file', '-f', help='Path to CSV file for ingestion')
@click.option('--api-key', envvar='N8N_API_KEY', help='n8n API key')
def ingest(csv_file, api_key):
    """Trigger data ingestion workflow"""
    from ai_data_platform.api.n8n_api_client import N8nAPIClient
    from ai_data_platform.config import settings
    
    try:
        if not api_key:
            click.echo("❌ N8N_API_KEY environment variable or --api-key option is required")
            click.echo("💡 Get your API key from n8n Settings > API Keys")
            return
        
        if not csv_file:
            csv_file = "ads_spend.csv"
        
        click.echo(f"🚀 Triggering data ingestion workflow for {csv_file}...")
        
        # Initialize API client
        client = N8nAPIClient(
            base_url=settings.n8n.base_url,
            api_key=api_key,
            webhook_secret=settings.n8n.webhook_secret
        )
        
        # Run data ingestion
        success = client.run_data_ingestion(csv_file)
        
        if success:
            click.echo("✅ Data ingestion workflow executed successfully!")
            click.echo("📊 Check n8n interface for execution details")
        else:
            click.echo("❌ Data ingestion workflow failed!")
            click.echo("💡 Check n8n logs for error details")
            
    except Exception as e:
        click.echo(f"❌ Ingestion failed: {e}")


@n8n.command()
@click.option('--api-key', envvar='N8N_API_KEY', help='n8n API key')
def status(api_key):
    """Get current workflow status"""
    from ai_data_platform.api.n8n_api_client import N8nAPIClient
    from ai_data_platform.config import settings
    
    try:
        if not api_key:
            click.echo("❌ N8N_API_KEY environment variable or --api-key option is required")
            click.echo("💡 Get your API key from n8n Settings > API Keys")
            return
        
        click.echo("📊 Getting workflow status...")
        
        # Initialize API client
        client = N8nAPIClient(
            base_url=settings.n8n.base_url,
            api_key=api_key,
            webhook_secret=settings.n8n.webhook_secret
        )
        
        # Get data ingestion workflow
        workflow = client.get_workflow_by_name("AI Data Platform - Data Ingestion")
        if workflow:
            workflow_id = workflow.get('id')
            status_info = client.get_workflow_status(workflow_id)
            
            click.echo(f"📋 Workflow: {workflow.get('name')}")
            click.echo(f"🆔 ID: {workflow_id}")
            click.echo(f"📊 Status: {'🟢 Active' if workflow.get('active') else '🔴 Inactive'}")
            click.echo(f"📅 Created: {workflow.get('createdAt', 'Unknown')}")
            click.echo(f"🔄 Version: {workflow.get('versionId', 'Unknown')}")
            
            # Get recent executions
            executions = client.monitor_workflow_executions(workflow_id, limit=5)
            if executions:
                click.echo(f"\n📈 Recent Executions ({len(executions)}):")
                for execution in executions:
                    status = execution.get('status', 'Unknown')
                    status_icon = "✅" if status == "success" else "❌" if status == "error" else "⏳"
                    click.echo(f"  {status_icon} {execution.get('id', 'Unknown')} - {status}")
            else:
                click.echo("\n📈 No executions found")
        else:
            click.echo("❌ Data ingestion workflow not found")
            click.echo("💡 Run 'n8n setup' to create the workflow")
            
    except Exception as e:
        click.echo(f"❌ Status check failed: {e}")


@cli.group()
def data():
    """Data management commands"""
    pass

@cli.group()
def analytics():
    """Analytics and time-based analysis commands"""
    pass

@analytics.command()
def time_analysis():
    """Run time-based analysis for last 30 days vs prior 30 days"""
    try:
        from ai_data_platform.database.connection import DatabaseConnection
        from ai_data_platform.analytics.time_analysis import TimeAnalysisEngine
        
        print("🔍 Running time-based analysis...")
        
        # Get database connection
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            print("❌ Failed to connect to database")
            return
        
        # Initialize time analysis engine
        engine = TimeAnalysisEngine(conn)
        
        # Run analysis
        analysis = engine.analyze_last_30_days_vs_prior()
        
        print(f"\n📊 Time-based Analysis Results")
        print(f"📅 Current Period: {analysis['current_period']['start_date']} to {analysis['current_period']['end_date']} ({analysis['current_period']['days']} days)")
        print(f"📅 Previous Period: {analysis['previous_period']['start_date']} to {analysis['previous_period']['end_date']} ({analysis['previous_period']['days']} days)")
        
        print(f"\n📋 Summary:")
        print(f"   {analysis['summary']}")
        
        if analysis['comparison']:
            print(f"\n📊 Detailed Comparison Table:")
            table = engine.format_comparison_table(analysis['comparison'])
            print(table)
        
        print(f"\n✅ Time-based analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running time-based analysis: {e}")
        logger.error(f"Error in time_analysis command: {e}")

@analytics.command()
@click.option('--days', default=30, help='Number of days to analyze')
def trend(days):
    """Show daily metrics trend for the specified number of days"""
    try:
        from ai_data_platform.database.connection import DatabaseConnection
        from ai_data_platform.analytics.time_analysis import TimeAnalysisEngine
        
        print(f"📈 Analyzing daily metrics trend for last {days} days...")
        
        # Get database connection
        db = DatabaseConnection()
        conn = db.connect()
        if not conn:
            print("❌ Failed to connect to database")
            return
        
        # Initialize time analysis engine
        engine = TimeAnalysisEngine(conn)
        
        # Get daily metrics
        daily_metrics = engine.get_daily_metrics_trend(days)
        
        if not daily_metrics:
            print("❌ No daily metrics data available")
            return
        
        print(f"\n📊 Daily Metrics Trend (Last {days} days)")
        print("┌────────────┬──────────┬──────────────┬──────────┬──────────┐")
        print("│    Date    │   Spend  │ Conversions  │   CAC    │   ROAS   │")
        print("├────────────┼──────────┼──────────────┼──────────┼──────────┤")
        
        for metric in daily_metrics:
            date_str = str(metric['date'])
            spend_str = f"${metric['spend']:.2f}"
            conversions_str = str(metric['conversions'])
            cac_str = f"${metric['cac']:.2f}" if metric['cac'] else "N/A"
            roas_str = f"{metric['roas']:.2f}x" if metric['roas'] else "N/A"
            
            print(f"│ {date_str:10} │ {spend_str:8} │ {conversions_str:12} │ {cac_str:8} │ {roas_str:8} │")
        
        print("└────────────┴──────────┴──────────────┴──────────┴──────────┘")
        
        print(f"\n✅ Daily trend analysis completed successfully!")
        
    except Exception as e:
        print(f"❌ Error running daily trend analysis: {e}")
        logger.error(f"Error in trend command: {e}")


@data.command()
@click.option('--csv-file', '-f', help='Path to CSV file for ingestion')
def ingest(csv_file):
    """Run ETL pipeline directly (without n8n)"""
    click.echo("Running ETL pipeline directly...")
    
    try:
        if not csv_file:
            csv_file = str(Path(settings.data.input_directory) / 'ads_spend.csv')
        
        pipeline = ETLPipeline(csv_file)
        result = pipeline.run()
        
        if result.success:
            click.echo("✅ ETL pipeline completed successfully!")
            summary = result.get_summary()
            click.echo(f"Records processed: {summary['records']['total_read']}")
            click.echo(f"Records inserted: {summary['records']['inserted']}")
            click.echo(f"Duration: {summary['duration_seconds']} seconds")
        else:
            click.echo("❌ ETL pipeline failed!")
            click.echo(f"Error: {result.error_message}")
    except Exception as e:
        click.echo(f"❌ ETL pipeline failed: {e}")


@cli.command()
def info():
    """Show platform information and configuration"""
    click.echo(f"🤖 {settings.app_name} v{settings.version}")
    click.echo(f"Environment: {settings.environment}")
    click.echo(f"Database: {settings.database.path}")
    click.echo(f"n8n URL: {settings.n8n.base_url}")
    click.echo(f"n8n Automation: {'✅ Enabled' if settings.n8n.enable_automation else '❌ Disabled'}")
    
    if settings.n8n.workflow_id:
        click.echo(f"Workflow ID: {settings.n8n.workflow_id}")
    else:
        click.echo("Workflow ID: Not configured")


@cli.command()
@click.option('--host', default='127.0.0.1', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload for development')
def serve(host, port, reload):
    """Start the REST API server"""
    click.echo(f"🚀 Starting AI Data Platform API server...")
    click.echo(f"Host: {host}")
    click.echo(f"Port: {port}")
    click.echo(f"Auto-reload: {'✅ Enabled' if reload else '❌ Disabled'}")
    click.echo(f"API docs: http://{host}:{port}/docs")
    click.echo(f"ReDoc: http://{host}:{port}/redoc")
    click.echo("Press Ctrl+C to stop the server")
    
    try:
        from ai_data_platform.api.server import run_server
        run_server(host=host, port=port, reload=reload)
    except KeyboardInterrupt:
        click.echo("\n🛑 Server stopped by user")
    except Exception as e:
        click.echo(f"❌ Failed to start server: {e}")
        logger.error(f"Error starting API server: {e}")


@cli.command()
@click.option('--query', '-q', help='Name of predefined query to execute')
@click.option('--start-date', '-s', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', help='End date (YYYY-MM-DD)')
@click.option('--format', '-f', default='table', type=click.Choice(['table', 'json', 'summary']), help='Output format')
@click.option('--list', '-l', is_flag=True, help='List available predefined queries')
@click.option('--help-query', help='Show help for a specific query')
def sql(query, start_date, end_date, format, list, help_query):
    """Execute parameterized SQL queries using predefined templates"""
    from datetime import datetime, date
    from ai_data_platform.analytics.sql_queries import sql_interface
    
    if list:
        # List available queries
        queries = sql_interface.get_available_queries()
        click.echo("🔍 Available Predefined Queries:")
        click.echo("=" * 50)
        for q in queries:
            click.echo(f"• {q}")
        return
    
    if help_query:
        # Show help for specific query
        help_text = sql_interface.get_query_help(help_query)
        click.echo(help_text)
        return
    
    if not query:
        click.echo("❌ Please specify a query name with --query or use --list to see available queries")
        click.echo("💡 Use --help-query <query_name> for detailed help on a specific query")
        return
    
    # Parse dates
    try:
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError as e:
        click.echo(f"❌ Invalid date format: {e}")
        click.echo("💡 Use YYYY-MM-DD format (e.g., 2025-06-01)")
        return
    
    # Set default dates if not provided
    if not start_date:
        start_date = date(2025, 6, 1)
    if not end_date:
        end_date = date(2025, 6, 30)
    
    # Prepare parameters
    parameters = {
        'start_date': start_date,
        'end_date': end_date
    }
    
    # Handle special case for period comparison
    if query == 'period_comparison':
        # For period comparison, we need previous period dates
        from datetime import timedelta
        period_length = (end_date - start_date).days + 1
        previous_end_date = start_date - timedelta(days=1)
        previous_start_date = previous_end_date - timedelta(days=period_length - 1)
        
        parameters.update({
            'previous_start_date': previous_start_date,
            'previous_end_date': previous_end_date
        })
    
    click.echo(f"🚀 Executing query: {query}")
    click.echo(f"📅 Parameters: {start_date} to {end_date}")
    click.echo("-" * 50)
    
    # Execute query
    result = sql_interface.execute_predefined_query(query, parameters)
    
    if not result.success:
        click.echo(f"❌ Query failed: {result.error_message}")
        return
    
    # Format and display results
    formatted_result = sql_interface.format_query_result(result, format)
    click.echo(formatted_result)
    
    # Show execution summary
    click.echo(f"\n📊 Execution Summary:")
    click.echo(f"   • Query: {query}")
    click.echo(f"   • Rows returned: {result.row_count}")
    click.echo(f"   • Execution time: {result.execution_time:.3f}s")


if __name__ == '__main__':
    cli()