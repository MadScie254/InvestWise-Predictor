"""
API v1 router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import predict, auth, health, data, metrics

router = APIRouter()

# Include all endpoint routers
router.include_router(health.router, prefix="/health", tags=["Health"])
router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(predict.router, prefix="/predict", tags=["Predictions"])
router.include_router(data.router, prefix="/data", tags=["Market Data"])
router.include_router(metrics.router, prefix="/metrics", tags=["Model Metrics"])