from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from .models import Prediction, Notification
from .utils import fetch_financial_data_from_api, train_neural_network
from .cache import invalidate_cache_by_prefix
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# ===========================
# 1. Fetch Financial Data Task
# ===========================

@shared_task
def fetch_financial_data():
    """
    Fetches financial data from external APIs and stores it in the database.
    """
    try:
        logger.info("Fetching financial data from external APIs...")
        data = fetch_financial_data_from_api()

        # Process and save data to the database
        for record in data:
            Prediction.objects.update_or_create(
                sector=record['sector'],
                country=record['country'],
                defaults={
                    'economic_indicator': record['indicator'],
                    'value': record['value'],
                }
            )
        logger.info("Financial data fetched and saved successfully.")
        invalidate_cache_by_prefix("predictions")  # Invalidate cache after updating predictions
    except Exception as e:
        logger.error(f"Failed to fetch financial data: {e}")
        raise


# ===========================
# 2. Train AI Model Task
# ===========================

@shared_task
def train_ai_model():
    """
    Trains the AI model using historical financial data.
    """
    try:
        logger.info("Training AI model with historical financial data...")
        train_neural_network()  # Simulates AI model training
        logger.info("AI model training completed successfully.")
    except Exception as e:
        logger.error(f"Failed to train AI model: {e}")
        raise


# ===========================
# 3. Send Notification Emails Task
# ===========================

@shared_task
def send_notification_emails():
    """
    Sends email notifications to users based on their preferences.
    """
    try:
        logger.info("Sending notification emails to users...")
        notifications = Notification.objects.filter(is_sent=False)

        for notification in notifications:
            send_mail(
                subject="New Investment Opportunity",
                message=notification.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification.user.email],
                fail_silently=False,
            )
            notification.is_sent = True
            notification.save()
        logger.info("Notification emails sent successfully.")
    except Exception as e:
        logger.error(f"Failed to send notification emails: {e}")
        raise


# ===========================
# 4. Periodic Cache Invalidation Task
# ===========================

@shared_task
def periodic_cache_invalidation():
    """
    Periodically invalidates cache for specific keys or prefixes.
    """
    try:
        logger.info("Invalidating cache for predictions...")
        invalidate_cache_by_prefix("predictions")
        logger.info("Cache invalidated successfully.")
    except Exception as e:
        logger.error(f"Failed to invalidate cache: {e}")
        raise


# ===========================
# 5. User-Specific Data Processing Task
# ===========================

@shared_task
def process_user_data(user_id):
    """
    Processes user-specific data (e.g., preferences, recent activity).
    """
    try:
        logger.info(f"Processing data for user ID: {user_id}...")
        # Example: Fetch user-specific data and perform analysis
        user_predictions = Prediction.objects.filter(owner_id=user_id)
        if not user_predictions.exists():
            logger.warning(f"No predictions found for user ID: {user_id}")
            return

        # Perform some processing (e.g., generate insights)
        insights = {
            "total_predictions": user_predictions.count(),
            "latest_prediction": user_predictions.latest('created_at').sector,
        }
        logger.info(f"Processed insights for user ID: {user_id}: {insights}")
    except Exception as e:
        logger.error(f"Failed to process data for user ID: {user_id}: {e}")
        raise

# ===========================
# 6. Cache Invalidation Utility
# ===========================

def invalidate_cache_by_prefix(prefix: str):
    """
    Invalidate all cache keys that start with the given prefix.
    """
    for key in default_cache.keys(f"{prefix}:*"):
        default_cache.delete(key)

# ===========================
# 7. Logging & Monitoring
# ===========================

import logging

logger = logging.getLogger(__name__)

def log_cache_usage(action: str, key: str, result=None):
    """
    Log cache usage for monitoring and debugging.
    """
    logger.info(f"Cache {action}: {key}")
    if result is not None:
        logger.debug(f"Cache {action} result: {result}")
# Compare this snippet from backend/investwise/external_logging.py:
# import logging
# import requests
#
# class ExternalLogHandler(logging.Handler):
#     """
#     Custom logging handler to send logs to an external service (e.g., Sentry, Logstash).
#     """
#     def __init__(self, service_url=None):
#         super().__init__()
#         self.service_url = service_url or "https://example.com/log-service"
#
#     def emit(self, record):
#         """
#         Send the log record to the external service.
#         """
#         try:
#             log_entry = self.format(record)
#             response = requests.post(
#                 self.service_url,
#                 json={"message": log_entry},
#                 timeout=5
#             )
#             if response.status_code != 200:
#                 print(f"Failed to send log to external service: {response.text}")
#         except Exception as e:
#             print(f"Error sending log to external service: {e}")
# # ===========================
# # 5. External Logging Service (Optional)
# # ===========================
def configure_logging():
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    if getattr(settings, 'LOGGING_EXTERNAL_SERVICE', False):
        from .external_logging import ExternalLogHandler
        external_handler = ExternalLogHandler()
        external_handler.setLevel(logging.WARNING)  # Log WARNING and above to external service
        external_handler.setFormatter(formatter)
        logger.addHandler(external_handler)
# Compare this snippet from backend/investwise/cache.py:
#     """
#     Invalidate cache keys that match the given prefix.
#     """

#     for key in default_cache.keys(f"{prefix}:*"):
#         default_cache.delete(key)
#
# # ===========================
# # 7. Logging & Monitoring
# # ===========================
#
# import logging
#
# logger = logging.getLogger(__name__)
#
# def log_cache_usage(action: str, key: str, result=None):
#     """
#     Log cache usage for monitoring and debugging.
#     """
#     logger.info(f"Cache {action}: {key}")
#     if result is not None:
#         logger.debug(f"Cache {action} result: {result}")
#
# # ===========================
# # 8. Example Usage
# # =========================== 
#   """
#     Invalidate cache keys that match the given prefix.
#     """
#
#     for key in default_cache.keys(f"{prefix}:*"):
#         default_cache.delete(key) 

