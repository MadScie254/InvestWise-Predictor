from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinLengthValidator, EmailValidator
import re
from .models import Prediction, Investment, Notification, Feedback


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with enhanced validation."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration with comprehensive validation."""
    password = serializers.CharField(
        write_only=True, 
        validators=[validate_password, MinLengthValidator(8)],
        help_text="Password must be at least 8 characters long"
    )
    password_confirm = serializers.CharField(
        write_only=True,
        help_text="Must match the password field"
    )
    email = serializers.EmailField(
        validators=[EmailValidator()],
        help_text="Valid email address required"
    )
    username = serializers.CharField(
        validators=[MinLengthValidator(3)],
        help_text="Username must be at least 3 characters long"
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate_username(self, value: str) -> str:
        """Validate username format and uniqueness."""
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and underscores"
            )
        
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists")
        
        return value.lower()
    
    def validate_email(self, value: str) -> str:
        """Validate email uniqueness."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email address already registered")
        
        return value.lower()
    
    def validate_password(self, value: str) -> str:
        """Enhanced password validation."""
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long")
        
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one digit")
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-field validation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords don't match"})
        
        # Remove password_confirm from validated data
        attrs.pop('password_confirm', None)
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> User:
        """Create user with validated data."""
        user = User.objects.create_user(**validated_data)
        return user


class PredictionSerializer(serializers.ModelSerializer):
    """Serializer for Prediction model"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Prediction
        fields = [
            'id', 'user', 'symbol', 'prediction_type', 'time_horizon',
            'predicted_value', 'confidence', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'predicted_value', 'confidence', 'status', 'created_at', 'updated_at']
    
    def validate_symbol(self, value):
        """Validate that symbol is uppercase and alphanumeric"""
        if not value.replace('.', '').replace('-', '').isalnum():
            raise serializers.ValidationError("Symbol must contain only letters, numbers, dots, and hyphens")
        return value.upper()


class InvestmentSerializer(serializers.ModelSerializer):
    """Serializer for Investment model"""
    user = serializers.StringRelatedField(read_only=True)
    current_value = serializers.SerializerMethodField()
    gain_loss = serializers.SerializerMethodField()
    
    class Meta:
        model = Investment
        fields = [
            'id', 'user', 'symbol', 'company_name', 'investment_type',
            'shares', 'purchase_price', 'current_value', 'gain_loss',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'current_value', 'gain_loss', 'created_at', 'updated_at']
    
    def get_current_value(self, obj):
        """Calculate current value (mock calculation)"""
        # In a real app, this would fetch real-time market data
        import random
        current_price = float(obj.purchase_price) * (1 + random.uniform(-0.1, 0.1))
        return round(float(obj.shares) * current_price, 2)
    
    def get_gain_loss(self, obj):
        """Calculate gain/loss percentage"""
        current_value = self.get_current_value(obj)
        invested_value = float(obj.shares) * float(obj.purchase_price)
        gain_loss = current_value - invested_value
        percentage = (gain_loss / invested_value) * 100 if invested_value > 0 else 0
        return {
            'value': round(gain_loss, 2),
            'percentage': round(percentage, 2),
            'is_positive': gain_loss >= 0
        }
    
    def validate_shares(self, value):
        """Validate that shares is positive"""
        if value <= 0:
            raise serializers.ValidationError("Shares must be greater than 0")
        return value
    
    def validate_purchase_price(self, value):
        """Validate that purchase price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Purchase price must be greater than 0")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'type', 'read',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class FeedbackSerializer(serializers.ModelSerializer):
    """Serializer for Feedback model"""
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Feedback
        fields = [
            'id', 'user', 'category', 'subject', 'message', 'rating',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value
    
    def validate_message(self, value):
        """Validate message length"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long")
        return value.strip()
