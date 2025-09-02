"""
Data transformation functions for adding metadata and processing records
"""
import logging
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models.ads_spend import AdsSpendRecord, AdsSpendRecordWithMetadata

logger = logging.getLogger(__name__)


class DataTransformer:
    """Handles data transformations and metadata addition"""
    
    def __init__(self, source_file_path: str, batch_id: Optional[str] = None):
        """Initialize data transformer
        
        Args:
            source_file_path: Path to the source file being processed
            batch_id: Optional batch ID, will generate one if not provided
        """
        self.source_file_path = Path(source_file_path)
        self.source_file_name = self.source_file_path.name
        self.batch_id = batch_id or self._generate_batch_id()
        self.load_date = datetime.now()
        
        logger.info(f"Initialized data transformer for {self.source_file_name} with batch_id: {self.batch_id}")
    
    def _generate_batch_id(self) -> str:
        """Generate a unique batch ID
        
        Returns:
            Unique batch identifier string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"batch_{timestamp}_{unique_id}"
    
    def add_metadata(self, record: AdsSpendRecord) -> AdsSpendRecordWithMetadata:
        """Add ingestion metadata to a single record
        
        Args:
            record: Original AdsSpendRecord
            
        Returns:
            AdsSpendRecordWithMetadata with added metadata
        """
        return AdsSpendRecordWithMetadata(
            # Copy all original fields
            date=record.date,
            platform=record.platform,
            account=record.account,
            campaign=record.campaign,
            country=record.country,
            device=record.device,
            spend=record.spend,
            clicks=record.clicks,
            impressions=record.impressions,
            conversions=record.conversions,
            # Add metadata
            load_date=self.load_date,
            source_file_name=self.source_file_name,
            batch_id=self.batch_id
        )
    
    def transform_records(self, records: List[AdsSpendRecord]) -> List[AdsSpendRecordWithMetadata]:
        """Transform a list of records by adding metadata
        
        Args:
            records: List of AdsSpendRecord objects
            
        Returns:
            List of AdsSpendRecordWithMetadata objects
        """
        logger.info(f"Transforming {len(records)} records with metadata")
        
        transformed_records = []
        for record in records:
            try:
                transformed_record = self.add_metadata(record)
                transformed_records.append(transformed_record)
            except Exception as e:
                logger.error(f"Error transforming record {record}: {e}")
                raise
        
        logger.info(f"Successfully transformed {len(transformed_records)} records")
        return transformed_records
    
    def get_transformation_metadata(self) -> Dict[str, Any]:
        """Get metadata about the transformation process
        
        Returns:
            Dictionary with transformation metadata
        """
        return {
            'batch_id': self.batch_id,
            'source_file_name': self.source_file_name,
            'source_file_path': str(self.source_file_path),
            'load_date': self.load_date,
            'load_date_iso': self.load_date.isoformat()
        }
    
    def create_batch_summary(self, record_count: int, success_count: int, error_count: int) -> Dict[str, Any]:
        """Create a summary of the batch transformation
        
        Args:
            record_count: Total number of records processed
            success_count: Number of successfully transformed records
            error_count: Number of records that failed transformation
            
        Returns:
            Dictionary with batch summary information
        """
        success_rate = (success_count / record_count * 100) if record_count > 0 else 0
        
        summary = {
            'batch_id': self.batch_id,
            'source_file': self.source_file_name,
            'load_date': self.load_date.isoformat(),
            'total_records': record_count,
            'successful_records': success_count,
            'failed_records': error_count,
            'success_rate_percent': round(success_rate, 2),
            'processing_status': 'completed' if error_count == 0 else 'completed_with_errors'
        }
        
        logger.info(f"Batch transformation summary: {summary}")
        return summary


def create_data_transformer(source_file_path: str, batch_id: Optional[str] = None) -> DataTransformer:
    """Factory function to create a data transformer
    
    Args:
        source_file_path: Path to the source file
        batch_id: Optional batch ID
        
    Returns:
        Configured DataTransformer instance
    """
    return DataTransformer(source_file_path, batch_id)


def generate_batch_id() -> str:
    """Generate a unique batch ID
    
    Returns:
        Unique batch identifier string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"batch_{timestamp}_{unique_id}"