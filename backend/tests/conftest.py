import pytest
import asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.main import app
from app.core.config import settings
from app.db.database import get_db
from app.db.models import User, Prediction, MarketData
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """Test client for FastAPI app"""
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client():
    """Async test client for FastAPI app"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def db_session():
    """Database session for testing"""
    from app.db.models import Base
    Base.metadata.create_all(bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_user(db_session: Session):
    """Create a mock user for testing"""
    user = User(
        email="test@example.com",
        username="testuser",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # secret
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(client, mock_user):
    """Authentication headers for testing"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "test@example.com",
            "password": "secret"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def mock_ml_service():
    """Mock ML service responses"""
    with patch('app.utils.ml_client.predict') as mock_predict, \
         patch('app.utils.ml_client.explain') as mock_explain, \
         patch('app.utils.ml_client.health_check') as mock_health:
        
        # Mock predict response
        mock_predict.return_value = {
            "prediction": 1250.75,
            "confidence": 0.85,
            "model_version": "v1.0.0",
            "features_used": ["gdp_growth", "inflation_rate", "exchange_rate"]
        }
        
        # Mock explain response
        mock_explain.return_value = {
            "shap_values": {
                "gdp_growth": 0.15,
                "inflation_rate": -0.08,
                "exchange_rate": 0.03
            },
            "feature_importance": {
                "gdp_growth": 0.45,
                "inflation_rate": 0.35,
                "exchange_rate": 0.20
            }
        }
        
        # Mock health check
        mock_health.return_value = {"status": "healthy"}
        
        yield {
            "predict": mock_predict,
            "explain": mock_explain,
            "health": mock_health
        }

@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        "gdp_growth": 5.2,
        "inflation_rate": 7.8,
        "exchange_rate": 110.5,
        "interest_rate": 9.0,
        "unemployment_rate": 14.2,
        "mobile_money_transactions": 1500000,
        "trade_balance": -250000
    }

@pytest.fixture
def sample_prediction_request():
    """Sample prediction request for testing"""
    return {
        "features": {
            "gdp_growth": 5.2,
            "inflation_rate": 7.8,
            "exchange_rate": 110.5,
            "interest_rate": 9.0,
            "unemployment_rate": 14.2,
            "mobile_money_transactions": 1500000,
            "trade_balance": -250000
        },
        "model_type": "lightgbm",
        "prediction_horizon": 30
    }