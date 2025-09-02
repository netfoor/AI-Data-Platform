"""
Logging utilities for AI Data Platform
"""
import logging
import logging.handlers
from pathlib import Path
from ai_data_platform.config import settings

def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    if settings.logging.file_path:
        log_file = Path(settings.logging.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.logging.level.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(settings.logging.format)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation
    if settings.logging.file_path:
        file_handler = logging.handlers.RotatingFileHandler(
            settings.logging.file_path,
            maxBytes=settings.logging.max_file_size_mb * 1024 * 1024,
            backupCount=settings.logging.backup_count
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)