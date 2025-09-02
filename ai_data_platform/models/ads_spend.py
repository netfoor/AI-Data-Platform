"""
Pydantic data models for advertising spend records
"""
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class AdsSpendRecord(BaseModel):
    """Raw advertising spend record from CSV input"""
    
    date: date
    platform: str
    account: str
    campaign: str
    country: str
    device: str
    spend: Decimal
    clicks: int
    impressions: int
    conversions: int


class AdsSpendRecordWithMetadata(AdsSpendRecord):
    """Ads spend record with ingestion metadata"""
    
    load_date: datetime = Field(default_factory=datetime.now)
    source_file_name: str
    batch_id: str


class KPIMetrics(BaseModel):
    """Computed KPI metrics for advertising performance"""
    
    date: date
    platform: str
    account: str
    campaign: str
    country: str
    device: str
    total_spend: Decimal
    total_conversions: int
    cac: Optional[Decimal] = None
    roas: Optional[Decimal] = None
    revenue: Decimal
    created_at: datetime = Field(default_factory=datetime.now)


class PeriodComparison(BaseModel):
    """Model for period-over-period comparison analysis"""
    
    metric_name: str
    current_period_value: Optional[Decimal] = None
    previous_period_value: Optional[Decimal] = None
    absolute_change: Optional[Decimal] = None
    percent_change: Optional[Decimal] = None
    period_start: date
    period_end: date


# Helper functions for KPI calculations
def calculate_cac(spend: Decimal, conversions: int) -> Optional[Decimal]:
    """Calculate Customer Acquisition Cost"""
    if conversions > 0:
        return spend / conversions
    return None


def calculate_roas(revenue: Decimal, spend: Decimal) -> Optional[Decimal]:
    """Calculate Return on Ad Spend"""
    if spend > 0:
        return revenue / spend
    return None


def calculate_revenue(conversions: int, revenue_per_conversion: Decimal = Decimal('100')) -> Decimal:
    """Calculate revenue from conversions"""
    return Decimal(conversions) * revenue_per_conversion


# Enum-like constants for validation
VALID_PLATFORMS = {'Meta', 'Google'}
VALID_DEVICES = {'Desktop', 'Mobile'}
VALID_COUNTRIES = {'US', 'CA', 'BR', 'MX'}


class PlatformType:
    """Platform type constants"""
    META = "Meta"
    GOOGLE = "Google"


class DeviceType:
    """Device type constants"""
    DESKTOP = "Desktop"
    MOBILE = "Mobile"