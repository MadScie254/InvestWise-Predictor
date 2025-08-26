import unittest
from unittest.mock import patch, MagicMock
from django.test import TestCase, RequestFactory
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import (
    Prediction,
    DataPoint,
    InvestmentPreference,
    RiskProfile,
    Notification,
    EconomicIndicator,
    SectorPerformance,
)
from .serializers import (
    PredictionSerializer,
    DataPointSerializer,
    InvestmentPreferenceSerializer,
    RiskProfileSerializer,
    NotificationSerializer,
    UserRegistrationSerializer,
    UserSerializer,
)
from .views import GeneratePredictionView, register_user, login_user, logout_user
from .utils import generate_prediction


# ===========================
# 1. Authentication Tests
# ===========================

class AuthenticationTestCase(APITestCase):
    """Test cases for user authentication views."""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
    def test_user_registration_success(self):
        """Test successful user registration."""
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['email'], 'test@example.com')
        
        # Check if JWT tokens are in response (if available)
        if 'jwt_available' not in response.data or response.data.get('jwt_available', True):
            self.assertIn('access', response.data)
            self.assertIn('refresh', response.data)
    
    def test_user_registration_invalid_data(self):
        """Test user registration with invalid data."""
        url = reverse('register')
        invalid_data = {'username': 'testuser'}  # Missing required fields
        response = self.client.post(url, invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_login_success(self):
        """Test successful user login."""
        # Create a user first
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )
        
        url = reverse('login')
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('login')
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
    
    def test_user_login_missing_fields(self):
        """Test login with missing required fields."""
        url = reverse('login')
        login_data = {'username': 'testuser'}  # Missing password
        response = self.client.post(url, login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_user_logout_success(self):
        """Test successful user logout."""
        # Create and authenticate user
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.client.force_authenticate(user=user)
        
        url = reverse('logout')
        logout_data = {'refresh_token': 'dummy_token'}
        response = self.client.post(url, logout_data, format='json')
        
        # Should return success regardless of JWT availability
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
    
    def test_user_logout_missing_token(self):
        """Test logout without refresh token."""
        user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )
        self.client.force_authenticate(user=user)
        
        url = reverse('logout')
        response = self.client.post(url, {}, format='json')
        
        # Should handle missing token gracefully
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST])


class JWTMockTests(APITestCase):
    """Test JWT functionality with mocked JWT library."""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
    
    @patch('apps.views.JWT_AVAILABLE', True)
    @patch('apps.views.RefreshToken')
    def test_registration_with_jwt_available(self, mock_refresh_token):
        """Test registration when JWT is available."""
        # Mock JWT token generation
        mock_token = MagicMock()
        mock_token.access_token = 'mock_access_token'
        mock_refresh_token.for_user.return_value = mock_token
        mock_token.__str__ = lambda x: 'mock_refresh_token'
        
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    @patch('apps.views.JWT_AVAILABLE', False)
    def test_registration_without_jwt_available(self):
        """Test registration when JWT is not available."""
        url = reverse('register')
        response = self.client.post(url, self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['jwt_available'], False)


# ===========================
# 1. Model Tests
# ===========================

class PredictionModelTest(TestCase):
    """
    Test cases for the Prediction model.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.prediction = Prediction.objects.create(
            user=self.user,
            sector='Technology',
            country='US',
            predicted_value=500.00,
            status='completed'
        )

    def test_prediction_creation(self):
        """
        Ensure that a Prediction instance can be created successfully.
        """
        self.assertEqual(self.prediction.sector, 'Technology')
        self.assertEqual(self.prediction.country, 'US')
        self.assertEqual(self.prediction.predicted_value, 500.00)
        self.assertEqual(self.prediction.status, 'completed')

    def test_prediction_string_representation(self):
        """
        Ensure that the string representation of a Prediction is correct.
        """
        self.assertEqual(str(self.prediction), f"Prediction for {self.user.username} - Technology (US)")


class DataPointModelTest(TestCase):
    """
    Test cases for the DataPoint model.
    """
    def setUp(self):
        self.data_point = DataPoint.objects.create(
            indicator='GDP',
            value=1000.00,
            date='2023-01-01',
            country='KE',
            source='KNBS'
        )

    def test_data_point_creation(self):
        """
        Ensure that a DataPoint instance can be created successfully.
        """
        self.assertEqual(self.data_point.indicator, 'GDP')
        self.assertEqual(self.data_point.value, 1000.00)
        self.assertEqual(str(self.data_point), "GDP (KE) - 2023-01-01")


# ===========================
# 2. Serializer Tests
# ===========================

class PredictionSerializerTest(TestCase):
    """
    Test cases for the PredictionSerializer.
    """
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.prediction = Prediction.objects.create(
            user=self.user,
            sector='Technology',
            country='US',
            predicted_value=500.00,
            status='completed'
        )
        self.serializer = PredictionSerializer(instance=self.prediction)

    def test_serializer_contains_expected_fields(self):
        """
        Ensure that the serializer contains the expected fields.
        """
        data = self.serializer.data
        self.assertCountEqual(data.keys(), ['id', 'user', 'sector', 'country', 'predicted_value', 'status', 'created_at', 'updated_at'])

    def test_serializer_data(self):
        """
        Ensure that the serialized data matches the model instance.
        """
        data = self.serializer.data
        self.assertEqual(data['sector'], 'Technology')
        self.assertEqual(data['country'], 'US')
        self.assertEqual(data['predicted_value'], '500.00')


# ===========================
# 3. View Tests
# ===========================

class PredictionViewTest(APITestCase):
    """
    Test cases for the Prediction API views.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_prediction(self):
        """
        Ensure that predictions can be created via the API.
        """
        url = reverse('prediction-list-create')
        data = {
            'sector': 'Technology',
            'country': 'US'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Prediction.objects.count(), 1)
        self.assertEqual(Prediction.objects.get().sector, 'Technology')

    def test_list_predictions(self):
        """
        Ensure that predictions can be listed via the API.
        """
        Prediction.objects.create(
            user=self.user,
            sector='Technology',
            country='US',
            predicted_value=500.00,
            status='completed'
        )
        url = reverse('prediction-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class GeneratePredictionViewTest(APITestCase):
    """
    Test cases for the GeneratePredictionView.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_generate_prediction(self):
        """
        Ensure that predictions can be generated via the custom API endpoint.
        """
        url = reverse('generate-prediction')
        data = {
            'sector': 'Technology',
            'country': 'US'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('sector', response.data)
        self.assertIn('country', response.data)
        self.assertIn('predicted_value', response.data)


# ===========================
# 4. Utility Function Tests
# ===========================

class GeneratePredictionUtilityTest(TestCase):
    """
    Test cases for the generate_prediction utility function.
    """
    def test_generate_prediction(self):
        """
        Ensure that the generate_prediction function returns valid data.
        """
        prediction_data = generate_prediction(sector='Technology', country='US')
        self.assertIn('sector', prediction_data)
        self.assertIn('country', prediction_data)
        self.assertIn('predicted_value', prediction_data)
        self.assertGreater(prediction_data['predicted_value'], 0)


# ===========================
# 5. Integration Tests
# ===========================

class PredictionIntegrationTest(APITestCase):
    """
    Integration tests for the Prediction workflow.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_full_prediction_workflow(self):
        """
        Simulate the full prediction workflow: create -> list -> retrieve.
        """
        # Step 1: Create a prediction
        create_url = reverse('prediction-list-create')
        create_data = {
            'sector': 'Technology',
            'country': 'US'
        }
        create_response = self.client.post(create_url, create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Step 2: List predictions
        list_url = reverse('prediction-list-create')
        list_response = self.client.get(list_url, format='json')
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data['results']), 1)

        # Step 3: Retrieve a specific prediction
        prediction_id = list_response.data['results'][0]['id']
        retrieve_url = reverse('prediction-detail', kwargs={'pk': prediction_id})
        retrieve_response = self.client.get(retrieve_url, format='json')
        self.assertEqual(retrieve_response.status_code, status.HTTP_200_OK)
        self.assertEqual(retrieve_response.data['sector'], 'Technology')
