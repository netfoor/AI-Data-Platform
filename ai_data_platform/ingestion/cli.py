"""
Command-line interface for data ingestion operations
"""
import argparse
import logging
import sys
from pathlib import Path

from .etl_pipeline import create_etl_pipeline, run_etl_pipeline
from .database_loader import create_database_loader
from ..utils.logging import setup_logging

logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="AI Data Platform - Data Ingestion CLI")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Ingest command
    ingest_parser = subparsers.add_parser('ingest', help='Ingest CSV data')
    ingest_parser.add_argument('csv_file', help='Path to CSV file to ingest')
    ingest_parser.add_argument('--batch-id', help='Custom batch ID (optional)')
    ingest_parser.add_argument('--skip-existing', action='store_true', default=True,
                              help='Skip processing if batch already exists')
    ingest_parser.add_argument('--validation-threshold', type=float, default=95.0,
                              help='Minimum validation success rate percentage (default: 95.0)')
    
    # Dry run command
    dryrun_parser = subparsers.add_parser('dry-run', help='Perform dry run validation')
    dryrun_parser.add_argument('csv_file', help='Path to CSV file to validate')
    dryrun_parser.add_argument('--batch-id', help='Custom batch ID (optional)')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show database status')
    
    # Batch info command
    batch_parser = subparsers.add_parser('batch-info', help='Show batch information')
    batch_parser.add_argument('batch_id', help='Batch ID to query')
    
    # Delete batch command
    delete_parser = subparsers.add_parser('delete-batch', help='Delete a batch')
    delete_parser.add_argument('batch_id', help='Batch ID to delete')
    delete_parser.add_argument('--confirm', action='store_true',
                              help='Confirm deletion without prompting')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Setup logging
    setup_logging()
    
    try:
        if args.command == 'ingest':
            return handle_ingest(args)
        elif args.command == 'dry-run':
            return handle_dry_run(args)
        elif args.command == 'status':
            return handle_status(args)
        elif args.command == 'batch-info':
            return handle_batch_info(args)
        elif args.command == 'delete-batch':
            return handle_delete_batch(args)
        else:
            print(f"Unknown command: {args.command}")
            return 1
            
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return 1


def handle_ingest(args) -> int:
    """Handle the ingest command"""
    csv_file = Path(args.csv_file)
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        return 1
    
    print(f"Starting ingestion of {csv_file}")
    if args.batch_id:
        print(f"Using batch ID: {args.batch_id}")
    
    result = run_etl_pipeline(
        str(csv_file),
        batch_id=args.batch_id,
        skip_if_exists=args.skip_existing,
        validation_threshold=args.validation_threshold
    )
    
    # Print results
    summary = result.get_summary()
    print("\n" + "="*50)
    print("INGESTION RESULTS")
    print("="*50)
    print(f"Batch ID: {summary['batch_id']}")
    print(f"Success: {summary['success']}")
    print(f"Duration: {summary['duration_seconds']} seconds")
    print(f"Records read: {summary['records']['total_read']}")
    print(f"Records valid: {summary['records']['valid']}")
    print(f"Records inserted: {summary['records']['inserted']}")
    print(f"Validation success rate: {summary['success_rates']['validation_percent']}%")
    print(f"Insertion success rate: {summary['success_rates']['insertion_percent']}%")
    
    if summary['error_message']:
        print(f"Error: {summary['error_message']}")
    
    if result.validation_errors:
        print(f"\nValidation errors ({len(result.validation_errors)}):")
        for error in result.validation_errors[:5]:  # Show first 5
            print(f"  - {error}")
        if len(result.validation_errors) > 5:
            print(f"  ... and {len(result.validation_errors) - 5} more")
    
    if result.insertion_errors:
        print(f"\nInsertion errors ({len(result.insertion_errors)}):")
        for error in result.insertion_errors[:5]:  # Show first 5
            print(f"  - {error}")
        if len(result.insertion_errors) > 5:
            print(f"  ... and {len(result.insertion_errors) - 5} more")
    
    return 0 if result.success else 1


def handle_dry_run(args) -> int:
    """Handle the dry-run command"""
    csv_file = Path(args.csv_file)
    
    if not csv_file.exists():
        print(f"Error: CSV file not found: {csv_file}")
        return 1
    
    print(f"Starting dry run for {csv_file}")
    
    pipeline = create_etl_pipeline(str(csv_file), args.batch_id)
    result = pipeline.dry_run()
    
    print("\n" + "="*50)
    print("DRY RUN RESULTS")
    print("="*50)
    print(f"Batch ID: {result['batch_id']}")
    print(f"Ready for processing: {result['ready_for_processing']}")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
        return 1
    
    # File info
    file_info = result['file_info']
    print(f"\nFile Information:")
    print(f"  File: {file_info['file_name']}")
    print(f"  Size: {file_info['file_size_mb']} MB")
    print(f"  Estimated rows: {file_info['estimated_row_count']}")
    
    # Validation summary
    validation = result['validation_summary']
    print(f"\nValidation Summary:")
    print(f"  Total processed: {validation['total_processed']}")
    print(f"  Valid records: {validation['valid_records']}")
    print(f"  Invalid records: {validation['invalid_records']}")
    print(f"  Success rate: {validation['success_rate']}%")
    
    # Sample data
    if result['sample_data']:
        print(f"\nSample Data (first 3 rows):")
        for i, row in enumerate(result['sample_data'], 1):
            print(f"  Row {i}: {dict(list(row.items())[:3])}...")  # Show first 3 columns
    
    return 0


def handle_status(args) -> int:
    """Handle the status command"""
    loader = create_database_loader()
    
    try:
        stats = loader.get_table_stats()
        
        print("\n" + "="*50)
        print("DATABASE STATUS")
        print("="*50)
        print(f"Total records: {stats.get('total_records', 0):,}")
        print(f"Total batches: {stats.get('total_batches', 0)}")
        print(f"Total source files: {stats.get('total_source_files', 0)}")
        print(f"Date range: {stats.get('earliest_date', 'N/A')} to {stats.get('latest_date', 'N/A')}")
        print(f"Load date range: {stats.get('first_load_date', 'N/A')} to {stats.get('last_load_date', 'N/A')}")
        
        return 0
        
    except Exception as e:
        print(f"Error getting database status: {e}")
        return 1


def handle_batch_info(args) -> int:
    """Handle the batch-info command"""
    loader = create_database_loader()
    
    try:
        info = loader.get_batch_info(args.batch_id)
        
        if not info:
            print(f"Batch not found: {args.batch_id}")
            return 1
        
        print("\n" + "="*50)
        print("BATCH INFORMATION")
        print("="*50)
        print(f"Batch ID: {info['batch_id']}")
        print(f"Source file: {info['source_file_name']}")
        print(f"Record count: {info['record_count']:,}")
        print(f"Data date range: {info['earliest_data_date']} to {info['latest_data_date']}")
        print(f"Load date range: {info['first_load_date']} to {info['last_load_date']}")
        
        return 0
        
    except Exception as e:
        print(f"Error getting batch info: {e}")
        return 1


def handle_delete_batch(args) -> int:
    """Handle the delete-batch command"""
    loader = create_database_loader()
    
    # Check if batch exists
    if not loader.check_batch_exists(args.batch_id):
        print(f"Batch not found: {args.batch_id}")
        return 1
    
    # Get batch info for confirmation
    info = loader.get_batch_info(args.batch_id)
    
    if not args.confirm:
        print(f"\nBatch to delete:")
        print(f"  Batch ID: {info['batch_id']}")
        print(f"  Source file: {info['source_file_name']}")
        print(f"  Record count: {info['record_count']:,}")
        
        confirm = input("\nAre you sure you want to delete this batch? (yes/no): ")
        if confirm.lower() not in ['yes', 'y']:
            print("Deletion cancelled")
            return 0
    
    try:
        deleted_count = loader.delete_batch(args.batch_id)
        print(f"Successfully deleted {deleted_count:,} records for batch {args.batch_id}")
        return 0
        
    except Exception as e:
        print(f"Error deleting batch: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())