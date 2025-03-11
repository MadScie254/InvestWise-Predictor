import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime

# Initialize logger
logger = logging.getLogger(__name__)

# ===========================
# 1. Request Logging Middleware
# ===========================

class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log incoming requests and outgoing responses.
    Useful for debugging and monitoring application activity.
    """

    def process_request(self, request):
        """
        Log details of the incoming request.
        """
        request.start_time = datetime.now()  # Record start time for response timing
        logger.info(
            f"Request: {request.method} {request.path} | "
            f"User: {request.user if request.user.is_authenticated else 'Anonymous'} | "
            f"IP: {self.get_client_ip(request)}"
        )

    def process_response(self, request, response):
        """
        Log details of the outgoing response.
        """
        duration = (datetime.now() - getattr(request, "start_time", datetime.now())).total_seconds()
        logger.info(
            f"Response: {response.status_code} | "
            f"Duration: {duration:.2f}s | "
            f"Path: {request.path}"
        )
        return response

    @staticmethod
    def get_client_ip(request):
        """
        Extract the client's IP address from the request.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return x_forwarded_for.split(",")[0] if x_forwarded_for else request.META.get("REMOTE_ADDR")


# ===========================
# 2. User Activity Tracking Middleware
# ===========================

class UserActivityTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track user activity (e.g., last active timestamp).
    Updates the user's last_login or last_activity field in the database.
    """

    def process_request(self, request):
        """
        Update the user's last activity timestamp if authenticated.
        """
        if request.user.is_authenticated:
            try:
                # Update the user's last activity timestamp
                user = request.user
                user.last_activity = datetime.now()
                user.save(update_fields=["last_activity"])
            except Exception as e:
                logger.error(f"Failed to update user activity: {e}")


# ===========================
# 3. Security Headers Middleware
# ===========================

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to HTTP responses.
    Protects against common web vulnerabilities like XSS and clickjacking.
    """

    def process_response(self, request, response):
        """
        Add security headers to the response.
        """
        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        return response


# ===========================
# 4. API Throttling Middleware
# ===========================

class APIThrottlingMiddleware(MiddlewareMixin):
    """
    Middleware to throttle API requests based on IP address or user account.
    Prevents abuse and ensures fair usage of resources.
    """

    def process_request(self, request):
        """
        Check if the request exceeds the allowed rate limit.
        """
        if request.path.startswith("/api/"):  # Apply throttling only to API endpoints
            ip_address = self.get_client_ip(request)
            user = request.user if request.user.is_authenticated else None

            # Example: Use Redis to track request counts
            redis_client = settings.REDIS_CLIENT
            key = f"throttle:{user.id if user else ip_address}"
            request_count = redis_client.incr(key)

            if request_count == 1:  # First request, set expiration
                redis_client.expire(key, 60)  # Expire after 60 seconds

            if request_count > settings.API_RATE_LIMIT:
                logger.warning(f"Rate limit exceeded for {ip_address}")
                return JsonResponse(
                    {"error": "Rate limit exceeded. Please try again later."},
                    status=429,
                )


# ===========================
# 5. Maintenance Mode Middleware
# ===========================

class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to enable a maintenance mode for the application.
    Redirects users to a maintenance page when enabled.
    """

    def process_request(self, request):
        """
        Check if maintenance mode is enabled and block access.
        """
        if getattr(settings, "MAINTENANCE_MODE", False):
            if not request.path.startswith("/admin/") and not request.user.is_staff:
                return JsonResponse(
                    {"message": "The application is currently under maintenance. Please try again later."},
                    status=503,
                )


# ===========================
# 6. Error Handling Middleware
# ===========================

class CustomErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle uncaught exceptions globally.
    Returns a standardized JSON response for API errors.
    """

    def process_exception(self, request, exception):
        """
        Handle exceptions and return a standardized JSON response.
        """
        logger.error(f"Unhandled exception: {exception}", exc_info=True)

        # Return a generic 500 error for unhandled exceptions
        return JsonResponse(
            {
                "error": {
                    "code": "internal_server_error",
                    "message": "An unexpected error occurred. Please contact support.",
                    "timestamp": datetime.now().isoformat(),
                }
            },
            status=500,
        )

# ===========================
# 7. Example Usage in Django Settings
#  ===========================
# MIDDLEWARE = [
#    "myapp.middleware.RequestLoggingMiddleware",
#   "myapp.middleware.UserActivityTrackingMiddleware",
#   "myapp.middleware.SecurityHeadersMiddleware",
#  "myapp.middleware.APIThrottlingMiddleware",
# "myapp.middleware.MaintenanceModeMiddleware",
# "myapp.middleware.CustomErrorHandlingMiddleware",
# ]
# 
# API_RATE_LIMIT = 100  # Maximum API requests per minute
# REDIS_CLIENT = redis.StrictRedis(host="localhost", port=6379, db=0)
# MAINTENANCE_MODE = False  # Enable maintenance mode
# 
# # ===========================
# # 8. Example Usage in Application
# # ===========================
#  
# # Example view that triggers an exception
# def error_view(request):
#    raise Exception("This is a test exception")
# 
# # Example view that triggers a rate-limited response
# def rate_limited_view(request):
#   return JsonResponse({"message": "This is a rate-limited response"})
# 
# # Example view that triggers a maintenance mode response
# def maintenance_view(request):
#   return JsonResponse({"message": "This is a maintenance mode response"})
#  
# # Example view that triggers a successful response
# def success_view(request):
#  return JsonResponse({"message": "This is a successful response"})
# 
# # Example URL configuration
# urlpatterns = [
#   path("error/", error_view),
#  path("rate-limited/", rate_limited_view),
# path("maintenance/", maintenance_view),
# path("success/", success_view),
# ]
#     

