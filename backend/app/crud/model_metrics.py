"""
CRUD operations for model metrics
"""
from sqlalchemy.orm import Session
from app.db.models import ModelMetrics
from typing import List, Optional, Dict, Any
from datetime import datetime

def create_model_metric(
    db: Session,
    model_name: str,
    model_version: str,
    metric_name: str,
    metric_value: float,
    dataset_info: Dict[str, Any] = None
) -> ModelMetrics:
    """Create a new model metric record"""
    db_metric = ModelMetrics(
        model_name=model_name,
        model_version=model_version,
        metric_name=metric_name,
        metric_value=metric_value,
        dataset_info=dataset_info
    )
    
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_model_metrics(
    db: Session,
    model_name: Optional[str] = None,
    model_version: Optional[str] = None,
    metric_name: Optional[str] = None,
    limit: Optional[int] = 100
) -> List[ModelMetrics]:
    """Get model metrics with optional filters"""
    query = db.query(ModelMetrics)
    
    if model_name:
        query = query.filter(ModelMetrics.model_name == model_name)
    if model_version:
        query = query.filter(ModelMetrics.model_version == model_version)
    if metric_name:
        query = query.filter(ModelMetrics.metric_name == metric_name)
    
    query = query.order_by(ModelMetrics.evaluation_date.desc())
    
    if limit:
        query = query.limit(limit)
    
    return query.all()

def get_latest_metrics(
    db: Session,
    model_name: str,
    model_version: str = "latest"
) -> List[ModelMetrics]:
    """Get the latest metrics for a specific model"""
    return db.query(ModelMetrics)\
        .filter(
            ModelMetrics.model_name == model_name,
            ModelMetrics.model_version == model_version
        )\
        .order_by(ModelMetrics.evaluation_date.desc())\
        .all()