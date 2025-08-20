"""
ChainGuard AI - Smart Contract Analysis & Security Auditor
Main FastAPI application entry point
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from prometheus_fastapi_instrumentator import Instrumentator
import structlog
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.security import get_current_user_optional
from app.core.middleware import (
    RequestLoggingMiddleware,
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    TenantMiddleware,
)
from app.core.health import health_check_router
from app.core.metrics import metrics_router

# Setup logging
setup_logging()
logger = structlog.get_logger(__name__)

# Initialize Sentry if configured
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ChainGuard AI application")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize Redis connections
    from app.core.cache import init_redis
    await init_redis()
    logger.info("Redis initialized")
    
    # Initialize AI/ML services
    from app.core.ai import init_ai_services
    await init_ai_services()
    logger.info("AI services initialized")
    
    # Initialize security tools
    from app.core.tools import init_security_tools
    await init_security_tools()
    logger.info("Security tools initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChainGuard AI application")
    await close_db()
    logger.info("Application shutdown complete")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    
    app = FastAPI(
        title="ChainGuard AI",
        description="Smart Contract Analysis & Security Auditor",
        version="1.0.0",
        docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
        openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
        lifespan=lifespan,
    )
    
    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantMiddleware)
    
    # Add exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    # Add routes
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(health_check_router, prefix="/health", tags=["health"])
    app.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
    
    # Add Prometheus metrics
    if settings.ENABLE_METRICS:
        Instrumentator().instrument(app).expose(app, include_in_schema=False)
    
    # Add root endpoint
    @app.get("/", tags=["root"])
    async def root(request: Request) -> Dict[str, Any]:
        """Root endpoint with basic application info"""
        user = await get_current_user_optional(request)
        return {
            "name": "ChainGuard AI",
            "version": "1.0.0",
            "description": "Smart Contract Analysis & Security Auditor",
            "status": "operational",
            "environment": settings.ENVIRONMENT,
            "user": user.email if user else None,
            "docs": "/docs" if settings.ENVIRONMENT != "production" else None,
        }
    
    # Add security endpoint
    @app.get("/security", tags=["security"])
    async def security_info() -> Dict[str, Any]:
        """Security information endpoint"""
        return {
            "security_headers": {
                "x_frame_options": "DENY",
                "x_content_type_options": "nosniff",
                "referrer_policy": "strict-origin-when-cross-origin",
                "permissions_policy": "camera=(), microphone=(), geolocation=()",
                "content_security_policy": "default-src 'self'",
            },
            "authentication": {
                "type": "JWT",
                "refresh_tokens": True,
                "session_timeout": f"{settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            },
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": settings.RATE_LIMIT_PER_MINUTE,
            },
            "data_protection": {
                "encryption_at_rest": True,
                "encryption_in_transit": True,
                "tenant_isolation": True,
                "audit_logging": True,
            },
        }
    
    return app


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions"""
    logger.warning(
        "HTTP exception",
        status_code=exc.status_code,
        detail=exc.detail,
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "type": "http_error",
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation exceptions"""
    logger.warning(
        "Validation error",
        errors=exc.errors(),
        path=request.url.path,
        method=request.method,
    )
    
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "type": "validation_error",
                "details": exc.errors(),
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(
        "Unhandled exception",
        exception=str(exc),
        exception_type=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        exc_info=True,
    )
    
    # Don't expose internal errors in production
    if settings.ENVIRONMENT == "production":
        message = "Internal server error"
    else:
        message = str(exc)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": message,
                "type": "internal_error",
            }
        },
    )


# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level="info",
    )
