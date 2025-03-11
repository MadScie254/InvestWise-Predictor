import logging
import requests

class ExternalLogHandler(logging.Handler):
    """
    Custom logging handler to send logs to an external service (e.g., Sentry, Logstash).
    """
    def __init__(self, service_url=None):
        super().__init__()
        self.service_url = service_url or "https://example.com/log-service"

    def emit(self, record):
        """
        Send the log record to the external service.
        """
        try:
            log_entry = self.format(record)
            response = requests.post(
                self.service_url,
                json={"message": log_entry},
                timeout=5
            )
            if response.status_code != 200:
                print(f"Failed to send log to external service: {response.text}")
        except Exception as e:
            print(f"Error sending log to external service: {e}")
# ===========================
# 5. External Logging Service (Optional)
# ===========================
#
# if getattr(settings, 'LOGGING_EXTERNAL_SERVICE', False):
#     from .external_logging import ExternalLogHandler
#     external_handler = ExternalLogHandler()
#     external_handler.setLevel(logging.WARNING)  # Log WARNING and above to external service
#     external_handler.setFormatter(formatter)
#     logger.addHandler(external_handler)
#
# return logger
#
# # ===========================
# # 6. Example Usage in Application
# # ===========================
#
# # Initialize the logger
# logger = configure_logging()
#
# # Example logging statements
# if __name__ == "__main__":
#     logger.debug("This is a debug message.")
#     logger.info("This is an info message.")
#     logger.warning("This is a warning message.")
#     logger.error("This is an error message.")
#     logger.critical("This is a critical message.")
# In this example, the `ExternalLogHandler` class is used to send log messages to an external logging service (e.g., Sentry, Logstash). This handler can be added to the logger configuration to forward log messages to the external service.
