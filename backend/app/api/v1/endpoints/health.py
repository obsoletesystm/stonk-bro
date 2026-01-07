"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.config import settings
from app.celery_app import celery_app
import redis

router = APIRouter()


@router.get("/")
async def health_check():
    """Simple health check"""
    return {"status": "ok"}


@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check including database and Redis"""
    health_status = {
        "app": settings.APP_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": "unknown",
        "redis": "unknown",
        "celery": "unknown"
    }

    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["database"] = "healthy"
    except Exception as e:
        health_status["database"] = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["redis"] = "healthy"
    except Exception as e:
        health_status["redis"] = f"unhealthy: {str(e)}"

    # Check Celery worker
    try:
        # Check if any workers are active
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        if active_workers:
            health_status["celery"] = "healthy"
        else:
            health_status["celery"] = "no workers found"
    except Exception as e:
        health_status["celery"] = f"unhealthy: {str(e)}"

    return health_status
