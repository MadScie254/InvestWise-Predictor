"""
CRUD operations for predictions
"""
from sqlalchemy.orm import Session
from app.db.models import PredictionHistory
from typing import Dict, Any, Optional, List

def create_prediction_history(
    db: Session,
    input_features: Dict[str, Any],
    prediction_result: Dict[str, Any],
    user_id: Optional[str] = None,
    model_version: str = "latest"
) -> PredictionHistory:
    """
    Create a new prediction history record
    """
    db_prediction = PredictionHistory(
        user_id=user_id,
        input_features=input_features,
        prediction_result=prediction_result,
        model_version=model_version,
        confidence_score=prediction_result.get("confidence")
    )
    
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

def get_prediction_history(
    db: Session,
    user_id: Optional[str] = None,
    limit: int = 100
) -> List[PredictionHistory]:
    """
    Get prediction history
    """
    query = db.query(PredictionHistory)
    
    if user_id:
        query = query.filter(PredictionHistory.user_id == user_id)
    
    return query.order_by(PredictionHistory.created_at.desc()).limit(limit).all()

def get_prediction_stats(db: Session) -> Dict[str, Any]:
    """
    Get prediction statistics
    """
    total_predictions = db.query(PredictionHistory).count()
    
    # Get prediction counts by day for the last 30 days
    result = db.execute("""
        SELECT 
            DATE(created_at) as prediction_date,
            COUNT(*) as count
        FROM prediction_history 
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY DATE(created_at)
        ORDER BY prediction_date DESC
    """).fetchall()
    
    daily_counts = [{"date": row[0], "count": row[1]} for row in result]
    
    return {
        "total_predictions": total_predictions,
        "daily_predictions": daily_counts
    }