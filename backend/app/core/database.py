"""
Database connection and session management for ChainGuard AI
"""

import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import event, text
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    pool_timeout=settings.DATABASE_POOL_TIMEOUT,
    pool_recycle=settings.DATABASE_POOL_RECYCLE,
    pool_pre_ping=True,
    future=True,
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create sync session factory for migrations
SessionLocal = sessionmaker(
    bind=engine.sync_engine,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Database session error", error=str(e))
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database connection and create tables"""
    try:
        # Test database connection
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        
        logger.info("Database connection established successfully")
        
        # Import all models to ensure they are registered
        from app.models.base import Base
        from app.models.user import User, Tenant, Role, Permission, RefreshToken, AuditLog, UserSession
        from app.models.project import Project, Contract, AnalysisRun, Finding, Artifact, CustomRule, AnalysisCheckpoint
        
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database tables created successfully")
        
        # Initialize system data
        await init_system_data()
        
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        raise


async def close_db() -> None:
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error("Error closing database connections", error=str(e))


async def init_system_data() -> None:
    """Initialize system data like default roles and permissions"""
    try:
        async with AsyncSessionLocal() as session:
            # Check if system data already exists
            existing_roles = await session.execute(
                text("SELECT COUNT(*) FROM role WHERE is_system = true")
            )
            if existing_roles.scalar() > 0:
                logger.info("System data already exists, skipping initialization")
                return
            
            # Create default permissions
            permissions = [
                {"name": "project:read", "description": "Read projects", "resource": "project", "action": "read"},
                {"name": "project:write", "description": "Create and update projects", "resource": "project", "action": "write"},
                {"name": "project:delete", "description": "Delete projects", "resource": "project", "action": "delete"},
                {"name": "analysis:read", "description": "Read analysis runs", "resource": "analysis", "action": "read"},
                {"name": "analysis:write", "description": "Create and update analysis runs", "resource": "analysis", "action": "write"},
                {"name": "analysis:delete", "description": "Delete analysis runs", "resource": "analysis", "action": "delete"},
                {"name": "finding:read", "description": "Read findings", "resource": "finding", "action": "read"},
                {"name": "finding:write", "description": "Create and update findings", "resource": "finding", "action": "write"},
                {"name": "finding:delete", "description": "Delete findings", "resource": "finding", "action": "delete"},
                {"name": "report:read", "description": "Read reports", "resource": "report", "action": "read"},
                {"name": "report:write", "description": "Create and update reports", "resource": "report", "action": "write"},
                {"name": "report:delete", "description": "Delete reports", "resource": "report", "action": "delete"},
                {"name": "user:read", "description": "Read users", "resource": "user", "action": "read"},
                {"name": "user:write", "description": "Create and update users", "resource": "user", "action": "write"},
                {"name": "user:delete", "description": "Delete users", "resource": "user", "action": "delete"},
                {"name": "tenant:read", "description": "Read tenant settings", "resource": "tenant", "action": "read"},
                {"name": "tenant:write", "description": "Update tenant settings", "resource": "tenant", "action": "write"},
            ]
            
            for perm_data in permissions:
                perm = Permission(**perm_data, is_system=True)
                session.add(perm)
            
            await session.commit()
            
            # Create default roles
            from app.models.user import Role
            
            system_roles = Role.get_system_roles()
            for role_data in system_roles:
                role = Role(
                    name=role_data["name"],
                    description=role_data["description"],
                    permissions=role_data["permissions"],
                    is_system=True
                )
                session.add(role)
            
            await session.commit()
            
            logger.info("System data initialized successfully")
            
    except Exception as e:
        logger.error("Failed to initialize system data", error=str(e))
        raise


async def get_db_session() -> AsyncSession:
    """Get a database session"""
    return AsyncSessionLocal()


async def execute_in_transaction(func, *args, **kwargs):
    """Execute a function within a database transaction"""
    async with AsyncSessionLocal() as session:
        async with session.begin():
            try:
                result = await func(session, *args, **kwargs)
                return result
            except Exception as e:
                await session.rollback()
                logger.error("Transaction failed", error=str(e))
                raise


# Database health check
async def check_db_health() -> bool:
    """Check database health"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False


# Database metrics
async def get_db_metrics() -> dict:
    """Get database metrics"""
    try:
        async with engine.begin() as conn:
            # Get connection pool stats
            pool_stats = engine.pool.status()
            
            # Get database size
            size_result = await conn.execute(
                text("SELECT pg_size_pretty(pg_database_size(current_database()))")
            )
            db_size = size_result.scalar()
            
            # Get table counts
            table_counts = {}
            tables = ["user", "project", "analysisrun", "finding", "artifact"]
            for table in tables:
                count_result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                table_counts[table] = count_result.scalar()
            
            return {
                "pool_size": pool_stats.size,
                "checked_in": pool_stats.checkedin,
                "checked_out": pool_stats.checkedout,
                "overflow": pool_stats.overflow,
                "invalid": pool_stats.invalid,
                "database_size": db_size,
                "table_counts": table_counts,
            }
    except Exception as e:
        logger.error("Failed to get database metrics", error=str(e))
        return {}


# Database maintenance
async def cleanup_expired_data() -> None:
    """Clean up expired data"""
    try:
        async with AsyncSessionLocal() as session:
            # Clean up expired refresh tokens
            await session.execute(
                text("DELETE FROM refreshtoken WHERE expires_at < NOW()")
            )
            
            # Clean up expired user sessions
            await session.execute(
                text("DELETE FROM usersession WHERE expires_at < NOW()")
            )
            
            # Clean up expired artifacts
            await session.execute(
                text("DELETE FROM artifact WHERE expires_at < NOW() AND expires_at IS NOT NULL")
            )
            
            await session.commit()
            logger.info("Expired data cleanup completed")
            
    except Exception as e:
        logger.error("Failed to cleanup expired data", error=str(e))


# Database backup
async def create_backup() -> str:
    """Create database backup"""
    try:
        import subprocess
        import os
        from datetime import datetime
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_file = f"{backup_dir}/chainguard_backup_{timestamp}.sql"
        
        # Extract database connection details
        db_url = settings.DATABASE_URL
        if db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgresql://", "")
        
        # Create backup using pg_dump
        cmd = [
            "pg_dump",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-privileges",
            f"--file={backup_file}",
            db_url
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_file}")
            return backup_file
        else:
            logger.error("Database backup failed", error=result.stderr)
            raise Exception("Backup failed")
            
    except Exception as e:
        logger.error("Failed to create database backup", error=str(e))
        raise


# Database migration helpers
async def run_migrations() -> None:
    """Run database migrations"""
    try:
        import alembic.config
        import alembic.command
        
        # Create Alembic configuration
        alembic_cfg = alembic.config.Config("alembic.ini")
        alembic_cfg.set_main_option("script_location", "alembic")
        alembic_cfg.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
        
        # Run migrations
        alembic.command.upgrade(alembic_cfg, "head")
        
        logger.info("Database migrations completed successfully")
        
    except Exception as e:
        logger.error("Failed to run database migrations", error=str(e))
        raise


# Database seeding
async def seed_test_data() -> None:
    """Seed test data for development"""
    if settings.ENVIRONMENT != "development":
        logger.info("Skipping test data seeding in non-development environment")
        return
    
    try:
        async with AsyncSessionLocal() as session:
            # Check if test data already exists
            existing_tenants = await session.execute(
                text("SELECT COUNT(*) FROM tenant WHERE name LIKE '%Test%'")
            )
            if existing_tenants.scalar() > 0:
                logger.info("Test data already exists, skipping seeding")
                return
            
            # Create test tenant
            from app.models.user import Tenant, User, Role
            
            test_tenant = Tenant(
                name="Test Organization",
                domain="test.chainguard.ai",
                description="Test organization for development",
                subscription_plan="pro",
                max_users=10,
                max_projects=50,
                max_storage_gb=10
            )
            session.add(test_tenant)
            await session.flush()
            
            # Create test user
            from app.core.security import get_password_hash
            
            admin_role = await session.execute(
                text("SELECT id FROM role WHERE name = 'admin'")
            )
            admin_role_id = admin_role.scalar()
            
            test_user = User(
                email="admin@test.chainguard.ai",
                username="testadmin",
                password_hash=get_password_hash("testpassword123"),
                first_name="Test",
                last_name="Admin",
                is_verified=True,
                tenant_id=test_tenant.id,
                created_by=test_tenant.id  # Self-reference for initial user
            )
            session.add(test_user)
            await session.flush()
            
            # Assign admin role to test user
            await session.execute(
                text("INSERT INTO user_roles (user_id, role_id, assigned_at, assigned_by) VALUES (:user_id, :role_id, NOW(), :assigned_by)"),
                {"user_id": test_user.id, "role_id": admin_role_id, "assigned_by": test_user.id}
            )
            
            await session.commit()
            logger.info("Test data seeded successfully")
            
    except Exception as e:
        logger.error("Failed to seed test data", error=str(e))
        raise
