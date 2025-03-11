import os
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from django.conf import settings

# ===========================
# 1. Logging Configuration
# ===========================

def configure_logging():
    """
    Configure logging for the InvestWise Predictor application.
    Supports multiple handlers: console, rotating file, and timed rotating file.
    """
    # Define log directory
    log_dir = Path(settings.BASE_DIR) / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)

    # Define log file paths
    general_log_file = log_dir / 'application.log'
    error_log_file = log_dir / 'errors.log'

    # Define log format
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create a logger
    logger = logging.getLogger('investwise')
    logger.setLevel(logging.DEBUG)

    # ===========================
    # 2. Console Handler
    # ===========================

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Log INFO and above to the console
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # ===========================
    # 3. Rotating File Handler
    # ===========================

    # Rotates logs when they reach a certain size
    rotating_file_handler = RotatingFileHandler(
        general_log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5  # Keep up to 5 backup files
    )
    rotating_file_handler.setLevel(logging.DEBUG)  # Log DEBUG and above to the file
    rotating_file_handler.setFormatter(formatter)
    logger.addHandler(rotating_file_handler)

    # ===========================
    # 4. Timed Rotating File Handler
    # ===========================

    # Rotates logs daily
    timed_rotating_file_handler = TimedRotatingFileHandler(
        error_log_file,
        when='midnight',  # Rotate logs at midnight
        interval=1,       # Every day
        backupCount=7     # Keep logs for 7 days
    )
    timed_rotating_file_handler.setLevel(logging.ERROR)  # Log only ERROR and above
    timed_rotating_file_handler.setFormatter(formatter)
    logger.addHandler(timed_rotating_file_handler)

    # ===========================
    # 5. External Logging Service (Optional)
    # ===========================

    if getattr(settings, 'LOGGING_EXTERNAL_SERVICE', False):
        from .external_logging import ExternalLogHandler
        external_handler = ExternalLogHandler()
        external_handler.setLevel(logging.WARNING)  # Log WARNING and above to external service
        external_handler.setFormatter(formatter)
        logger.addHandler(external_handler)

    return logger


# ===========================
# 6. Example Usage in Application
# ===========================

# Initialize the logger
logger = configure_logging()

# Example logging statements
if __name__ == "__main__":
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")
