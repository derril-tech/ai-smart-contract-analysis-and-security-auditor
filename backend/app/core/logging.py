"""
Logging configuration for ChainGuard AI
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

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
    logger_factory=LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Create logger instance
logger = structlog.get_logger(__name__)

# Configure standard library logging
def setup_logging(
    level: str = "INFO",
    format_string: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """Setup logging configuration"""
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("celery").setLevel(logging.INFO)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

# Logging middleware for FastAPI
class LoggingMiddleware:
    """Middleware to log HTTP requests and responses"""
    
    def __init__(self, app):
        self.app = app
        self.logger = structlog.get_logger("http")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # Log request
            self.logger.info(
                "HTTP request",
                method=scope["method"],
                path=scope["path"],
                client_ip=scope.get("client", ("unknown",))[0],
                user_agent=dict(scope.get("headers", [])).get(b"user-agent", b"").decode(),
            )
            
            # Track response
            response_status = None
            
            async def send_wrapper(message):
                nonlocal response_status
                if message["type"] == "http.response.start":
                    response_status = message["status"]
                await send(message)
            
            await self.app(scope, receive, send_wrapper)
            
            # Log response
            self.logger.info(
                "HTTP response",
                method=scope["method"],
                path=scope["path"],
                status=response_status,
            )
        else:
            await self.app(scope, receive, send)

# Structured logging for different components
def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger for a specific component"""
    return structlog.get_logger(name)

# Logging decorators
def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(
            "Function called",
            function=func.__name__,
            args=args,
            kwargs=kwargs,
        )
        try:
            result = func(*args, **kwargs)
            logger.info(
                "Function completed",
                function=func.__name__,
                result=result,
            )
            return result
        except Exception as e:
            logger.error(
                "Function failed",
                function=func.__name__,
                error=str(e),
                exception_type=type(e).__name__,
            )
            raise
    return wrapper

def log_async_function_call(func):
    """Decorator to log async function calls"""
    async def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        logger.info(
            "Async function called",
            function=func.__name__,
            args=args,
            kwargs=kwargs,
        )
        try:
            result = await func(*args, **kwargs)
            logger.info(
                "Async function completed",
                function=func.__name__,
                result=result,
            )
            return result
        except Exception as e:
            logger.error(
                "Async function failed",
                function=func.__name__,
                error=str(e),
                exception_type=type(e).__name__,
            )
            raise
    return wrapper

# Logging utilities
def log_security_event(
    event_type: str,
    user_id: str = None,
    tenant_id: str = None,
    details: Dict[str, Any] = None,
    ip_address: str = None,
    user_agent: str = None,
) -> None:
    """Log security-related events"""
    security_logger = get_logger("security")
    security_logger.warning(
        "Security event",
        event_type=event_type,
        user_id=user_id,
        tenant_id=tenant_id,
        details=details or {},
        ip_address=ip_address,
        user_agent=user_agent,
    )

def log_analysis_event(
    event_type: str,
    run_id: str = None,
    project_id: str = None,
    details: Dict[str, Any] = None,
) -> None:
    """Log analysis-related events"""
    analysis_logger = get_logger("analysis")
    analysis_logger.info(
        "Analysis event",
        event_type=event_type,
        run_id=run_id,
        project_id=project_id,
        details=details or {},
    )

def log_performance_metric(
    metric_name: str,
    value: float,
    unit: str = None,
    tags: Dict[str, str] = None,
) -> None:
    """Log performance metrics"""
    perf_logger = get_logger("performance")
    perf_logger.info(
        "Performance metric",
        metric_name=metric_name,
        value=value,
        unit=unit,
        tags=tags or {},
    )

# Initialize logging
setup_logging()
