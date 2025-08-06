#!/usr/bin/env python
"""
InvestWise-Predictor Functionality Test Script
This script tests the core functionality of the platform.
"""

import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investwise.settings')

try:
    django.setup()
    print("✅ Django setup successful!")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Now we can import our models and test functionality
from django.contrib.auth.models import User
from apps.models import Prediction, Investment, Notification, Feedback
from apps.utils import generate_prediction, get_current_price
from apps.serializers import PredictionSerializer, InvestmentSerializer

def test_database_models():
    """Test database models and basic operations"""
    print("\n🔍 Testing Database Models...")
    
    try:
        # Test User model
        user_count = User.objects.count()
        print(f"✅ User model accessible - Current users: {user_count}")
        
        # Test Prediction model
        prediction_count = Prediction.objects.count()
        print(f"✅ Prediction model accessible - Current predictions: {prediction_count}")
        
        # Test Investment model
        investment_count = Investment.objects.count()
        print(f"✅ Investment model accessible - Current investments: {investment_count}")
        
        # Test Notification model
        notification_count = Notification.objects.count()
        print(f"✅ Notification model accessible - Current notifications: {notification_count}")
        
        # Test Feedback model
        feedback_count = Feedback.objects.count()
        print(f"✅ Feedback model accessible - Current feedbacks: {feedback_count}")
        
        return True
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

def test_ai_prediction_system():
    """Test AI prediction functionality"""
    print("\n🤖 Testing AI Prediction System...")
    
    try:
        # Test price prediction
        result = generate_prediction("AAPL", "price", "1M")
        if result and 'predicted_value' in result:
            print(f"✅ Price prediction works - AAPL predicted: ${result['predicted_value']} (Confidence: {result['confidence']}%)")
        else:
            print(f"❌ Price prediction failed: {result}")
            return False
        
        # Test trend prediction
        result = generate_prediction("GOOGL", "trend", "1W")
        if result and 'predicted_value' in result:
            print(f"✅ Trend prediction works - GOOGL trend: {result.get('trend_direction', 'N/A')} (Confidence: {result['confidence']}%)")
        else:
            print(f"❌ Trend prediction failed: {result}")
            return False
        
        # Test volatility prediction
        result = generate_prediction("TSLA", "volatility", "3M")
        if result and 'predicted_value' in result:
            print(f"✅ Volatility prediction works - TSLA volatility: {result['predicted_value']} (Level: {result.get('volatility_level', 'N/A')})")
        else:
            print(f"❌ Volatility prediction failed: {result}")
            return False
        
        # Test risk prediction
        result = generate_prediction("AMD", "risk", "1Y")
        if result and 'predicted_value' in result:
            print(f"✅ Risk prediction works - AMD risk: {result['predicted_value']} (Level: {result.get('risk_level', 'N/A')})")
        else:
            print(f"❌ Risk prediction failed: {result}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ AI prediction test failed: {e}")
        return False

def test_serializers():
    """Test serializer functionality"""
    print("\n📝 Testing Serializers...")
    
    try:
        # Test PredictionSerializer
        prediction_data = {
            'symbol': 'AAPL',
            'prediction_type': 'price',
            'time_horizon': '1M'
        }
        
        serializer = PredictionSerializer(data=prediction_data)
        if serializer.is_valid():
            print("✅ PredictionSerializer validation works")
        else:
            print(f"❌ PredictionSerializer validation failed: {serializer.errors}")
            return False
        
        # Test InvestmentSerializer
        investment_data = {
            'symbol': 'AAPL',
            'company_name': 'Apple Inc.',
            'investment_type': 'stock',
            'shares': 10,
            'purchase_price': 150.00
        }
        
        serializer = InvestmentSerializer(data=investment_data)
        if serializer.is_valid():
            print("✅ InvestmentSerializer validation works")
        else:
            print(f"❌ InvestmentSerializer validation failed: {serializer.errors}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Serializer test failed: {e}")
        return False

def test_mock_price_data():
    """Test mock price data functionality"""
    print("\n💰 Testing Mock Price Data...")
    
    try:
        symbols = ['AAPL', 'GOOGL', 'TSLA', 'MSFT', 'AMZN']
        
        for symbol in symbols:
            price = get_current_price(symbol)
            if price and price > 0:
                print(f"✅ {symbol}: ${price}")
            else:
                print(f"❌ Failed to get price for {symbol}")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Mock price data test failed: {e}")
        return False

def test_model_creation():
    """Test creating model instances"""
    print("\n🏗️ Testing Model Creation...")
    
    try:
        # Create test user (if doesn't exist)
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            print("✅ Test user created")
        else:
            print("✅ Test user already exists")
        
        # Create test prediction
        prediction = Prediction.objects.create(
            user=test_user,
            symbol='TEST',
            prediction_type='price',
            time_horizon='1M',
            predicted_value=100.0,
            confidence=85.5,
            status='completed'
        )
        print(f"✅ Test prediction created: ID {prediction.id}")
        
        # Create test investment
        investment = Investment.objects.create(
            user=test_user,
            symbol='TEST',
            company_name='Test Company',
            investment_type='stock',
            shares=10,
            purchase_price=50.0
        )
        print(f"✅ Test investment created: ID {investment.id}")
        
        # Create test notification
        notification = Notification.objects.create(
            user=test_user,
            title='Test Notification',
            message='This is a test notification',
            type='info'
        )
        print(f"✅ Test notification created: ID {notification.id}")
        
        # Create test feedback
        feedback = Feedback.objects.create(
            user=test_user,
            category='general',
            subject='Test Feedback',
            message='This is test feedback',
            rating=5
        )
        print(f"✅ Test feedback created: ID {feedback.id}")
        
        return True
    except Exception as e:
        print(f"❌ Model creation test failed: {e}")
        return False

def run_all_tests():
    """Run all functionality tests"""
    print("🚀 InvestWise-Predictor Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_models,
        test_ai_prediction_system,
        test_serializers,
        test_mock_price_data,
        test_model_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! InvestWise-Predictor is fully functional!")
        return True
    else:
        print(f"⚠️ {total - passed} tests failed. Check the errors above.")
        return False

if __name__ == "__main__":
    # Check if we can run migrations first
    print("🔧 Checking database setup...")
    
    try:
        from django.core.management import execute_from_command_line
        
        # Run migrations to ensure database is set up
        print("Running migrations...")
        execute_from_command_line(['manage.py', 'migrate', '--run-syncdb'])
        print("✅ Database migrations completed")
        
    except Exception as e:
        print(f"⚠️ Migration warning: {e}")
        print("Continuing with tests...")
    
    # Run the test suite
    success = run_all_tests()
    sys.exit(0 if success else 1)
