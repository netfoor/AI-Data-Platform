"""
Data validation functions for advertising spend records
"""
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Any, Tuple, Optional
import csv
from pathlib import Path

from pydantic import ValidationError
from .ads_spend import AdsSpendRecord, AdsSpendRecordWithMetadata, KPIMetrics

logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for validation results"""
    
    def __init__(self):
        self.valid_records: List[AdsSpendRecord] = []
        self.invalid_records: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.total_processed: int = 0
    
    @property
    def is_valid(self) -> bool:
        """Check if validation passed (no errors)"""
        return len(self.errors) == 0
    
    @property
    def success_rate(self) -> float:
        """Calculate the percentage of successfully validated records"""
        if self.total_processed == 0:
            return 0.0
        return (len(self.valid_records) / self.total_processed) * 100
    
    def add_error(self, error: str, row_data: Optional[Dict[str, Any]] = None):
        """Add an error to the validation result"""
        self.errors.append(error)
        if row_data:
            self.invalid_records.append({
                'data': row_data,
                'error': error,
                'timestamp': datetime.now()
            })
    
    def add_warning(self, warning: str):
        """Add a warning to the validation result"""
        self.warnings.append(warning)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of validation results"""
        return {
            'total_processed': self.total_processed,
            'valid_records': len(self.valid_records),
            'invalid_records': len(self.invalid_records),
            'success_rate': round(self.success_rate, 2),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'is_valid': self.is_valid
        }


def validate_ads_spend_record(record_data: Dict[str, Any]) -> Tuple[Optional[AdsSpendRecord], Optional[str]]:
    """Validate a single advertising spend record
    
    Args:
        record_data: Dictionary containing record data
        
    Returns:
        Tuple of (validated_record, error_message)
        If validation succeeds: (AdsSpendRecord, None)
        If validation fails: (None, error_message)
    """
    try:
        # Convert string values to appropriate types
        processed_data = _preprocess_record_data(record_data)
        
        # Create and validate the Pydantic model
        validated_record = AdsSpendRecord(**processed_data)
        
        # Additional business logic validation
        business_validation_error = _validate_business_rules(validated_record)
        if business_validation_error:
            return None, business_validation_error
        
        return validated_record, None
        
    except ValidationError as e:
        error_msg = f"Validation error: {_format_pydantic_errors(e.errors())}"
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected validation error: {str(e)}"
        return None, error_msg


def validate_csv_file(file_path: str, batch_id: str) -> ValidationResult:
    """Validate an entire CSV file of advertising spend records
    
    Args:
        file_path: Path to the CSV file
        batch_id: Unique identifier for this validation batch
        
    Returns:
        ValidationResult object with validation results
    """
    result = ValidationResult()
    file_path_obj = Path(file_path)
    
    if not file_path_obj.exists():
        result.add_error(f"File not found: {file_path}")
        return result
    
    try:
        with open(file_path, 'r', encoding='utf-8') as csvfile:
            # Detect delimiter
            sample = csvfile.read(1024)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            
            # Validate headers
            expected_headers = {
                'date', 'platform', 'account', 'campaign', 'country', 
                'device', 'spend', 'clicks', 'impressions', 'conversions'
            }
            
            actual_headers = set(reader.fieldnames or [])
            missing_headers = expected_headers - actual_headers
            
            if missing_headers:
                result.add_error(f"Missing required columns: {', '.join(missing_headers)}")
                return result
            
            # Validate each row
            for row_num, row in enumerate(reader, start=2):  # Start at 2 because of header
                result.total_processed += 1
                
                # Skip empty rows
                if not any(row.values()):
                    result.add_warning(f"Row {row_num}: Empty row skipped")
                    continue
                
                validated_record, error = validate_ads_spend_record(row)
                
                if validated_record:
                    result.valid_records.append(validated_record)
                else:
                    result.add_error(f"Row {row_num}: {error}", row)
    
    except Exception as e:
        result.add_error(f"Error reading CSV file: {str(e)}")
    
    logger.info(f"CSV validation completed: {result.get_summary()}")
    return result


def validate_kpi_metrics(metrics_data: Dict[str, Any]) -> Tuple[Optional[KPIMetrics], Optional[str]]:
    """Validate KPI metrics data
    
    Args:
        metrics_data: Dictionary containing KPI metrics data
        
    Returns:
        Tuple of (validated_metrics, error_message)
    """
    try:
        validated_metrics = KPIMetrics(**metrics_data)
        
        # Additional validation for KPI-specific business rules
        if validated_metrics.cac is not None and validated_metrics.cac < 0:
            return None, "CAC cannot be negative"
        
        if validated_metrics.roas is not None and validated_metrics.roas < 0:
            return None, "ROAS cannot be negative"
        
        # Validate that revenue calculation is consistent
        expected_revenue = Decimal(validated_metrics.total_conversions * 100)
        if abs(validated_metrics.revenue - expected_revenue) > Decimal('0.01'):
            return None, f"Revenue calculation inconsistent: expected {expected_revenue}, got {validated_metrics.revenue}"
        
        return validated_metrics, None
        
    except ValidationError as e:
        error_msg = f"KPI validation error: {_format_pydantic_errors(e.errors())}"
        return None, error_msg
    except Exception as e:
        error_msg = f"Unexpected KPI validation error: {str(e)}"
        return None, error_msg


def _preprocess_record_data(record_data: Dict[str, Any]) -> Dict[str, Any]:
    """Preprocess record data to convert string values to appropriate types
    
    Args:
        record_data: Raw record data from CSV
        
    Returns:
        Processed record data with correct types
    """
    processed = record_data.copy()
    
    # Convert date string to date object
    if 'date' in processed and isinstance(processed['date'], str):
        try:
            # Try different date formats
            date_str = processed['date'].strip()
            for date_format in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    processed['date'] = datetime.strptime(date_str, date_format).date()
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Unable to parse date: {date_str}")
        except Exception as e:
            raise ValueError(f"Invalid date format: {processed['date']} - {str(e)}")
    
    # Convert numeric fields
    numeric_fields = ['spend', 'clicks', 'impressions', 'conversions']
    for field in numeric_fields:
        if field in processed and isinstance(processed[field], str):
            try:
                if field == 'spend':
                    # Handle spend as decimal
                    processed[field] = Decimal(processed[field].strip().replace(',', ''))
                else:
                    # Handle counts as integers
                    processed[field] = int(float(processed[field].strip().replace(',', '')))
            except (ValueError, InvalidOperation) as e:
                raise ValueError(f"Invalid {field} value: {processed[field]} - {str(e)}")
    
    # Clean string fields
    string_fields = ['platform', 'account', 'campaign', 'country', 'device']
    for field in string_fields:
        if field in processed and isinstance(processed[field], str):
            processed[field] = processed[field].strip()
            
    # Normalize country to uppercase
    if 'country' in processed:
        processed['country'] = processed['country'].upper()
    
    return processed


def _validate_business_rules(record: AdsSpendRecord) -> Optional[str]:
    """Apply additional business rule validation
    
    Args:
        record: Validated AdsSpendRecord
        
    Returns:
        Error message if validation fails, None if passes
    """
    from .ads_spend import VALID_PLATFORMS, VALID_DEVICES, VALID_COUNTRIES
    
    # Validate platform
    if record.platform not in VALID_PLATFORMS:
        return f"Invalid platform: {record.platform}. Must be one of: {', '.join(VALID_PLATFORMS)}"
    
    # Validate device
    if record.device not in VALID_DEVICES:
        return f"Invalid device: {record.device}. Must be one of: {', '.join(VALID_DEVICES)}"
    
    # Validate country
    if record.country.upper() not in VALID_COUNTRIES:
        return f"Invalid country: {record.country}. Must be one of: {', '.join(VALID_COUNTRIES)}"
    
    # Validate clicks don't exceed impressions
    if record.clicks > record.impressions:
        return f"Clicks ({record.clicks}) cannot exceed impressions ({record.impressions})"
    
    # Check for reasonable date range (not too far in the past or future)
    today = date.today()
    if record.date > today:
        return f"Date cannot be in the future: {record.date}"
    
    # Check for reasonable spend amounts (not extremely high)
    if record.spend > Decimal('1000000'):  # $1M per day seems unreasonable
        return f"Spend amount seems unreasonably high: ${record.spend}"
    
    # Check for reasonable conversion rates
    if record.impressions > 0:
        click_rate = (record.clicks / record.impressions) * 100
        if click_rate > 50:  # 50% click rate seems unreasonable
            return f"Click rate seems unreasonably high: {click_rate:.2f}%"
    
    if record.clicks > 0:
        conversion_rate = (record.conversions / record.clicks) * 100
        if conversion_rate > 50:  # 50% conversion rate seems unreasonable
            return f"Conversion rate seems unreasonably high: {conversion_rate:.2f}%"
    
    return None


def _format_pydantic_errors(errors: List[Dict[str, Any]]) -> str:
    """Format Pydantic validation errors into a readable string
    
    Args:
        errors: List of Pydantic error dictionaries
        
    Returns:
        Formatted error message string
    """
    error_messages = []
    for error in errors:
        field = '.'.join(str(loc) for loc in error['loc'])
        message = error['msg']
        error_messages.append(f"{field}: {message}")
    
    return '; '.join(error_messages)


def create_sample_valid_record() -> AdsSpendRecord:
    """Create a sample valid record for testing purposes
    
    Returns:
        Valid AdsSpendRecord instance
    """
    return AdsSpendRecord(
        date=date.today(),
        platform="Meta",
        account="AcctA",
        campaign="Prospecting",
        country="US",
        device="Desktop",
        spend=Decimal("100.50"),
        clicks=150,
        impressions=1000,
        conversions=5
    )


def create_sample_invalid_record_data() -> Dict[str, Any]:
    """Create sample invalid record data for testing purposes
    
    Returns:
        Dictionary with invalid data that should fail validation
    """
    return {
        'date': 'invalid-date',
        'platform': 'InvalidPlatform',
        'account': '',  # Empty account
        'campaign': 'Test Campaign',
        'country': 'INVALID',  # Invalid country code
        'device': 'InvalidDevice',
        'spend': 'not-a-number',
        'clicks': -5,  # Negative clicks
        'impressions': 100,
        'conversions': 200  # More conversions than impressions
    }