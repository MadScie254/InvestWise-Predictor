from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import logging
import requests
from django.db import connection
from django.core.cache import cache

# Set up logging for this module
logger = logging.getLogger(__name__)


class PredictorConfig(AppConfig):
    """
    Custom AppConfig for the 'predictor' app.
    Handles initialization, signals, and configuration logic.
    """
    name = 'predictor'
    verbose_name = "InvestWise Predictor"

    def ready(self):
        """
        Entry point for initializing the app after it has been loaded.
        Use this method to connect signals, perform checks, and initialize services.
        """
        super().ready()

        # Ensure required settings are configured
        self._validate_settings()

        # Initialize logging for the app
        self._initialize_logging()

        # Load initial data or perform migrations-related tasks
        self._load_initial_data()

        # Connect signals for event-driven functionality
        self._connect_signals()

        # Perform health checks to ensure the app is ready
        self._perform_health_checks()

        logger.info("Predictor app initialized successfully.")

    def _validate_settings(self):
        """
        Validates that all required settings are present in the Django settings file.
        Raises an error if any required setting is missing.
        """
        required_settings = [
            'PREDICTOR_API_KEY',
            'PREDICTOR_DATA_SOURCES',
            'PREDICTOR_MODEL_PATH',
            'PREDICTOR_CACHE_TIMEOUT',
            'HEALTH_CHECK_API_ENDPOINTS',
            'HEALTH_CHECK_DATA_SOURCES',
        ]

        for setting in required_settings:
            if not hasattr(settings, setting):
                raise ImproperlyConfigured(
                    f"The '{setting}' setting must be defined in your settings file."
                )

        logger.info("All required settings validated successfully.")

    def _initialize_logging(self):
        """
        Initializes logging for the predictor app.
        Configures log levels, handlers, and formats specific to this app.
        """
        logging.config.dictConfig({
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'verbose': {
                    'format': '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S',
                },
                'simple': {
                    'format': '%(levelname)s %(message)s',
                },
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose',
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.FileHandler',
                    'filename': 'predictor.log',
                    'formatter': 'verbose',
                },
            },
            'loggers': {
                'predictor': {
                    'handlers': ['console', 'file'],
                    'level': 'DEBUG',
                    'propagate': True,
                },
            },
        })

        logger.info("Logging initialized for the predictor app.")

    def _load_initial_data(self):
        """
        Loads initial data or performs tasks that need to run once after migrations.
        This can include seeding the database, loading machine learning models, etc.
        """
        from .tasks import load_initial_data

        try:
            # Call a Celery task to load initial data asynchronously
            load_initial_data.delay()
            logger.info("Initial data loading process triggered.")
        except Exception as e:
            logger.error(f"Failed to load initial data: {e}")

    def _connect_signals(self):
        """
        Connects signals for event-driven functionality.
        Example: Sending notifications when a new prediction is generated.
        """
        from .signals import send_prediction_notification

        @receiver(post_migrate)
        def create_default_user(sender, **kwargs):
            """
            Creates a default admin user if none exists after migrations.
            """
            from django.contrib.auth.models import User

            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='adminpassword'
                )
                logger.info("Default admin user created.")

        # Connect custom signal for predictions
        from .models import Prediction
        from django.db.models.signals import post_save

        post_save.connect(send_prediction_notification, sender=Prediction)

        logger.info("Signals connected successfully.")

    def _perform_health_checks(self):
        """
        Performs health checks to ensure the app is functioning correctly.
        Includes database connection, API endpoint availability, cache system, and more.
        """
        from django.conf import settings
        import requests

        # 1. Database Health Check
        try:
            # Test database connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                logger.info("Database connection verified successfully.")
        except Exception as e:
            logger.error(f"Database health check failed: {e}")

        # 2. Cache System Health Check
        try:
            # Test cache by setting and retrieving a key
            test_key = "health_check_cache_test"
            test_value = "cache_is_working"
            cache.set(test_key, test_value, timeout=5)
            retrieved_value = cache.get(test_key)

            if retrieved_value == test_value:
                logger.info("Cache system verified successfully.")
            else:
                logger.warning("Cache system is not functioning correctly.")
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")

        # 3. API Endpoint Health Check
        try:
            # Define API endpoints to check
            api_endpoints = getattr(settings, 'HEALTH_CHECK_API_ENDPOINTS', [])
            for endpoint in api_endpoints:
                try:
                    response = requests.get(endpoint, timeout=5)
                    if response.status_code == 200:
                        logger.info(f"API endpoint '{endpoint}' is healthy.")
                    else:
                        logger.warning(f"API endpoint '{endpoint}' returned status code {response.status_code}.")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to connect to API endpoint '{endpoint}': {e}")
        except Exception as e:
            logger.error(f"API health check failed: {e}")

        # 4. External Data Source Health Check
        try:
            # Define external data sources to check (e.g., financial APIs)
            data_sources = getattr(settings, 'HEALTH_CHECK_DATA_SOURCES', [])
            for source in data_sources:
                try:
                    response = requests.get(source['url'], params=source.get('params', {}), timeout=10)
                    if response.status_code == 200:
                        logger.info(f"Data source '{source['url']}' is healthy.")
                    else:
                        logger.warning(f"Data source '{source['url']}' returned status code {response.status_code}.")
                except requests.exceptions.RequestException as e:
                    logger.error(f"Failed to connect to data source '{source['url']}': {e}")
        except Exception as e:
            logger.error(f"External data source health check failed: {e}")

        # 5. Machine Learning Model Health Check
        try:
            # Load and test the AI model
            from .utils import load_model, test_model
            model = load_model(settings.PREDICTOR_MODEL_PATH)
            if model:
                test_result = test_model(model)
                if test_result:
                    logger.info("Machine learning model verified successfully.")
                else:
                    logger.warning("Machine learning model is not functioning correctly.")
            else:
                logger.error("Failed to load the machine learning model.")
        except Exception as e:
            logger.error(f"Machine learning model health check failed: {e}")

        # 6. Background Task Queue Health Check (Celery/Redis)
        try:
            # Test Celery task execution
            from .tasks import test_celery_task
            result = test_celery_task.delay()
            if result.ready() and result.get() == "Celery is working":
                logger.info("Celery task queue verified successfully.")
            else:
                logger.warning("Celery task queue is not functioning correctly.")
        except Exception as e:
            logger.error(f"Celery task queue health check failed: {e}")

        logger.info("All health checks completed.")
