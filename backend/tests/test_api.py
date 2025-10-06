import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch


class TestHealthEndpoint:
    """Test health check endpoints"""
    
    def test_health_check(self, client: TestClient):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
    
    def test_health_detailed(self, client: TestClient):
        """Test detailed health check"""
        with patch('app.api.v1.endpoints.health.check_database') as mock_db, \
             patch('app.api.v1.endpoints.health.check_redis') as mock_redis, \
             patch('app.api.v1.endpoints.health.check_ml_service') as mock_ml:
            
            mock_db.return_value = True
            mock_redis.return_value = True
            mock_ml.return_value = True
            
            response = client.get("/health/detailed")
            assert response.status_code == 200
            data = response.json()
            
            assert data["status"] == "healthy"
            assert data["services"]["database"] == "healthy"
            assert data["services"]["redis"] == "healthy"
            assert data["services"]["ml_service"] == "healthy"
    
    def test_health_detailed_database_down(self, client: TestClient):
        """Test health check when database is down"""
        with patch('app.api.v1.endpoints.health.check_database') as mock_db, \
             patch('app.api.v1.endpoints.health.check_redis') as mock_redis, \
             patch('app.api.v1.endpoints.health.check_ml_service') as mock_ml:
            
            mock_db.return_value = False
            mock_redis.return_value = True
            mock_ml.return_value = True
            
            response = client.get("/health/detailed")
            assert response.status_code == 503
            data = response.json()
            
            assert data["status"] == "unhealthy"
            assert data["services"]["database"] == "unhealthy"
            assert data["services"]["redis"] == "healthy"
            assert data["services"]["ml_service"] == "healthy"


class TestPredictionEndpoints:
    """Test prediction endpoints"""
    
    def test_predict_success(self, client: TestClient, auth_headers: dict, 
                           sample_prediction_request: dict, mock_ml_service):
        """Test successful prediction"""
        response = client.post(
            "/api/v1/predict/",
            json=sample_prediction_request,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "prediction" in data
        assert "confidence" in data
        assert "model_version" in data
        assert "request_id" in data
        assert data["prediction"] == 1250.75
        assert data["confidence"] == 0.85
    
    def test_predict_unauthorized(self, client: TestClient, sample_prediction_request: dict):
        """Test prediction without authentication"""
        response = client.post("/api/v1/predict/", json=sample_prediction_request)
        assert response.status_code == 401
    
    def test_predict_invalid_data(self, client: TestClient, auth_headers: dict):
        """Test prediction with invalid data"""
        invalid_request = {
            "features": {
                "gdp_growth": "invalid"  # Should be float
            }
        }
        
        response = client.post(
            "/api/v1/predict/",
            json=invalid_request,
            headers=auth_headers
        )
        assert response.status_code == 422
    
    def test_predict_ml_service_error(self, client: TestClient, auth_headers: dict,
                                    sample_prediction_request: dict):
        """Test prediction when ML service is down"""
        with patch('app.utils.ml_client.predict') as mock_predict:
            mock_predict.side_effect = Exception("ML service unavailable")
            
            response = client.post(
                "/api/v1/predict/",
                json=sample_prediction_request,
                headers=auth_headers
            )
            assert response.status_code == 503
    
    def test_explain_prediction(self, client: TestClient, auth_headers: dict,
                              sample_prediction_request: dict, mock_ml_service):
        """Test prediction explanation"""
        response = client.post(
            "/api/v1/predict/explain",
            json=sample_prediction_request,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "shap_values" in data
        assert "feature_importance" in data
        assert "gdp_growth" in data["shap_values"]
    
    def test_prediction_history(self, client: TestClient, auth_headers: dict):
        """Test getting prediction history"""
        response = client.get("/api/v1/predict/history", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAuthEndpoints:
    """Test authentication endpoints"""
    
    def test_login_success(self, client: TestClient, mock_user):
        """Test successful login"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "secret"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, client: TestClient, mock_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "wrong_password"
            }
        )
        assert response.status_code == 401
    
    def test_register_success(self, client: TestClient):
        """Test successful user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
    
    def test_register_duplicate_email(self, client: TestClient, mock_user):
        """Test registration with existing email"""
        user_data = {
            "email": "test@example.com",  # Already exists
            "username": "newuser",
            "password": "newpassword123"
        }
        
        response = client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 400
    
    def test_get_current_user(self, client: TestClient, auth_headers: dict, mock_user):
        """Test getting current user info"""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"


class TestDataEndpoints:
    """Test data management endpoints"""
    
    def test_get_market_data(self, client: TestClient, auth_headers: dict):
        """Test getting market data"""
        response = client.get("/api/v1/data/market", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_add_market_data(self, client: TestClient, auth_headers: dict, 
                           sample_market_data: dict):
        """Test adding market data"""
        response = client.post(
            "/api/v1/data/market",
            json=sample_market_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["gdp_growth"] == sample_market_data["gdp_growth"]
    
    def test_get_market_data_unauthorized(self, client: TestClient):
        """Test getting market data without authentication"""
        response = client.get("/api/v1/data/market")
        assert response.status_code == 401


class TestMetricsEndpoints:
    """Test metrics endpoints"""
    
    def test_get_metrics(self, client: TestClient):
        """Test getting metrics"""
        response = client.get("/metrics")
        assert response.status_code == 200
        # Should return Prometheus format metrics
        assert "investwise_" in response.text
    
    def test_api_metrics(self, client: TestClient, auth_headers: dict):
        """Test API-specific metrics"""
        response = client.get("/api/v1/metrics", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "predictions_total" in data
        assert "api_requests_total" in data


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_not_exceeded(self, client: TestClient, auth_headers: dict,
                                   sample_prediction_request: dict, mock_ml_service):
        """Test that requests within rate limit work"""
        for _ in range(5):  # Should be under the limit
            response = client.post(
                "/api/v1/predict/",
                json=sample_prediction_request,
                headers=auth_headers
            )
            assert response.status_code == 200
    
    @pytest.mark.skip("Rate limiting tests need Redis setup")
    def test_rate_limit_exceeded(self, client: TestClient, auth_headers: dict,
                                sample_prediction_request: dict, mock_ml_service):
        """Test rate limiting when limit is exceeded"""
        # This would need proper Redis setup for testing
        pass


class TestValidation:
    """Test input validation"""
    
    def test_prediction_request_validation(self, client: TestClient, auth_headers: dict):
        """Test prediction request validation"""
        invalid_requests = [
            {},  # Empty request
            {"features": {}},  # Empty features
            {"features": {"gdp_growth": None}},  # Null values
            {"features": {"gdp_growth": "invalid"}},  # Invalid type
        ]
        
        for invalid_request in invalid_requests:
            response = client.post(
                "/api/v1/predict/",
                json=invalid_request,
                headers=auth_headers
            )
            assert response.status_code == 422
    
    def test_user_registration_validation(self, client: TestClient):
        """Test user registration validation"""
        invalid_requests = [
            {},  # Empty request
            {"email": "invalid_email"},  # Invalid email
            {"email": "test@example.com", "password": "123"},  # Password too short
            {"email": "test@example.com", "username": "a"},  # Username too short
        ]
        
        for invalid_request in invalid_requests:
            response = client.post("/api/v1/auth/register", json=invalid_request)
            assert response.status_code == 422