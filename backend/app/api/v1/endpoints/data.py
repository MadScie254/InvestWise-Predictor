"""
Market data endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel
from app.db.session import get_db
from app.crud.market_data import get_market_data, get_market_data_by_type
from app.utils.data_processor import load_and_process_data
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class MarketDataResponse(BaseModel):
    """Market data response model"""
    id: int
    date: datetime
    data_type: str
    data_source: str
    processed_data: dict
    created_at: datetime

@router.get("/", response_model=List[MarketDataResponse])
async def get_data(
    data_type: Optional[str] = Query(None, description="Filter by data type (gdp, inflation, etc.)"),
    start_date: Optional[date] = Query(None, description="Start date filter"),
    end_date: Optional[date] = Query(None, description="End date filter"),
    limit: int = Query(100, le=1000, description="Maximum number of records"),
    db: Session = Depends(get_db)
):
    """
    Get market data with optional filters
    """
    try:
        if data_type:
            data = get_market_data_by_type(
                db=db,
                data_type=data_type,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        else:
            data = get_market_data(
                db=db,
                start_date=start_date,
                end_date=end_date,
                limit=limit
            )
        
        return data
        
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching market data")

@router.get("/types")
async def get_data_types(db: Session = Depends(get_db)):
    """
    Get available data types
    """
    try:
        # Query distinct data types from database
        result = db.execute(
            "SELECT DISTINCT data_type FROM market_data ORDER BY data_type"
        ).fetchall()
        
        data_types = [row[0] for row in result]
        
        # If no data in DB, return available types from data files
        if not data_types:
            data_types = [
                "gdp", "inflation", "exchange_rates", "interest_rates",
                "mobile_payments", "trade_foreign_summary"
            ]
        
        return {"data_types": data_types}
        
    except Exception as e:
        logger.error(f"Error fetching data types: {e}")
        return {"data_types": []}

@router.get("/summary")
async def get_data_summary(db: Session = Depends(get_db)):
    """
    Get summary statistics of available data
    """
    try:
        # Get data summary from database
        result = db.execute("""
            SELECT 
                data_type,
                COUNT(*) as count,
                MIN(date) as earliest_date,
                MAX(date) as latest_date
            FROM market_data 
            GROUP BY data_type
            ORDER BY data_type
        """).fetchall()
        
        summary = []
        for row in result:
            summary.append({
                "data_type": row[0],
                "record_count": row[1],
                "earliest_date": row[2],
                "latest_date": row[3]
            })
        
        return {"summary": summary}
        
    except Exception as e:
        logger.error(f"Error getting data summary: {e}")
        return {"summary": []}

@router.post("/refresh")
async def refresh_data(
    data_type: Optional[str] = Query(None, description="Specific data type to refresh"),
    db: Session = Depends(get_db)
):
    """
    Refresh market data from source files
    """
    try:
        result = load_and_process_data(db, data_type)
        return {
            "message": "Data refresh completed",
            "processed_types": result.get("processed_types", []),
            "total_records": result.get("total_records", 0)
        }
        
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        raise HTTPException(status_code=500, detail="Error refreshing data")

@router.get("/latest")
async def get_latest_data(
    data_type: str = Query(..., description="Data type to get latest data for"),
    db: Session = Depends(get_db)
):
    """
    Get the latest data point for a specific data type
    """
    try:
        latest_data = db.execute("""
            SELECT * FROM market_data 
            WHERE data_type = :data_type 
            ORDER BY date DESC 
            LIMIT 1
        """, {"data_type": data_type}).fetchone()
        
        if not latest_data:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for type: {data_type}"
            )
        
        return {
            "data_type": latest_data.data_type,
            "date": latest_data.date,
            "data": latest_data.processed_data or latest_data.raw_data,
            "source": latest_data.data_source
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching latest data")