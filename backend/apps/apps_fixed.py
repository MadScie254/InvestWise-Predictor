from django.apps import AppConfig
import logging

# Set up logging for this module
logger = logging.getLogger(__name__)


class AppsConfig(AppConfig):
    """
    Custom AppConfig for the 'apps' app.
    Handles initialization, signals, and configuration logic.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps'
    verbose_name = "InvestWise Predictor Apps"

    def ready(self):
        """
        Entry point for initializing the app after it has been loaded.
        Use this method to connect signals, perform checks, and initialize services.
        """
        super().ready()
        
        # Import signals to connect them
        try:
            import apps.signals
        except ImportError:
            pass
        
        logger.info("Apps module initialized successfully.")
