import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
import pandas as pd
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.utils.ml_client import MLClient, predict, explain, health_check
from app.utils.rate_limiter import RateLimiter
from app.utils.data_processor import DataProcessor


class TestMLClient:
    """Test ML client functionality"""
    
    @pytest.fixture
    def ml_client(self):
        """ML client instance for testing"""
        return MLClient("http://test-ml-service:8001")
    
    @patch('app.utils.ml_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_predict_success(self, mock_client, ml_client):
        """Test successful prediction"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "prediction": 1250.75,
            "confidence": 0.85,
            "model_version": "v1.0.0"
        }
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        features = {"gdp_growth": 5.2, "inflation_rate": 7.8}
        result = await ml_client.predict(features)
        
        assert result["prediction"] == 1250.75
        assert result["confidence"] == 0.85
    
    @patch('app.utils.ml_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_predict_failure(self, mock_client, ml_client):
        """Test prediction failure"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        features = {"gdp_growth": 5.2}
        
        with pytest.raises(Exception):
            await ml_client.predict(features)
    
    @patch('app.utils.ml_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_explain_success(self, mock_client, ml_client):
        """Test successful explanation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "shap_values": {"gdp_growth": 0.15},
            "feature_importance": {"gdp_growth": 0.45}
        }
        
        mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
        
        features = {"gdp_growth": 5.2}
        result = await ml_client.explain(features)
        
        assert "shap_values" in result
        assert "feature_importance" in result
    
    @patch('app.utils.ml_client.httpx.AsyncClient')
    @pytest.mark.asyncio
    async def test_health_check_success(self, mock_client, ml_client):
        """Test successful health check"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        result = await ml_client.health_check()
        assert result["status"] == "healthy"


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.fixture
    def rate_limiter(self):
        """Rate limiter instance for testing"""
        return RateLimiter()
    
    @patch('app.utils.rate_limiter.redis_client')
    def test_rate_limit_not_exceeded(self, mock_redis, rate_limiter):
        """Test rate limit not exceeded"""
        mock_redis.get.return_value = b'5'  # 5 requests made
        mock_redis.ttl.return_value = 300  # 5 minutes remaining
        
        result = rate_limiter.check_rate_limit("user123", limit=100, window=3600)
        assert result is True
    
    @patch('app.utils.rate_limiter.redis_client')
    def test_rate_limit_exceeded(self, mock_redis, rate_limiter):
        """Test rate limit exceeded"""
        mock_redis.get.return_value = b'101'  # 101 requests made
        mock_redis.ttl.return_value = 300  # 5 minutes remaining
        
        result = rate_limiter.check_rate_limit("user123", limit=100, window=3600)
        assert result is False
    
    @patch('app.utils.rate_limiter.redis_client')
    def test_rate_limit_first_request(self, mock_redis, rate_limiter):
        """Test first request (no existing counter)"""
        mock_redis.get.return_value = None
        
        result = rate_limiter.check_rate_limit("user123", limit=100, window=3600)
        assert result is True
        
        # Should set initial counter
        mock_redis.setex.assert_called_once()
    
    @patch('app.utils.rate_limiter.redis_client')
    def test_increment_counter(self, mock_redis, rate_limiter):
        """Test incrementing rate limit counter"""
        mock_redis.incr.return_value = 6
        
        rate_limiter.increment_counter("user123", window=3600)
        mock_redis.incr.assert_called_once_with("rate_limit:user123")


class TestDataProcessor:
    """Test data processing utilities"""
    
    @pytest.fixture
    def data_processor(self):
        """Data processor instance for testing"""
        return DataProcessor()
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=100, freq='D'),
            'gdp_growth': np.random.normal(5.0, 1.0, 100),
            'inflation_rate': np.random.normal(7.0, 2.0, 100),
            'exchange_rate': np.random.normal(110.0, 5.0, 100)
        })
    
    def test_validate_features(self, data_processor):
        """Test feature validation"""
        valid_features = {
            "gdp_growth": 5.2,
            "inflation_rate": 7.8,
            "exchange_rate": 110.5
        }
        
        result = data_processor.validate_features(valid_features)
        assert result is True
        
        invalid_features = {
            "gdp_growth": None,
            "inflation_rate": "invalid"
        }
        
        result = data_processor.validate_features(invalid_features)
        assert result is False
    
    def test_preprocess_features(self, data_processor):
        """Test feature preprocessing"""
        features = {
            "gdp_growth": 5.2,
            "inflation_rate": 7.8,
            "exchange_rate": 110.5
        }
        
        processed = data_processor.preprocess_features(features)
        
        assert isinstance(processed, dict)
        assert all(isinstance(v, (int, float)) for v in processed.values())
    
    def test_create_lag_features(self, data_processor, sample_data):
        """Test lag feature creation"""
        result = data_processor.create_lag_features(sample_data, ['gdp_growth'], lags=[1, 2])
        
        assert 'gdp_growth_lag_1' in result.columns
        assert 'gdp_growth_lag_2' in result.columns
        assert len(result) == len(sample_data)
    
    def test_create_moving_averages(self, data_processor, sample_data):
        """Test moving average creation"""
        result = data_processor.create_moving_averages(sample_data, ['gdp_growth'], windows=[7, 14])
        
        assert 'gdp_growth_ma_7' in result.columns
        assert 'gdp_growth_ma_14' in result.columns
    
    def test_detect_outliers(self, data_processor, sample_data):
        """Test outlier detection"""
        # Add some outliers
        sample_data.loc[0, 'gdp_growth'] = 100  # Extreme outlier
        
        outliers = data_processor.detect_outliers(sample_data, ['gdp_growth'])
        assert len(outliers) > 0
        assert 0 in outliers  # First row should be detected as outlier
    
    def test_normalize_features(self, data_processor, sample_data):
        """Test feature normalization"""
        normalized = data_processor.normalize_features(sample_data, ['gdp_growth', 'inflation_rate'])
        
        # Check that values are normalized (mean ~0, std ~1)
        assert abs(normalized['gdp_growth'].mean()) < 0.1
        assert abs(normalized['gdp_growth'].std() - 1.0) < 0.1


class TestCacheUtilities:
    """Test caching utilities"""
    
    @patch('app.utils.cache.redis_client')
    def test_cache_set_get(self, mock_redis):
        """Test cache set and get operations"""
        from app.utils.cache import cache_set, cache_get
        
        # Test cache set
        cache_set("test_key", {"data": "value"}, ttl=3600)
        mock_redis.setex.assert_called_once()
        
        # Test cache get
        mock_redis.get.return_value = b'{"data": "value"}'
        result = cache_get("test_key")
        assert result == {"data": "value"}
    
    @patch('app.utils.cache.redis_client')
    def test_cache_miss(self, mock_redis):
        """Test cache miss"""
        from app.utils.cache import cache_get
        
        mock_redis.get.return_value = None
        result = cache_get("nonexistent_key")
        assert result is None
    
    @patch('app.utils.cache.redis_client')
    def test_cache_delete(self, mock_redis):
        """Test cache deletion"""
        from app.utils.cache import cache_delete
        
        cache_delete("test_key")
        mock_redis.delete.assert_called_once_with("test_key")


class TestSecurityUtilities:
    """Test security utilities"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        from app.core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False
    
    def test_jwt_token_creation(self):
        """Test JWT token creation and verification"""
        from app.core.security import create_access_token, decode_access_token
        
        data = {"sub": "test@example.com"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        decoded = decode_access_token(token)
        assert decoded["sub"] == "test@example.com"
    
    def test_jwt_token_expiration(self):
        """Test JWT token expiration"""
        from app.core.security import create_access_token, decode_access_token
        from datetime import timedelta
        
        data = {"sub": "test@example.com"}
        token = create_access_token(data, expires_delta=timedelta(seconds=-1))  # Expired
        
        with pytest.raises(Exception):  # Should raise an exception for expired token
            decode_access_token(token)


class TestDatabaseUtilities:
    """Test database utilities"""
    
    def test_pagination(self):
        """Test database pagination"""
        from app.utils.pagination import paginate
        
        # Mock query object
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = [1, 2, 3]
        mock_query.count.return_value = 100
        
        result = paginate(mock_query, page=1, size=10)
        
        assert result["items"] == [1, 2, 3]
        assert result["total"] == 100
        assert result["page"] == 1
        assert result["size"] == 10
        assert result["pages"] == 10
    
    def test_pagination_edge_cases(self):
        """Test pagination edge cases"""
        from app.utils.pagination import paginate
        
        mock_query = Mock()
        mock_query.offset.return_value.limit.return_value.all.return_value = []
        mock_query.count.return_value = 0
        
        # Test empty result
        result = paginate(mock_query, page=1, size=10)
        assert result["items"] == []
        assert result["total"] == 0
        assert result["pages"] == 0
        
        # Test page out of range
        mock_query.count.return_value = 5
        result = paginate(mock_query, page=10, size=10)  # Page 10 with only 5 items
        assert result["page"] == 10


class TestValidators:
    """Test custom validators"""
    
    def test_email_validation(self):
        """Test email validation"""
        from app.utils.validators import validate_email
        
        assert validate_email("test@example.com") is True
        assert validate_email("user@domain.co.uk") is True
        assert validate_email("invalid_email") is False
        assert validate_email("@domain.com") is False
        assert validate_email("user@") is False
    
    def test_feature_validation(self):
        """Test feature validation"""
        from app.utils.validators import validate_prediction_features
        
        valid_features = {
            "gdp_growth": 5.2,
            "inflation_rate": 7.8,
            "exchange_rate": 110.5
        }
        assert validate_prediction_features(valid_features) is True
        
        invalid_features = {
            "gdp_growth": None,
            "invalid_feature": 123
        }
        assert validate_prediction_features(invalid_features) is False
    
    def test_numeric_range_validation(self):
        """Test numeric range validation"""
        from app.utils.validators import validate_numeric_range
        
        assert validate_numeric_range(5.0, min_val=0, max_val=10) is True
        assert validate_numeric_range(-1.0, min_val=0, max_val=10) is False
        assert validate_numeric_range(15.0, min_val=0, max_val=10) is False