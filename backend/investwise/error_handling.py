import logging
from django.http import JsonResponse
from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from requests.exceptions import RequestException

# Initialize logger
logger = logging.getLogger(__name__)


# ===========================
# 1. Custom API Exceptions
# ===========================

class DataProcessingError(APIException):
    """
    Exception raised for errors during financial data processing.
    """
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred while processing financial data."
    default_code = "data_processing_error"


class ModelLoadingError(APIException):
    """
    Exception raised when the AI model fails to load.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "The AI model could not be loaded. Please try again later."
    default_code = "model_loading_error"


class ExternalAPIError(APIException):
    """
    Exception raised when an external API call fails.
    """
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "An external service is unavailable. Please try again later."
    default_code = "external_api_error"


# ===========================
# 2. Custom DRF Exception Handler
# ===========================

def custom_exception_handler(exc, context):
    """
    Custom exception handler to standardize API error responses.
    Handles Django REST Framework exceptions, database errors, and custom exceptions.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)

    # Handle uncaught exceptions (e.g., database failures, external API errors)
    if response is None:
        # Log unexpected exceptions
        logger.error(f"Unhandled exception: {exc}", exc_info=True)

        # Return a generic 500 error for unhandled exceptions
        return JsonResponse(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred. Please contact support.",
                    "timestamp": timezone.now().isoformat(),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Customize the response format for DRF exceptions
    error_data = {
        "error": {
            "code": getattr(exc, "default_code", "unknown_error"),
            "message": str(exc),
            "timestamp": timezone.now().isoformat(),
        }
    }

    # Add additional details for validation errors
    if isinstance(exc, ValidationError):
        error_data["error"]["details"] = exc.message_dict

    response.data = error_data
    return response


# ===========================
# 3. Global Error Middleware
# ===========================

class GlobalErrorHandlerMiddleware:
    """
    Middleware to catch and handle exceptions globally across all views.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """
        Handle exceptions and return a standardized JSON response.
        """
        # Log the exception
        logger.error(f"Exception occurred: {exception}", exc_info=True, extra={
            'request': request,
            'user': request.user,
            'path': request.path,
        })

        # Handle specific exception types
        if isinstance(exception, DatabaseError):
            return JsonResponse(
                {
                    "error": {
                        "code": "database_error",
                        "message": "A database error occurred. Please try again later.",
                        "timestamp": timezone.now().isoformat(),
                    }
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        elif isinstance(exception, RequestException):
            return JsonResponse(
                {
                    "error": {
                        "code": "external_api_error",
                        "message": "An external service is unavailable.",
                        "timestamp": timezone.now().isoformat(),
                    }
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        elif isinstance(exception, APIException):
            # Use the custom DRF exception handler for API exceptions
            return custom_exception_handler(exception, context={
                'view': getattr(exception, 'view', None),
                'request': request,
            })

        # Return a generic 500 error for unhandled exceptions
        return JsonResponse(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred.",
                    "timestamp": timezone.now().isoformat(),
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ===========================
# 4. Error Utilities
# ===========================

def handle_external_api_error(response: requests.Response):
    """
    Utility to handle errors from external API calls.
    """
    if response.status_code >= 400:
        logger.error(f"External API error: {response.status_code} - {response.text}")
        raise ExternalAPIError(detail=f"API call failed with status code {response.status_code}")


def handle_database_error(func):
    """
    Decorator to catch and handle database errors.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DatabaseError as e:
            logger.error(f"Database error: {e}")
            raise DataProcessingError(detail="Database operation failed.")
    return wrapper
