from rest_framework import serializers
from django_countries.serializer_fields import CountryField
from .models import (
    User,
    Prediction,
    DataPoint,
    InvestmentPreference,
    RiskProfile,
    Notification,
    EconomicIndicator,
    SectorPerformance,
)


# ===========================
# 1. User-Related Serializers
# ===========================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    Includes additional fields like phone_number, date_of_birth, and risk_tolerance.
    """
    country = CountryField(country_dict=True)  # Use django-countries for country representation

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone_number',
            'date_of_birth',
            'risk_tolerance',
            'is_staff',
            'is_superuser',
            'date_joined',
            'last_login',
        ]
        read_only_fields = ['id', 'is_staff', 'is_superuser', 'date_joined', 'last_login']

    def validate_email(self, value):
        """
        Ensure that the email is unique.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


# ===========================
# 2. Core Model Serializers
# ===========================

class PredictionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Prediction model.
    Includes nested fields for user and read-only fields for predicted_value.
    """
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    sector = serializers.CharField(max_length=255)
    country = CountryField(country_dict=True)

    class Meta:
        model = Prediction
        fields = [
            'id',
            'user',
            'sector',
            'country',
            'predicted_value',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'predicted_value', 'created_at', 'updated_at']

    def validate_sector(self, value):
        """
        Ensure the sector field is not empty.
        """
        if not value.strip():
            raise serializers.ValidationError("Sector cannot be empty.")
        return value


class DataPointSerializer(serializers.ModelSerializer):
    """
    Serializer for the DataPoint model.
    Includes validation for positive values and proper date formatting.
    """
    indicator = serializers.CharField(max_length=255)
    value = serializers.FloatField(min_value=0)
    date = serializers.DateField()
    country = CountryField(country_dict=True)

    class Meta:
        model = DataPoint
        fields = [
            'id',
            'indicator',
            'value',
            'date',
            'country',
            'source',
        ]
        read_only_fields = ['id']

    def validate_value(self, value):
        """
        Ensure the value is positive.
        """
        if value <= 0:
            raise serializers.ValidationError("Value must be positive.")
        return value


class InvestmentPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for the InvestmentPreference model.
    Allows users to set their preferred sector, country, and risk tolerance.
    """
    preferred_country = CountryField(country_dict=True, required=False)

    class Meta:
        model = InvestmentPreference
        fields = [
            'id',
            'preferred_sector',
            'preferred_country',
            'risk_tolerance',
        ]
        read_only_fields = ['id']


class RiskProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the RiskProfile model.
    Includes validation for score range and profile type.
    """
    profile_type = serializers.ChoiceField(choices=RiskProfile.ProfileType.choices)
    score = serializers.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = RiskProfile
        fields = [
            'id',
            'profile_type',
            'score',
            'description',
        ]
        read_only_fields = ['id']

    def validate_score(self, value):
        """
        Ensure the score is within the valid range.
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError("Score must be between 0 and 100.")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    Includes read-only fields for created_at and is_read.
    """
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'message',
            'is_read',
            'created_at',
        ]
        read_only_fields = ['id', 'user', 'created_at']


# ===========================
# 3. Supporting Model Serializers
# ===========================

class EconomicIndicatorSerializer(serializers.ModelSerializer):
    """
    Serializer for the EconomicIndicator model.
    """
    class Meta:
        model = EconomicIndicator
        fields = [
            'id',
            'name',
            'description',
            'unit',
            'source',
        ]
        read_only_fields = ['id']


class SectorPerformanceSerializer(serializers.ModelSerializer):
    """
    Serializer for the SectorPerformance model.
    Includes validation for growth_rate and market_size.
    """
    growth_rate = serializers.DecimalField(max_digits=5, decimal_places=2, min_value=0)
    market_size = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0)

    class Meta:
        model = SectorPerformance
        fields = [
            'id',
            'sector',
            'growth_rate',
            'market_size',
            'year',
        ]
        read_only_fields = ['id']

    def validate_year(self, value):
        """
        Ensure the year is not in the future.
        """
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year:
            raise serializers.ValidationError("Year cannot be in the future.")
        return value


# ===========================
# 4. Nested Serializers
# ===========================

class UserWithPreferencesSerializer(UserSerializer):
    """
    Serializer for the User model with nested investment preferences and risk profile.
    """
    investment_preference = InvestmentPreferenceSerializer(read_only=True)
    risk_profile = RiskProfileSerializer(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['investment_preference', 'risk_profile']


class PredictionWithDetailsSerializer(PredictionSerializer):
    """
    Serializer for the Prediction model with detailed user information.
    """
    user = UserWithPreferencesSerializer(read_only=True)

    class Meta(PredictionSerializer.Meta):
        fields = PredictionSerializer.Meta.fields + ['user']
