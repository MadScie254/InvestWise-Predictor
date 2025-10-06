"""
ML Service FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import uvicorn
import time
import logging
from typing import Dict, List, Optional, Any
from app.model_loader import ModelManager
from app.explainers import ExplainerManager
from prometheus_client import Counter, Histogram, generate_latest
from fastapi.responses import Response
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
PREDICTION_COUNTER = Counter('predictions_total', 'Total number of predictions made')
PREDICTION_DURATION = Histogram('prediction_duration_seconds', 'Time spent on predictions')
ERROR_COUNTER = Counter('prediction_errors_total', 'Total number of prediction errors', ['error_type'])

app = FastAPI(
    title="InvestWise ML Service",
    description="Machine Learning prediction service for investment decisions",
    version="1.0.0"
)

# Initialize model and explainer managers
model_manager = ModelManager()
explainer_manager = ExplainerManager()

class PredictionRequest(BaseModel):
    """Prediction request schema"""
    features: Dict[str, float] = Field(
        ..., 
        description="Feature dictionary with economic indicators"
    )
    model_version: str = Field(
        default="latest",
        description="Model version to use"
    )
    explain: bool = Field(
        default=False,
        description="Whether to include SHAP explanations"
    )

class PredictionResponse(BaseModel):
    """Prediction response schema"""
    prediction: float = Field(..., description="Predicted value")
    confidence: Optional[float] = Field(None, description="Confidence score")
    model_version: str = Field(..., description="Model version used")
    features_used: Dict[str, float] = Field(..., description="Input features")
    explanation: Optional[Dict[str, Any]] = Field(None, description="SHAP explanation")
    processing_time: float = Field(..., description="Processing time in seconds")

class ModelInfo(BaseModel):
    """Model information schema"""
    name: str
    version: str
    status: str
    last_updated: Optional[str]
    metrics: Optional[Dict[str, float]]

@app.on_event("startup")
async def startup_event():
    """Initialize models on startup"""
    logger.info("Starting ML service...")
    try:
        model_manager.load_default_model()
        logger.info("ML service ready")
    except Exception as e:
        logger.error(f"Failed to load models: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "InvestWise ML Service",
        "version": "1.0.0",
        "status": "ready"
    }

@app.get("/healthz")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if model is loaded
        model_status = "healthy" if model_manager.is_model_loaded() else "no_model"
        
        return {
            "status": "healthy",
            "model_status": model_status,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Generate predictions using the loaded ML model
    """
    start_time = time.time()
    
    try:
        # Validate features
        required_features = ["gdp_growth_rate", "inflation_rate", "usd_kes_rate", "cbr_rate", "trade_balance"]
        missing_features = [f for f in required_features if f not in request.features]
        
        if missing_features:
            ERROR_COUNTER.labels(error_type='missing_features').inc()
            raise HTTPException(
                status_code=422,
                detail=f"Missing required features: {missing_features}"
            )
        
        # Get model
        model = model_manager.get_model(request.model_version)
        if model is None:
            ERROR_COUNTER.labels(error_type='model_not_found').inc()
            raise HTTPException(
                status_code=404,
                detail=f"Model version {request.model_version} not found"
            )
        
        # Prepare features in correct order
        feature_order = ["gdp_growth_rate", "inflation_rate", "usd_kes_rate", "cbr_rate", "trade_balance"]
        X = [[request.features[f] for f in feature_order]]
        
        # Make prediction
        with PREDICTION_DURATION.time():
            prediction = model.predict(X)[0]
            
            # Calculate confidence if model supports it
            confidence = None
            if hasattr(model, 'predict_proba'):
                try:
                    proba = model.predict_proba(X)[0]
                    confidence = float(max(proba))
                except:
                    pass
        
        # Generate explanation if requested
        explanation = None
        if request.explain:
            try:
                explanation = explainer_manager.explain_prediction(
                    model, X[0], feature_order
                )
            except Exception as e:
                logger.warning(f"Explanation generation failed: {e}")
        
        processing_time = time.time() - start_time
        
        # Update metrics
        PREDICTION_COUNTER.inc()
        
        response = PredictionResponse(
            prediction=float(prediction),
            confidence=confidence,
            model_version=request.model_version,
            features_used=request.features,
            explanation=explanation,
            processing_time=processing_time
        )
        
        logger.info(f"Prediction completed: {prediction:.4f} (took {processing_time:.3f}s)")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        ERROR_COUNTER.labels(error_type='prediction_error').inc()
        logger.exception(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail="Prediction failed")

@app.get("/models", response_model=List[ModelInfo])
async def list_models():
    """List available models"""
    try:
        models = model_manager.list_models()
        return models
    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return []

@app.post("/models/{model_version}/load")
async def load_model(model_version: str):
    """Load a specific model version"""
    try:
        success = model_manager.load_model(model_version)
        if success:
            return {"message": f"Model {model_version} loaded successfully"}
        else:
            raise HTTPException(status_code=404, detail="Model not found")
    except Exception as e:
        logger.error(f"Error loading model {model_version}: {e}")
        raise HTTPException(status_code=500, detail="Model loading failed")

@app.get("/features")
async def get_feature_info():
    """Get information about expected features"""
    return {
        "required_features": [
            {
                "name": "gdp_growth_rate",
                "description": "GDP growth rate as percentage",
                "type": "float",
                "range": [-10.0, 20.0]
            },
            {
                "name": "inflation_rate", 
                "description": "Inflation rate as percentage",
                "type": "float",
                "range": [0.0, 50.0]
            },
            {
                "name": "usd_kes_rate",
                "description": "USD to KES exchange rate",
                "type": "float", 
                "range": [50.0, 200.0]
            },
            {
                "name": "cbr_rate",
                "description": "Central Bank Rate as percentage",
                "type": "float",
                "range": [0.0, 30.0]
            },
            {
                "name": "trade_balance",
                "description": "Trade balance in millions",
                "type": "float",
                "range": [-100000.0, 100000.0]
            }
        ]
    }

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("ENVIRONMENT") == "development"
    )