"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from app.db.session import get_db
from app.core.config import settings
import httpx
import redis
import time

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "InvestWise API",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

@router.get("/detailed")
async def detailed_health_check(db=Depends(get_db)):
    """Detailed health check including dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "dependencies": {}
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["dependencies"]["database"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["dependencies"]["redis"] = "healthy"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check ML Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.ML_SERVICE_URL}/healthz")
            if response.status_code == 200:
                health_status["dependencies"]["ml_service"] = "healthy"
            else:
                health_status["dependencies"]["ml_service"] = f"unhealthy: HTTP {response.status_code}"
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["dependencies"]["ml_service"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/ready")
async def readiness_check(db=Depends(get_db)):
    """Kubernetes readiness probe"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception:
        return {"status": "not ready"}, 503

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}