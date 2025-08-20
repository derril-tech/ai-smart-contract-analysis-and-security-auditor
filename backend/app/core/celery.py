"""
Celery configuration for ChainGuard AI
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "chainguard",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.analysis_tasks",
        "app.tasks.report_tasks",
        "app.tasks.cleanup_tasks",
        "app.tasks.notification_tasks",
    ]
)

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        "app.tasks.analysis_tasks.*": {"queue": "analysis"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
        "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
    },
    
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_always_eager=False,
    task_eager_propagates=True,
    task_ignore_result=False,
    task_store_errors_even_if_ignored=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=False,
    
    # Task time limits
    task_soft_time_limit=3600,  # 1 hour
    task_time_limit=7200,       # 2 hours
    
    # Result backend
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    
    # Beat schedule
    beat_schedule={
        "cleanup-old-data": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_data",
            "schedule": 86400.0,  # Daily
        },
        "update-project-stats": {
            "task": "app.tasks.analysis_tasks.update_project_statistics",
            "schedule": 3600.0,   # Hourly
        },
        "check-failed-runs": {
            "task": "app.tasks.analysis_tasks.check_failed_runs",
            "schedule": 300.0,    # Every 5 minutes
        },
    },
    
    # Security
    security_key=settings.SECRET_KEY,
    security_certificate=None,
    security_cert_store=None,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    event_queue_expires=60.0,
    event_queue_ttl=5.0,
    
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)

# Task annotations for specific tasks
celery_app.conf.task_annotations = {
    "app.tasks.analysis_tasks.run_security_analysis": {
        "rate_limit": "10/m",
        "time_limit": 7200,
        "soft_time_limit": 3600,
    },
    "app.tasks.analysis_tasks.run_slither_analysis": {
        "rate_limit": "30/m",
        "time_limit": 1800,
        "soft_time_limit": 900,
    },
    "app.tasks.analysis_tasks.run_mythril_analysis": {
        "rate_limit": "20/m",
        "time_limit": 3600,
        "soft_time_limit": 1800,
    },
    "app.tasks.analysis_tasks.run_echidna_analysis": {
        "rate_limit": "5/m",
        "time_limit": 7200,
        "soft_time_limit": 3600,
    },
    "app.tasks.report_tasks.generate_pdf_report": {
        "rate_limit": "10/m",
        "time_limit": 1800,
        "soft_time_limit": 900,
    },
}

# Task routing for different environments
if settings.ENVIRONMENT == "development":
    celery_app.conf.task_routes = {
        "*": {"queue": "default"},
    }
elif settings.ENVIRONMENT == "production":
    celery_app.conf.task_routes = {
        "app.tasks.analysis_tasks.*": {"queue": "analysis"},
        "app.tasks.report_tasks.*": {"queue": "reports"},
        "app.tasks.cleanup_tasks.*": {"queue": "cleanup"},
        "app.tasks.notification_tasks.*": {"queue": "notifications"},
        "*": {"queue": "default"},
    }

# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup"""
    print(f"Request: {self.request!r}")

# Task failure handling
@celery_app.task(bind=True)
def handle_task_failure(self, exc, task_id, args, kwargs, einfo):
    """Handle task failures"""
    from app.core.logging import logger
    
    logger.error(
        "Task failed",
        task_id=task_id,
        task_name=self.request.task,
        args=args,
        kwargs=kwargs,
        exception=str(exc),
        traceback=einfo.traceback,
    )

# Task success handling
@celery_app.task(bind=True)
def handle_task_success(self, retval, task_id, args, kwargs):
    """Handle task successes"""
    from app.core.logging import logger
    
    logger.info(
        "Task completed successfully",
        task_id=task_id,
        task_name=self.request.task,
        result=retval,
    )

# Register signal handlers
celery_app.conf.task_annotations = {
    "*": {
        "on_failure": handle_task_failure,
        "on_success": handle_task_success,
    }
}
