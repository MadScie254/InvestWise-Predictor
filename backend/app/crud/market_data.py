"""
CRUD operations for market data
"""
from sqlalchemy.orm import Session
from app.db.models import MarketData
from typing import List, Optional
from datetime import datetime, date

def create_market_data(
    db: Session,
    date: datetime,
    data_type: str,
    data_source: str,
    raw_data: dict,
    processed_data: dict = None
) -> MarketData:
    """Create new market data record"""
    db_data = MarketData(
        date=date,
        data_type=data_type,
        data_source=data_source,
        raw_data=raw_data,
        processed_data=processed_data
    )
    
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_market_data(
    db: Session,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100
) -> List[MarketData]:
    """Get market data with optional date filters"""
    query = db.query(MarketData)
    
    if start_date:
        query = query.filter(MarketData.date >= start_date)
    if end_date:
        query = query.filter(MarketData.date <= end_date)
    
    return query.order_by(MarketData.date.desc()).limit(limit).all()

def get_market_data_by_type(
    db: Session,
    data_type: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 100
) -> List[MarketData]:
    """Get market data filtered by type"""
    query = db.query(MarketData).filter(MarketData.data_type == data_type)
    
    if start_date:
        query = query.filter(MarketData.date >= start_date)
    if end_date:
        query = query.filter(MarketData.date <= end_date)
    
    return query.order_by(MarketData.date.desc()).limit(limit).all()

def get_latest_market_data(
    db: Session,
    data_type: str
) -> Optional[MarketData]:
    """Get the most recent data for a specific type"""
    return db.query(MarketData)\
        .filter(MarketData.data_type == data_type)\
        .order_by(MarketData.date.desc())\
        .first()