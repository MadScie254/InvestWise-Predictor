"""
Prediction endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from pydantic import BaseModel, Field
import httpx
import asyncio
import time
from typing import Dict, Any, Optional
from app.core.config import settings
from app.db.session import get_db
from app.crud.predictions import create_prediction_history
from app.utils.rate_limiter import rate_limit
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class PredictionRequest(BaseModel):
    """Request model for predictions"""
    features: Dict[str, float] = Field(
        ..., 
        description="Feature dictionary with economic indicators",
        example={
            "gdp_growth_rate": 2.5,
            "inflation_rate": 5.2,
            "usd_kes_rate": 110.5,
            "cbr_rate": 9.0,
            "trade_balance": -12000.5
        }
    )
    model_version: Optional[str] = Field(
        default="latest",
        description="Model version to use for prediction"
    )

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: float = Field(..., description="Predicted value")
    confidence: Optional[float] = Field(None, description="Confidence score (0-1)")
    model_version: str = Field(..., description="Model version used")
    features_used: Dict[str, float] = Field(..., description="Features used in prediction")
    explanation: Optional[Dict[str, Any]] = Field(None, description="Model explanation")
    timestamp: str = Field(..., description="Prediction timestamp")

async def log_prediction_async(
    features: Dict[str, float],
    result: Dict[str, Any],
    user_id: Optional[str],
    db_session
):
    """Log prediction asynchronously"""
    try:
        create_prediction_history(
            db=db_session,
            input_features=features,
            prediction_result=result,
            user_id=user_id
        )
    except Exception as e:
        logger.error(f"Failed to log prediction: {e}")

@router.post("/", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest,
    background_tasks: BackgroundTasks,
    req: Request,
    db=Depends(get_db)
):
    """
    Generate investment predictions based on economic indicators
    
    This endpoint validates input features and forwards them to the ML service.
    It includes rate limiting, logging, and error handling.
    """
    # Rate limiting
    if not await rate_limit(req.client.host, settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    start_time = time.time()
    
    try:
        # Validate required features
        required_features = [
            "gdp_growth_rate", "inflation_rate", "usd_kes_rate", 
            "cbr_rate", "trade_balance"
        ]
        
        missing_features = [f for f in required_features if f not in request.features]
        if missing_features:
            raise HTTPException(
                status_code=422,
                detail=f"Missing required features: {missing_features}"
            )
        
        # Call ML service
        ml_service_url = f"{settings.ML_SERVICE_URL}/predict"
        payload = {
            "features": request.features,
            "model_version": request.model_version
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(ml_service_url, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"ML service error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=503,
                        detail="Prediction service temporarily unavailable"
                    )
                
                ml_result = response.json()
                
            except httpx.TimeoutException:
                logger.error("ML service timeout")
                raise HTTPException(
                    status_code=504,
                    detail="Prediction service timeout"
                )
            except httpx.RequestError as e:
                logger.error(f"ML service connection error: {e}")
                raise HTTPException(
                    status_code=503,
                    detail="Cannot connect to prediction service"
                )
        
        # Prepare response
        prediction_response = PredictionResponse(
            prediction=ml_result.get("prediction", 0.0),
            confidence=ml_result.get("confidence"),
            model_version=ml_result.get("model_version", request.model_version),
            features_used=request.features,
            explanation=ml_result.get("explanation"),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        )
        
        # Log prediction in background
        user_id = getattr(req.state, 'user_id', None)
        background_tasks.add_task(
            log_prediction_async,
            request.features,
            prediction_response.dict(),
            user_id,
            db
        )
        
        # Log performance metrics
        processing_time = time.time() - start_time
        logger.info(
            f"Prediction completed in {processing_time:.3f}s - "
            f"Result: {prediction_response.prediction}"
        )
        
        return prediction_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Unexpected error in prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during prediction"
        )

@router.get("/models")
async def list_available_models():
    """
    List available prediction models and their versions
    """
    try:
        ml_service_url = f"{settings.ML_SERVICE_URL}/models"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(ml_service_url)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "models": [
                        {
                            "name": "investwise_model",
                            "version": "latest",
                            "status": "available"
                        }
                    ]
                }
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return {
            "models": [
                {
                    "name": "investwise_model", 
                    "version": "latest",
                    "status": "unknown"
                }
            ]
        }