from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .cache import invalidate_cache_by_prefix
from .logging import logger

# Get the custom User model
User = get_user_model()

# ===========================
# 1. User Registration Signal
# ===========================

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Sends a welcome email to users upon registration.
    Triggered when a new user is created.
    """
    if created:
        try:
            subject = "Welcome to InvestWise Predictor!"
            message = (
                f"Hi {instance.first_name},\n\n"
                "Thank you for registering with InvestWise Predictor. "
                "We are excited to help you make data-driven investment decisions.\n\n"
                "Best regards,\nThe InvestWise Team"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=False,
            )
            logger.info(f"Welcome email sent to {instance.email}")
        except Exception as e:
            logger.error(f"Failed to send welcome email to {instance.email}: {e}")


# ===========================
# 2. Cache Invalidation Signal
# ===========================

@receiver(post_save, sender="predictor.Prediction")
@receiver(pre_delete, sender="predictor.Prediction")
def invalidate_prediction_cache(sender, instance, **kwargs):
    """
    Invalidates cache related to predictions when a Prediction object is saved or deleted.
    """
    try:
        invalidate_cache_by_prefix("predictions")
        logger.info(f"Cache invalidated for predictions due to change in {instance}")
    except Exception as e:
        logger.error(f"Failed to invalidate prediction cache: {e}")


# ===========================
# 3. Logging User Activity Signal
# ===========================

@receiver(post_save, sender=User)
def log_user_activity(sender, instance, **kwargs):
    """
    Logs user activity whenever a user's profile is updated.
    """
    logger.info(f"User {instance.email} was updated.")


# ===========================
# 4. Data Integrity Validation Signal
# ===========================

@receiver(pre_save, sender="predictor.Prediction")
def validate_prediction_data(sender, instance, **kwargs):
    """
    Validates Prediction data before saving to ensure integrity.
    """
    if not instance.sector or not instance.country:
        raise ValueError("Sector and country fields cannot be empty.")
    logger.info(f"Validation passed for Prediction {instance}")

# ===========================
# 5. Notification Signal (Optional)
# ===========================

@receiver(post_save, sender="predictor.Notification")
def send_notification_email(sender, instance, created, **kwargs):
    """
    Sends an email notification to users when a new notification is created.
    """
    if created:
        try:
            subject = "New Notification from InvestWise Predictor"
            message = (
                f"Hi {instance.user.first_name},\n\n"
                f"You have a new notification: {instance.message}\n\n"
                "Best regards,\nThe InvestWise Team"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.user.email],
                fail_silently=False,
            )
            logger.info(f"Notification email sent to {instance.user.email}")
        except Exception as e:
            logger.error(f"Failed to send notification email to {instance.user.email}: {e}")

# ===========================
# 6. Example Usage in Application
# ===========================
#
# # Create a new user
# new_user = User.objects.create_user(
#     email="
#     password="
# )
#
# # Update the user's profile
# new_user.first_name = "John"
# new_user.save()
#
