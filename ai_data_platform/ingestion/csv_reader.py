"""
CSV reader utility for processing ads spend data
"""
import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Iterator, Optional
from decimal import Decimal

from ..models.ads_spend import AdsSpendRecord
from ..models.validation import validate_csv_file, ValidationResult

logger = logging.getLogger(__name__)


class CSVReader:
    """Utility class for reading and processing CSV files"""
    
    def __init__(self, file_path: str):
        """Initialize CSV reader
        
        Args:
            file_path: Path to the CSV file to process
        """
        self.file_path = Path(file_path)
        self.batch_id: Optional[str] = None
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {file_path}")
        
        logger.info(f"Initialized CSV reader for: {self.file_path}")
    
    def set_batch_id(self, batch_id: str) -> None:
        """Set the batch ID for this processing run
        
        Args:
            batch_id: Unique identifier for this batch
        """
        self.batch_id = batch_id
        logger.debug(f"Set batch ID: {batch_id}")
    
    def validate_file(self) -> ValidationResult:
        """Validate the CSV file structure and data
        
        Returns:
            ValidationResult object with validation details
        """
        if not self.batch_id:
            raise ValueError("Batch ID must be set before validation")
        
        logger.info(f"Starting validation of CSV file: {self.file_path}")
        result = validate_csv_file(str(self.file_path), self.batch_id)
        
        if result.is_valid:
            logger.info(f"CSV validation successful: {result.get_summary()}")
        else:
            logger.error(f"CSV validation failed: {result.get_summary()}")
            for error in result.errors[:5]:  # Log first 5 errors
                logger.error(f"Validation error: {error}")
        
        return result
    
    def read_records(self) -> Iterator[Dict[str, Any]]:
        """Read records from CSV file as raw dictionaries
        
        Yields:
            Dictionary representing each CSV row
        """
        logger.info(f"Reading records from CSV file: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                # Auto-detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                record_count = 0
                for row in reader:
                    # Skip empty rows
                    if not any(row.values()):
                        continue
                    
                    record_count += 1
                    yield row
                
                logger.info(f"Successfully read {record_count} records from CSV")
                
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def read_validated_records(self) -> List[AdsSpendRecord]:
        """Read and validate all records from CSV file
        
        Returns:
            List of validated AdsSpendRecord objects
            
        Raises:
            ValueError: If validation fails or batch_id not set
        """
        if not self.batch_id:
            raise ValueError("Batch ID must be set before reading records")
        
        validation_result = self.validate_file()
        
        if not validation_result.is_valid:
            error_summary = validation_result.get_summary()
            raise ValueError(
                f"CSV validation failed: {error_summary['error_count']} errors found. "
                f"Success rate: {error_summary['success_rate']}%"
            )
        
        logger.info(f"Returning {len(validation_result.valid_records)} validated records")
        return validation_result.valid_records
    
    def get_file_info(self) -> Dict[str, Any]:
        """Get information about the CSV file
        
        Returns:
            Dictionary with file metadata
        """
        file_stat = self.file_path.stat()
        
        # Count rows quickly
        row_count = 0
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                row_count = sum(1 for line in f) - 1  # Subtract header row
        except Exception as e:
            logger.warning(f"Could not count rows: {e}")
            row_count = -1
        
        return {
            'file_path': str(self.file_path),
            'file_name': self.file_path.name,
            'file_size_bytes': file_stat.st_size,
            'file_size_mb': round(file_stat.st_size / (1024 * 1024), 2),
            'modified_time': file_stat.st_mtime,
            'estimated_row_count': row_count,
            'batch_id': self.batch_id
        }
    
    def peek_data(self, num_rows: int = 5) -> List[Dict[str, Any]]:
        """Peek at the first few rows of data without full processing
        
        Args:
            num_rows: Number of rows to peek at
            
        Returns:
            List of dictionaries representing the first few rows
        """
        logger.debug(f"Peeking at first {num_rows} rows of CSV file")
        
        rows = []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                # Auto-detect delimiter
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for i, row in enumerate(reader):
                    if i >= num_rows:
                        break
                    if any(row.values()):  # Skip empty rows
                        rows.append(row)
                        
        except Exception as e:
            logger.error(f"Error peeking at CSV data: {e}")
            raise
        
        return rows


def create_csv_reader(file_path: str, batch_id: str) -> CSVReader:
    """Factory function to create a configured CSV reader
    
    Args:
        file_path: Path to the CSV file
        batch_id: Unique identifier for this batch
        
    Returns:
        Configured CSVReader instance
    """
    reader = CSVReader(file_path)
    reader.set_batch_id(batch_id)
    return reader