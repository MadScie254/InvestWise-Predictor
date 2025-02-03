from django.db import models
from django.utils import timezone
from datetime import timedelta


# ===========================
# 1. Prediction Manager
# ===========================

class PredictionManager(models.Manager):
    """
    Custom manager for the Prediction model.
    Provides methods for filtering and querying predictions.
    """

    def get_pending_predictions(self):
        """
        Returns all pending predictions.
        """
        return self.filter(status='pending')

    def get_completed_predictions(self):
        """
        Returns all completed predictions.
        """
        return self.filter(status='completed')

    def get_predictions_for_user(self, user):
        """
        Returns all predictions for a specific user.
        """
        return self.filter(user=user).order_by('-created_at')

    def get_recent_predictions(self, days=7):
        """
        Returns predictions created in the last `days` days.
        """
        recent_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=recent_date).order_by('-created_at')

    def create_prediction(self, user, sector, country, **kwargs):
        """
        Creates a new prediction instance with default values.
        """
        from .models import Prediction

        if not user or not sector or not country:
            raise ValueError("User, sector, and country are required fields.")

        prediction = self.create(
            user=user,
            sector=sector,
            country=country,
            status='pending',
            **kwargs
        )
        return prediction


# ===========================
# 2. DataPoint Manager
# ===========================

class DataPointManager(models.Manager):
    """
    Custom manager for the DataPoint model.
    Provides methods for filtering and querying data points.
    """

    def get_data_points_for_country(self, country_code):
        """
        Returns all data points for a specific country.
        """
        return self.filter(country=country_code)

    def get_data_points_for_indicator(self, indicator_name):
        """
        Returns all data points for a specific economic indicator.
        """
        return self.filter(indicator=indicator_name)

    def get_latest_data_point(self, indicator_name, country_code):
        """
        Returns the latest data point for a specific indicator and country.
        """
        return self.filter(indicator=indicator_name, country=country_code).order_by('-date').first()


# ===========================
# 3. InvestmentPreference Manager
# ===========================

class InvestmentPreferenceManager(models.Manager):
    """
    Custom manager for the InvestmentPreference model.
    Provides methods for managing user investment preferences.
    """

    def get_or_create_preference(self, user):
        """
        Gets or creates an investment preference for a specific user.
        """
        preference, created = self.get_or_create(user=user)
        return preference

    def update_preferences(self, user, preferred_sector=None, preferred_country=None, risk_tolerance=None):
        """
        Updates the investment preferences for a specific user.
        """
        preference = self.get_or_create_preference(user)
        if preferred_sector:
            preference.preferred_sector = preferred_sector
        if preferred_country:
            preference.preferred_country = preferred_country
        if risk_tolerance:
            preference.risk_tolerance = risk_tolerance
        preference.save()
        return preference


# ===========================
# 4. RiskProfile Manager
# ===========================

class RiskProfileManager(models.Manager):
    """
    Custom manager for the RiskProfile model.
    Provides methods for managing user risk profiles.
    """

    def get_or_create_profile(self, user):
        """
        Gets or creates a risk profile for a specific user.
        """
        profile, created = self.get_or_create(user=user)
        return profile

    def update_profile(self, user, profile_type=None, score=None, description=None):
        """
        Updates the risk profile for a specific user.
        """
        profile = self.get_or_create_profile(user)
        if profile_type:
            profile.profile_type = profile_type
        if score:
            profile.score = score
        if description:
            profile.description = description
        profile.save()
        return profile


# ===========================
# 5. Notification Manager
# ===========================

class NotificationManager(models.Manager):
    """
    Custom manager for the Notification model.
    Provides methods for managing user notifications.
    """

    def create_notification(self, user, message):
        """
        Creates a new notification for a specific user.
        """
        if not user or not message:
            raise ValueError("User and message are required fields.")
        return self.create(user=user, message=message)

    def mark_as_read(self, notification_id):
        """
        Marks a notification as read.
        """
        notification = self.filter(id=notification_id).first()
        if notification:
            notification.is_read = True
            notification.save()
        return notification

    def get_unread_notifications(self, user):
        """
        Returns all unread notifications for a specific user.
        """
        return self.filter(user=user, is_read=False).order_by('-created_at')
