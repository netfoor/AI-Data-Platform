"""
Basic ETL pipeline that orchestrates CSV reading, transformation, and database loading
"""
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from .csv_reader import CSVReader, create_csv_reader
from .transformations import DataTransformer, create_data_transformer, generate_batch_id
from .database_loader import DatabaseLoader, create_database_loader
from ..models.validation import ValidationResult

logger = logging.getLogger(__name__)


class ETLPipelineResult:
    """Container for ETL pipeline execution results"""
    
    def __init__(self):
        self.batch_id: Optional[str] = None
        self.source_file: Optional[str] = None
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.total_records_read: int = 0
        self.valid_records: int = 0
        self.invalid_records: int = 0
        self.records_inserted: int = 0
        self.records_failed: int = 0
        self.validation_errors: List[str] = []
        self.insertion_errors: List[str] = []
        self.success: bool = False
        self.error_message: Optional[str] = None
    
    @property
    def duration_seconds(self) -> float:
        """Calculate pipeline execution duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def validation_success_rate(self) -> float:
        """Calculate validation success rate as percentage"""
        try:
            total_records = float(self.total_records_read) if self.total_records_read else 0
            valid_records = float(self.valid_records) if self.valid_records else 0
            if total_records > 0:
                return (valid_records / total_records) * 100
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    @property
    def insertion_success_rate(self) -> float:
        """Calculate insertion success rate as percentage"""
        try:
            records_inserted = float(self.records_inserted) if self.records_inserted else 0
            records_failed = float(self.records_failed) if self.records_failed else 0
            total_processed = records_inserted + records_failed
            if total_processed > 0:
                return (records_inserted / total_processed) * 100
            return 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the pipeline execution"""
        return {
            'batch_id': self.batch_id,
            'source_file': self.source_file,
            'success': self.success,
            'duration_seconds': round(self.duration_seconds, 2),
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'records': {
                'total_read': self.total_records_read,
                'valid': self.valid_records,
                'invalid': self.invalid_records,
                'inserted': self.records_inserted,
                'failed_insertion': self.records_failed
            },
            'success_rates': {
                'validation_percent': round(self.validation_success_rate, 2),
                'insertion_percent': round(self.insertion_success_rate, 2)
            },
            'error_counts': {
                'validation_errors': len(self.validation_errors),
                'insertion_errors': len(self.insertion_errors)
            },
            'error_message': self.error_message
        }


class ETLPipeline:
    """Main ETL pipeline for processing ads spend data"""
    
    def __init__(self, csv_file_path: str, batch_id: Optional[str] = None):
        """Initialize ETL pipeline
        
        Args:
            csv_file_path: Path to the CSV file to process
            batch_id: Optional batch ID, will generate one if not provided
        """
        self.csv_file_path = Path(csv_file_path)
        self.batch_id = batch_id or generate_batch_id()
        
        # Initialize components
        self.csv_reader: Optional[CSVReader] = None
        self.transformer: Optional[DataTransformer] = None
        self.database_loader: Optional[DatabaseLoader] = None
        
        logger.info(f"Initialized ETL pipeline for {self.csv_file_path} with batch_id: {self.batch_id}")
    
    def _initialize_components(self) -> None:
        """Initialize all pipeline components"""
        logger.debug("Initializing ETL pipeline components")
        
        self.csv_reader = create_csv_reader(str(self.csv_file_path), self.batch_id)
        self.transformer = create_data_transformer(str(self.csv_file_path), self.batch_id)
        self.database_loader = create_database_loader()
        
        logger.debug("ETL pipeline components initialized successfully")
    
    def validate_prerequisites(self) -> None:
        """Validate that all prerequisites are met before running pipeline
        
        Raises:
            FileNotFoundError: If CSV file doesn't exist
            ValueError: If other validation fails
        """
        if not self.csv_file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_file_path}")
        
        if not self.csv_file_path.is_file():
            raise ValueError(f"Path is not a file: {self.csv_file_path}")
        
        if self.csv_file_path.stat().st_size == 0:
            raise ValueError(f"CSV file is empty: {self.csv_file_path}")
        
        logger.debug("Pipeline prerequisites validated successfully")
    
    def run(self, skip_if_exists: bool = True, validation_threshold: float = 95.0) -> ETLPipelineResult:
        """Execute the complete ETL pipeline
        
        Args:
            skip_if_exists: If True, skip processing if batch already exists
            validation_threshold: Minimum validation success rate required (percentage)
            
        Returns:
            ETLPipelineResult with execution details
        """
        result = ETLPipelineResult()
        result.batch_id = self.batch_id
        result.source_file = str(self.csv_file_path)
        result.start_time = datetime.now()
        
        logger.info(f"Starting ETL pipeline execution for batch {self.batch_id}")
        
        try:
            # Validate prerequisites
            self.validate_prerequisites()
            
            # Initialize components
            self._initialize_components()
            
            # Check if batch already exists
            if skip_if_exists and self.database_loader.check_batch_exists(self.batch_id):
                logger.info(f"Batch {self.batch_id} already exists, skipping processing")
                result.success = True
                result.error_message = "Batch already exists, processing skipped"
                return result
            
            # Step 1: Read and validate CSV data
            logger.info("Step 1: Reading and validating CSV data")
            validation_result = self.csv_reader.validate_file()
            
            result.total_records_read = validation_result.total_processed
            result.valid_records = len(validation_result.valid_records)
            result.invalid_records = len(validation_result.invalid_records)
            result.validation_errors = validation_result.errors
            
            # Check validation threshold
            if result.validation_success_rate < validation_threshold:
                raise ValueError(
                    f"Validation success rate {result.validation_success_rate:.1f}% "
                    f"is below threshold {validation_threshold}%"
                )
            
            if not validation_result.valid_records:
                raise ValueError("No valid records found in CSV file")
            
            logger.info(f"Validation completed: {result.valid_records} valid, {result.invalid_records} invalid")
            
            # Step 2: Transform data by adding metadata
            logger.info("Step 2: Transforming data and adding metadata")
            transformed_records = self.transformer.transform_records(validation_result.valid_records)
            
            if len(transformed_records) != result.valid_records:
                logger.warning(
                    f"Record count mismatch after transformation: "
                    f"expected {result.valid_records}, got {len(transformed_records)}"
                )
            
            # Step 3: Load data into database
            logger.info("Step 3: Loading data into database")
            inserted_count, failed_count, insertion_errors = self.database_loader.insert_records(
                transformed_records
            )
            
            result.records_inserted = inserted_count
            result.records_failed = failed_count
            result.insertion_errors = insertion_errors
            
            # Determine overall success
            if result.records_inserted > 0 and result.records_failed == 0:
                result.success = True
                logger.info(f"ETL pipeline completed successfully: {result.records_inserted} records processed")
            elif result.records_inserted > 0:
                result.success = True  # Partial success
                result.error_message = f"Completed with {result.records_failed} insertion failures"
                logger.warning(f"ETL pipeline completed with errors: {result.error_message}")
            else:
                result.success = False
                result.error_message = "No records were successfully inserted"
                logger.error(result.error_message)
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"ETL pipeline failed: {e}")
            
        finally:
            result.end_time = datetime.now()
            
            # Log final summary
            summary = result.get_summary()
            if result.success:
                logger.info(f"ETL pipeline summary: {summary}")
            else:
                logger.error(f"ETL pipeline failed summary: {summary}")
        
        return result
    
    def dry_run(self) -> Dict[str, Any]:
        """Perform a dry run to validate the pipeline without inserting data
        
        Returns:
            Dictionary with dry run results
        """
        logger.info(f"Starting ETL pipeline dry run for {self.csv_file_path}")
        
        try:
            # Validate prerequisites
            self.validate_prerequisites()
            
            # Initialize components (except database loader)
            self.csv_reader = create_csv_reader(str(self.csv_file_path), self.batch_id)
            self.transformer = create_data_transformer(str(self.csv_file_path), self.batch_id)
            
            # Get file info
            file_info = self.csv_reader.get_file_info()
            
            # Peek at data
            sample_data = self.csv_reader.peek_data(3)
            
            # Validate data
            validation_result = self.csv_reader.validate_file()
            
            # Transform a sample
            sample_transformed = []
            if validation_result.valid_records:
                sample_record = validation_result.valid_records[0]
                sample_transformed_record = self.transformer.add_metadata(sample_record)
                sample_transformed = [sample_transformed_record.dict()]
            
            dry_run_result = {
                'batch_id': self.batch_id,
                'file_info': file_info,
                'sample_data': sample_data,
                'validation_summary': validation_result.get_summary(),
                'sample_transformed': sample_transformed,
                'transformation_metadata': self.transformer.get_transformation_metadata(),
                'ready_for_processing': validation_result.is_valid and len(validation_result.valid_records) > 0
            }
            
            logger.info(f"Dry run completed successfully: {dry_run_result['ready_for_processing']}")
            return dry_run_result
            
        except Exception as e:
            logger.error(f"Dry run failed: {e}")
            return {
                'batch_id': self.batch_id,
                'error': str(e),
                'ready_for_processing': False
            }


def create_etl_pipeline(csv_file_path: str, batch_id: Optional[str] = None) -> ETLPipeline:
    """Factory function to create an ETL pipeline
    
    Args:
        csv_file_path: Path to the CSV file to process
        batch_id: Optional batch ID
        
    Returns:
        Configured ETLPipeline instance
    """
    return ETLPipeline(csv_file_path, batch_id)


def run_etl_pipeline(csv_file_path: str, batch_id: Optional[str] = None, **kwargs) -> ETLPipelineResult:
    """Convenience function to create and run an ETL pipeline
    
    Args:
        csv_file_path: Path to the CSV file to process
        batch_id: Optional batch ID
        **kwargs: Additional arguments passed to pipeline.run()
        
    Returns:
        ETLPipelineResult with execution details
    """
    pipeline = create_etl_pipeline(csv_file_path, batch_id)
    return pipeline.run(**kwargs)