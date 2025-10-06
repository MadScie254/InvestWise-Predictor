"""
Model metrics endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.db.session import get_db
from app.crud.model_metrics import get_model_metrics, create_model_metric
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class ModelMetricResponse(BaseModel):
    """Model metric response"""
    id: int
    model_name: str
    model_version: str
    metric_name: str
    metric_value: float
    evaluation_date: datetime
    dataset_info: Optional[dict]

@router.get("/", response_model=List[ModelMetricResponse])
async def get_metrics(
    model_name: Optional[str] = None,
    model_version: Optional[str] = None,
    metric_name: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get model performance metrics
    """
    try:
        metrics = get_model_metrics(
            db=db,
            model_name=model_name,
            model_version=model_version,
            metric_name=metric_name,
            limit=limit
        )
        return metrics
        
    except Exception as e:
        logger.error(f"Error fetching model metrics: {e}")
        raise HTTPException(status_code=500, detail="Error fetching model metrics")

@router.get("/summary")
async def get_metrics_summary(db: Session = Depends(get_db)):
    """
    Get summary of model performance
    """
    try:
        # Get latest metrics for each model
        result = db.execute("""
            WITH latest_metrics AS (
                SELECT 
                    model_name,
                    model_version,
                    metric_name,
                    metric_value,
                    evaluation_date,
                    ROW_NUMBER() OVER (
                        PARTITION BY model_name, model_version, metric_name 
                        ORDER BY evaluation_date DESC
                    ) as rn
                FROM model_metrics
            )
            SELECT 
                model_name,
                model_version,
                metric_name,
                metric_value,
                evaluation_date
            FROM latest_metrics 
            WHERE rn = 1
            ORDER BY model_name, model_version, metric_name
        """).fetchall()
        
        summary = {}
        for row in result:
            model_key = f"{row[0]}:{row[1]}"
            if model_key not in summary:
                summary[model_key] = {
                    "model_name": row[0],
                    "model_version": row[1],
                    "metrics": {},
                    "last_evaluation": row[4]
                }
            
            summary[model_key]["metrics"][row[2]] = row[3]
        
        return {"models": list(summary.values())}
        
    except Exception as e:
        logger.error(f"Error getting metrics summary: {e}")
        return {"models": []}

@router.get("/performance")
async def get_model_performance(
    model_name: str,
    model_version: str = "latest",
    db: Session = Depends(get_db)
):
    """
    Get detailed performance metrics for a specific model
    """
    try:
        metrics = get_model_metrics(
            db=db,
            model_name=model_name,
            model_version=model_version,
            limit=None
        )
        
        if not metrics:
            raise HTTPException(
                status_code=404,
                detail=f"No metrics found for model {model_name}:{model_version}"
            )
        
        # Organize metrics by type
        performance = {
            "model_name": model_name,
            "model_version": model_version,
            "metrics": {},
            "evaluation_history": []
        }
        
        for metric in metrics:
            if metric.metric_name not in performance["metrics"]:
                performance["metrics"][metric.metric_name] = []
            
            performance["metrics"][metric.metric_name].append({
                "value": metric.metric_value,
                "date": metric.evaluation_date,
                "dataset_info": metric.dataset_info
            })
            
            performance["evaluation_history"].append({
                "metric_name": metric.metric_name,
                "metric_value": metric.metric_value,
                "evaluation_date": metric.evaluation_date
            })
        
        # Sort evaluation history by date
        performance["evaluation_history"].sort(
            key=lambda x: x["evaluation_date"], 
            reverse=True
        )
        
        return performance
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail="Error getting model performance")