from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from .models import Prediction, User, Notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Prediction)
def send_prediction_notification(sender, instance, created, **kwargs):
    """
    Send notification when a new prediction is created or updated.
    """
    if created:
        # Create notification for new prediction
        Notification.objects.create(
            user=instance.user,
            title="New Prediction Created",
            message=f"Your prediction for {instance.sector} in {instance.country} has been created.",
            notification_type='info'
        )
        logger.info(f"Notification sent for new prediction: {instance.id}")
    elif instance.status == 'completed':
        # Notify when prediction is completed
        Notification.objects.create(
            user=instance.user,
            title="Prediction Completed",
            message=f"Your prediction for {instance.sector} has been completed with value ${instance.predicted_value}.",
            notification_type='success'
        )
        logger.info(f"Completion notification sent for prediction: {instance.id}")


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    """
    Handle user login events.
    """
    logger.info(f"User {user.username} logged in from IP: {request.META.get('REMOTE_ADDR')}")


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    """
    Handle user logout events.
    """
    if user:
        logger.info(f"User {user.username} logged out")


@receiver(pre_delete, sender=Prediction)
def prediction_delete_handler(sender, instance, **kwargs):
    """
    Handle prediction deletion.
    """
    logger.info(f"Prediction {instance.id} for user {instance.user.username} is being deleted")
