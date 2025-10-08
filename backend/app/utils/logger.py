import logging
import structlog
from typing import Dict, Any
import sys
from datetime import datetime

def setup_logging(log_level: str = "INFO") -> None:
    """Setup structured logging for the application"""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard logging
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

class APILogger:
    """Logger for API requests and responses"""
    
    def __init__(self):
        self.logger = get_logger("api")
    
    def log_request(self, method: str, path: str, user_id: str = None, **kwargs):
        """Log API request"""
        self.logger.info(
            "API request",
            method=method,
            path=path,
            user_id=user_id,
            **kwargs
        )
    
    def log_response(self, method: str, path: str, status_code: int, 
                    response_time_ms: float, user_id: str = None, **kwargs):
        """Log API response"""
        self.logger.info(
            "API response",
            method=method,
            path=path,
            status_code=status_code,
            response_time_ms=response_time_ms,
            user_id=user_id,
            **kwargs
        )
    
    def log_error(self, method: str, path: str, error: str, 
                 user_id: str = None, **kwargs):
        """Log API error"""
        self.logger.error(
            "API error",
            method=method,
            path=path,
            error=error,
            user_id=user_id,
            **kwargs
        )

class AnalysisLogger:
    """Logger for analysis operations"""
    
    def __init__(self):
        self.logger = get_logger("analysis")
    
    def log_analysis_start(self, filename: str, file_size: int, user_id: str = None):
        """Log start of analysis"""
        self.logger.info(
            "Analysis started",
            filename=filename,
            file_size=file_size,
            user_id=user_id
        )
    
    def log_analysis_complete(self, filename: str, records_processed: int, 
                            anomalies_found: int, user_id: str = None):
        """Log completion of analysis"""
        self.logger.info(
            "Analysis completed",
            filename=filename,
            records_processed=records_processed,
            anomalies_found=anomalies_found,
            user_id=user_id
        )
    
    def log_analysis_error(self, filename: str, error: str, user_id: str = None):
        """Log analysis error"""
        self.logger.error(
            "Analysis failed",
            filename=filename,
            error=error,
            user_id=user_id
        )

# Global logger instances
api_logger = APILogger()
analysis_logger = AnalysisLogger()
