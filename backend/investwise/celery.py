import os
from celery import Celery
from django.conf import settings

# ===========================
# 1. Environment Configuration
# ===========================

# Set the default Django settings module for Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investwise.settings')

# ===========================
# 2. Initialize Celery Application
# ===========================

app = Celery('investwise')

# ===========================
# 3. Celery Configuration
# ===========================

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# ===========================
# 4. Auto-Discover Tasks
# ===========================

# Automatically discover tasks in all installed apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# ===========================
# 5. Logging Configuration
# ===========================

import logging

logger = logging.getLogger(__name__)

@app.task(bind=True)
def debug_task(self):
    """
    A simple debug task to test Celery setup.
    Logs the task request details.
    """
    logger.info(f"Debug Task Running: {self.request!r}")

# ===========================
# 6. Periodic Tasks (Optional)
# ===========================

# Example: Schedule periodic tasks using Celery Beat
from celery.schedules import crontab

app.conf.beat_schedule = {
    'fetch-financial-data-every-hour': {
        'task': 'predictor.tasks.fetch_financial_data',
        'schedule': 3600.0,  # Run every hour
        'args': (),
    },
    'train-ai-model-daily': {
        'task': 'predictor.tasks.train_ai_model',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
        'args': (),
    },
}

# ===========================
# 7. Error Handling for Tasks
# ===========================

@app.task(bind=True, max_retries=3)
def retry_on_failure(self, *args, **kwargs):
    """
    A generic task decorator to retry failed tasks up to 3 times.
    Logs retries and raises an exception if all retries fail.
    """
    try:
        # Perform the task logic here
        pass
    except Exception as exc:
        logger.error(f"Task failed: {exc}. Retrying...")
        self.retry(exc=exc, countdown=2 ** self.request.retries)  # Exponential backoff
