"""
Configuration management for ChainGuard AI
"""

import os
from typing import List, Optional, Dict, Any
from pydantic import BaseSettings, validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "ChainGuard AI"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Server
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    WORKERS: int = Field(default=1, env="WORKERS")
    
    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    CORS_ORIGINS: List[str] = Field(default=["http://localhost:3000"], env="CORS_ORIGINS")
    
    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_POOL_SIZE: int = Field(default=10, env="REDIS_POOL_SIZE")
    REDIS_POOL_TIMEOUT: int = Field(default=30, env="REDIS_POOL_TIMEOUT")
    
    # Celery
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0", env="CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0", env="CELERY_RESULT_BACKEND")
    CELERY_TASK_SERIALIZER: str = Field(default="json", env="CELERY_TASK_SERIALIZER")
    CELERY_RESULT_SERIALIZER: str = Field(default="json", env="CELERY_RESULT_SERIALIZER")
    CELERY_ACCEPT_CONTENT: List[str] = Field(default=["json"], env="CELERY_ACCEPT_CONTENT")
    CELERY_TIMEZONE: str = Field(default="UTC", env="CELERY_TIMEZONE")
    CELERY_ENABLE_UTC: bool = Field(default=True, env="CELERY_ENABLE_UTC")
    CELERY_TASK_TRACK_STARTED: bool = Field(default=True, env="CELERY_TASK_TRACK_STARTED")
    CELERY_TASK_TIME_LIMIT: int = Field(default=30 * 60, env="CELERY_TASK_TIME_LIMIT")  # 30 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = Field(default=25 * 60, env="CELERY_TASK_SOFT_TIME_LIMIT")  # 25 minutes
    
    # AI/ML Services
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4", env="OPENAI_MODEL")
    OPENAI_MAX_TOKENS: int = Field(default=4000, env="OPENAI_MAX_TOKENS")
    OPENAI_TEMPERATURE: float = Field(default=0.1, env="OPENAI_TEMPERATURE")
    
    ANTHROPIC_API_KEY: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    ANTHROPIC_MODEL: str = Field(default="claude-3-sonnet-20240229", env="ANTHROPIC_MODEL")
    ANTHROPIC_MAX_TOKENS: int = Field(default=4000, env="ANTHROPIC_MAX_TOKENS")
    
    LANGSMITH_API_KEY: Optional[str] = Field(default=None, env="LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: str = Field(default="chainguard-ai", env="LANGSMITH_PROJECT")
    LANGSMITH_ENDPOINT: str = Field(default="https://api.smith.langchain.com", env="LANGSMITH_ENDPOINT")
    
    # Vector Database
    VECTOR_DB_URL: str = Field(default="postgresql://localhost/chainguard_vectors", env="VECTOR_DB_URL")
    VECTOR_DIMENSION: int = Field(default=1536, env="VECTOR_DIMENSION")  # OpenAI embedding dimension
    
    # Web3 and Blockchain
    ETHEREUM_RPC_URL: str = Field(default="https://eth-mainnet.alchemyapi.io/v2/your-api-key", env="ETHEREUM_RPC_URL")
    POLYGON_RPC_URL: str = Field(default="https://polygon-mainnet.alchemyapi.io/v2/your-api-key", env="POLYGON_RPC_URL")
    BSC_RPC_URL: str = Field(default="https://bsc-dataseed.binance.org", env="BSC_RPC_URL")
    
    ETHERSCAN_API_KEY: Optional[str] = Field(default=None, env="ETHERSCAN_API_KEY")
    POLYGONSCAN_API_KEY: Optional[str] = Field(default=None, env="POLYGONSCAN_API_KEY")
    BSCSCAN_API_KEY: Optional[str] = Field(default=None, env="BSCSCAN_API_KEY")
    
    # Security Tools
    SLITHER_TIMEOUT: int = Field(default=300, env="SLITHER_TIMEOUT")  # 5 minutes
    MYTHRIL_TIMEOUT: int = Field(default=600, env="MYTHRIL_TIMEOUT")  # 10 minutes
    MANTICORE_TIMEOUT: int = Field(default=1800, env="MANTICORE_TIMEOUT")  # 30 minutes
    FOUNDRY_TIMEOUT: int = Field(default=900, env="FOUNDRY_TIMEOUT")  # 15 minutes
    
    # File Storage
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")  # local, s3, gcs
    STORAGE_PATH: str = Field(default="./storage", env="STORAGE_PATH")
    
    # AWS S3 (if using S3 storage)
    AWS_ACCESS_KEY_ID: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(default="us-east-1", env="AWS_REGION")
    AWS_S3_BUCKET: Optional[str] = Field(default=None, env="AWS_S3_BUCKET")
    
    # Google Cloud Storage (if using GCS storage)
    GOOGLE_CLOUD_PROJECT: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT")
    GOOGLE_CLOUD_BUCKET: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_BUCKET")
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    
    # Monitoring and Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    
    # Sentry
    SENTRY_DSN: Optional[str] = Field(default=None, env="SENTRY_DSN")
    SENTRY_ENVIRONMENT: str = Field(default="development", env="SENTRY_ENVIRONMENT")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")
    
    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = Field(
        default={
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
        },
        env="SECURITY_HEADERS"
    )
    
    # Analysis Settings
    MAX_FILE_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_FILE_SIZE")  # 100MB
    MAX_PROJECT_SIZE: int = Field(default=1 * 1024 * 1024 * 1024, env="MAX_PROJECT_SIZE")  # 1GB
    MAX_CONCURRENT_ANALYSES: int = Field(default=10, env="MAX_CONCURRENT_ANALYSES")
    ANALYSIS_TIMEOUT: int = Field(default=3600, env="ANALYSIS_TIMEOUT")  # 1 hour
    
    # Retention Policy
    PROJECT_RETENTION_DAYS: int = Field(default=365, env="PROJECT_RETENTION_DAYS")
    RUN_RETENTION_DAYS: int = Field(default=90, env="RUN_RETENTION_DAYS")
    ARTIFACT_RETENTION_DAYS: int = Field(default=30, env="ARTIFACT_RETENTION_DAYS")
    
    # Email Settings
    SMTP_HOST: Optional[str] = Field(default=None, env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: Optional[str] = Field(default=None, env="SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = Field(default=None, env="SMTP_PASSWORD")
    SMTP_TLS: bool = Field(default=True, env="SMTP_TLS")
    FROM_EMAIL: str = Field(default="noreply@chainguard.ai", env="FROM_EMAIL")
    FROM_NAME: str = Field(default="ChainGuard AI", env="FROM_NAME")
    
    # Slack Integration
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET: Optional[str] = Field(default=None, env="SLACK_SIGNING_SECRET")
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    
    # GitHub Integration
    GITHUB_APP_ID: Optional[str] = Field(default=None, env="GITHUB_APP_ID")
    GITHUB_PRIVATE_KEY: Optional[str] = Field(default=None, env="GITHUB_PRIVATE_KEY")
    GITHUB_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="GITHUB_WEBHOOK_SECRET")
    
    # GitLab Integration
    GITLAB_URL: Optional[str] = Field(default=None, env="GITLAB_URL")
    GITLAB_ACCESS_TOKEN: Optional[str] = Field(default=None, env="GITLAB_ACCESS_TOKEN")
    GITLAB_WEBHOOK_SECRET: Optional[str] = Field(default=None, env="GITLAB_WEBHOOK_SECRET")
    
    # Container Settings
    DOCKER_HOST: str = Field(default="unix://var/run/docker.sock", env="DOCKER_HOST")
    CONTAINER_MEMORY_LIMIT: str = Field(default="2g", env="CONTAINER_MEMORY_LIMIT")
    CONTAINER_CPU_LIMIT: str = Field(default="1.0", env="CONTAINER_CPU_LIMIT")
    CONTAINER_TIMEOUT: int = Field(default=1800, env="CONTAINER_TIMEOUT")  # 30 minutes
    
    # Feature Flags
    ENABLE_AI_EXPLANATIONS: bool = Field(default=True, env="ENABLE_AI_EXPLANATIONS")
    ENABLE_AUTO_PATCHES: bool = Field(default=True, env="ENABLE_AUTO_PATCHES")
    ENABLE_SYMBOLIC_EXECUTION: bool = Field(default=True, env="ENABLE_SYMBOLIC_EXECUTION")
    ENABLE_FUZZING: bool = Field(default=True, env="ENABLE_FUZZING")
    ENABLE_GAS_ANALYSIS: bool = Field(default=True, env="ENABLE_GAS_ANALYSIS")
    ENABLE_UPGRADE_SAFETY: bool = Field(default=True, env="ENABLE_UPGRADE_SAFETY")
    
    # Performance
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # 1 hour
    SESSION_TIMEOUT_MINUTES: int = Field(default=480, env="SESSION_TIMEOUT_MINUTES")  # 8 hours
    MAX_UPLOAD_SIZE: int = Field(default=100 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 100MB
    
    # Development
    RELOAD_ON_CHANGE: bool = Field(default=True, env="RELOAD_ON_CHANGE")
    ENABLE_DEBUG_TOOLBAR: bool = Field(default=False, env="ENABLE_DEBUG_TOOLBAR")
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("SECURITY_HEADERS", pre=True)
    def parse_security_headers(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create settings instance
settings = Settings()

# Validate critical settings
def validate_settings():
    """Validate critical settings"""
    if not settings.SECRET_KEY:
        raise ValueError("SECRET_KEY must be set")
    
    if settings.ENVIRONMENT == "production":
        if not settings.DATABASE_URL:
            raise ValueError("DATABASE_URL must be set in production")
        
        if not settings.REDIS_URL:
            raise ValueError("REDIS_URL must be set in production")
        
        if not settings.OPENAI_API_KEY and not settings.ANTHROPIC_API_KEY:
            raise ValueError("At least one AI API key must be set in production")


# Validate settings on import
validate_settings()
