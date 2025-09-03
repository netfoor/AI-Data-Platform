"""
Configuration management for AI Data Platform
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class DatabaseSettings(BaseSettings):
    """Database configuration settings"""
    path: str = Field(default="data/ai_data_platform.duckdb", description="Path to DuckDB database file")
    connection_timeout: int = Field(default=30, description="Database connection timeout in seconds")
    query_timeout: int = Field(default=300, description="Query execution timeout in seconds")
    
    class Config:
        env_prefix = "DB_"

class APISettings(BaseSettings):
    """API configuration settings"""
    host: str = Field(default="127.0.0.1", description="API server host")
    port: int = Field(default=8000, description="API server port")
    debug: bool = Field(default=False, description="Enable debug mode")
    reload: bool = Field(default=False, description="Enable auto-reload")
    workers: int = Field(default=1, description="Number of worker processes")
    
    class Config:
        env_prefix = "API_"

class N8nSettings(BaseSettings):
    """n8n workflow automation settings"""
    base_url: str = Field(default="http://localhost:5678", description="n8n local Docker instance URL")
    api_key: Optional[str] = Field(default=None, description="n8n API key for authentication")
    webhook_secret: Optional[str] = Field(default="ai-platform-secret-2024", description="Webhook secret for secure communication")
    workflow_id: Optional[str] = Field(default=None, description="ID of the data ingestion workflow")
    enable_automation: bool = Field(default=True, description="Enable n8n workflow automation")
    retry_attempts: int = Field(default=3, description="Number of retry attempts for failed workflows")
    retry_delay_seconds: int = Field(default=60, description="Delay between retry attempts in seconds")
    
    class Config:
        env_prefix = "N8N_"

class DataSettings(BaseSettings):
    """Data processing configuration settings"""
    input_directory: str = Field(default="data", description="Directory for input data files")
    output_directory: str = Field(default="data/processed", description="Directory for processed data")
    batch_size: int = Field(default=1000, description="Batch size for data processing")
    max_file_size_mb: int = Field(default=100, description="Maximum file size in MB")
    
    class Config:
        env_prefix = "DATA_"

class LoggingSettings(BaseSettings):
    """Logging configuration settings"""
    level: str = Field(default="INFO", description="Logging level")
    format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    file_path: Optional[str] = Field(default="logs/ai_data_platform.log", description="Log file path")
    max_file_size_mb: int = Field(default=10, description="Maximum log file size in MB")
    backup_count: int = Field(default=5, description="Number of backup log files to keep")
    
    class Config:
        env_prefix = "LOG_"

class Settings(BaseSettings):
    """Main application settings"""
    
    # Application metadata
    app_name: str = Field(default="AI Data Platform", description="Application name")
    version: str = Field(default="1.0.0", description="Application version")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # Component settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    api: APISettings = Field(default_factory=APISettings)
    n8n: N8nSettings = Field(default_factory=N8nSettings)
    data: DataSettings = Field(default_factory=DataSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    
    # Feature flags
    enable_api: bool = Field(default=True, description="Enable REST API")
    enable_natural_language: bool = Field(default=True, description="Enable natural language queries")
    enable_metrics_caching: bool = Field(default=False, description="Enable metrics result caching")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure required directories exist
        self._create_directories()
    
    def _create_directories(self):
        """Create required directories if they don't exist"""
        directories = [
            self.data.input_directory,
            self.data.output_directory,
            Path(self.database.path).parent if self.database.path != ":memory:" else None,
            Path(self.logging.file_path).parent if self.logging.file_path else None,
        ]
        
        for directory in directories:
            if directory:
                Path(directory).mkdir(parents=True, exist_ok=True)
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"

# Global settings instance
settings = Settings()