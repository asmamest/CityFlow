"""Logger centralisé pour l'API Gateway"""
import logging
import sys
from datetime import datetime
from pythonjsonlogger import jsonlogger
from  config import settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Formateur JSON personnalisé"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['service'] = 'api-gateway'

def setup_logger():
    """Configure le logger principal"""
    logger = logging.getLogger("gateway")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Handler pour stdout
    handler = logging.StreamHandler(sys.stdout)
    
    if settings.LOG_FORMAT == "json":
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Instance globale
logger = setup_logger()

def log_request(method: str, url: str, status_code: int = None, duration: float = None):
    """Log une requête HTTP"""
    logger.info(
        "HTTP Request",
        extra={
            "method": method,
            "url": url,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2) if duration else None
        }
    )

def log_error(service: str, error: Exception, context: dict = None):
    """Log une erreur"""
    logger.error(
        f"Error in {service}",
        extra={
            "service": service,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {}
        },
        exc_info=True
    )